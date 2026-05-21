"""
Polars × PyMEOS TemporalParquet round-trip example.

This script demonstrates the zero-copy bridge between PyMEOS' data-lake
interchange layer (``pymeos.io``) and the `Polars
<https://pola.rs/>`_ DataFrame engine. The round-trip covers:

1. Build a temporal dataset using PyMEOS.
2. Write to a TemporalParquet file via ``pymeos.io.write_temporal``
   (opaque MEOS-WKB payload column + native-scalar sidecar columns +
   self-describing ``temporal`` footer; byte-compatible with files
   written by MobilityDuck's ``temporalFooter()`` consumer recipe).
3. Read back with PyMEOS — full PyMEOS object reconstruction.
4. **Consume the same file in Polars** — zero-copy via
   ``pl.from_arrow(pymeos.io.to_arrow(...))``. Polars sees the sidecar
   columns as native-scalar primitives, so its lazy/predicate-pushdown
   machinery prunes row groups without decoding the MEOS-WKB payload.
5. Predicate pushdown demo — filtering on a sidecar column via
   ``pyarrow.parquet.read_table(filters=[...])`` reads only the
   matching row groups.

The example is deliberately small (3 temporal-point trajectories, a
handful of instants each) so it runs in seconds on a laptop and the
on-disk Parquet is human-inspectable.


Requirements
------------

The ``pymeos.io`` data-lake module ships in `PyMEOS PR #84
<https://github.com/MobilityDB/PyMEOS/pull/84>`_ (open at time of
writing). Until PR #84 reaches PyMEOS master, install PyMEOS from the
branch directly::

    pip install "git+https://github.com/MobilityDB/PyMEOS.git@feat/datalake-consumer#egg=pymeos[parquet]"
    pip install polars pyarrow

After PR #84 merges, the standard install path works::

    pip install "pymeos[parquet]" polars pyarrow

The example uses no other Python dependencies.


Why this matters
----------------

Polars is the natural Python-side analytical engine for TemporalParquet
adopters who don't need MEOS-aware predicates on every column: bbox
pruning (the ``covering.bbox.*`` sidecar fields) works as scalar
column-statistics, so Polars' query optimizer can skip row groups
before any per-row work. PyMEOS object reconstruction is reserved for
the columns the analyst genuinely needs as ``Temporal*`` instances.

The Polars side is **read-only** consumption — writes are owned by
PyMEOS' ``pymeos.io`` (or MobilityDuck's ``temporal_to_parquet`` UDF
in the DuckDB binding). This split keeps the writer authoritative for
the footer schema and the reader engine-agnostic.
"""

from __future__ import annotations

import os
import tempfile

# pyarrow is required by pymeos.io (parquet extra) and shipped with polars
import pyarrow as pa
import pyarrow.parquet as pq

# Polars
import polars as pl

# PyMEOS — temporal point types + data-lake interchange
from pymeos import pymeos_initialize, pymeos_finalize, TGeomPointSeq
from pymeos.io import (
    to_arrow,
    from_arrow,
    write_temporal,
    read_temporal,
    temporal_footer,
)


def build_dataset():
    """Build a tiny temporal-point dataset (3 trips, 4 instants each).

    Each trip is a TGeomPointSeq spanning ~10 minutes. Coordinates are
    arbitrary EPSG:4326 points in a small bounding box near Brussels.
    """
    trips = [
        TGeomPointSeq(string=(
            '[POINT(4.35 50.85)@2026-01-01 09:00:00+00,'
            ' POINT(4.36 50.86)@2026-01-01 09:03:00+00,'
            ' POINT(4.37 50.87)@2026-01-01 09:06:00+00,'
            ' POINT(4.38 50.88)@2026-01-01 09:10:00+00]'
        )),
        TGeomPointSeq(string=(
            '[POINT(4.40 50.80)@2026-01-01 09:00:00+00,'
            ' POINT(4.41 50.81)@2026-01-01 09:03:00+00,'
            ' POINT(4.42 50.82)@2026-01-01 09:06:00+00,'
            ' POINT(4.43 50.83)@2026-01-01 09:10:00+00]'
        )),
        TGeomPointSeq(string=(
            '[POINT(4.50 50.90)@2026-01-01 09:00:00+00,'
            ' POINT(4.51 50.91)@2026-01-01 09:03:00+00,'
            ' POINT(4.52 50.92)@2026-01-01 09:06:00+00,'
            ' POINT(4.53 50.93)@2026-01-01 09:10:00+00]'
        )),
    ]
    return {
        "vehicle_id": [1, 2, 3],
        "trip":       trips,
    }


def demo_roundtrip_via_pymeos(path: str) -> None:
    """Step 2-3: PyMEOS writes, PyMEOS reads, full object reconstruction."""
    print("\n=== PyMEOS write → PyMEOS read (full reconstruction) ===")
    data = build_dataset()
    write_temporal(data, path, temporal_columns=["trip"], sidecars=True)
    print(f"  wrote {path} ({os.path.getsize(path):,} bytes)")

    # Read back — reconstruct=True (default) gives PyMEOS objects
    out = read_temporal(path)
    print(f"  read back {len(out['trip'])} trips, type: {type(out['trip'][0]).__name__}")
    for vid, trip in zip(out["vehicle_id"], out["trip"]):
        print(f"    vehicle {vid}: numInstants={trip.num_instants()}  "
              f"first={trip.start_instant()}  last={trip.end_instant()}")


def demo_roundtrip_via_polars(path: str) -> None:
    """Step 4: Polars consumes the same file zero-copy via pl.from_arrow.

    Polars sees the sidecar columns (xmin/xmax/ymin/ymax/tmin/tmax)
    as native primitives, and the temporal payload as an opaque BINARY
    column. Analysts who don't need MEOS-aware operations work in Polars
    directly with first-class types.
    """
    print("\n=== Polars consumes the SAME file zero-copy ===")
    # Read as Arrow table (preserves the temporal footer + native sidecars)
    arrow_table = pq.read_table(path)
    print(f"  arrow schema: {arrow_table.schema}")
    print(f"  rows: {arrow_table.num_rows}, columns: {arrow_table.num_columns}")

    # Polars zero-copy — Polars accepts pyarrow.Table directly
    df = pl.from_arrow(arrow_table)
    print(f"\n  Polars DataFrame:")
    print(df)

    # Show the temporal footer (the catalog of which columns are MEOS-WKB)
    footer_bytes = arrow_table.schema.metadata.get(b"temporal")
    if footer_bytes:
        print(f"\n  temporal footer (engine-agnostic catalog): {footer_bytes.decode()}")


def demo_predicate_pushdown(path: str) -> None:
    """Step 5: Predicate pushdown on a sidecar column.

    Filtering on ``trip__xmax`` (or any of the sidecar scalar columns)
    via pyarrow's ``filters=`` argument prunes row groups before any
    per-row decode — same recipe MobilityDuck uses on the DuckDB side
    (sidecar columns are by-design row-group-statistics friendly).
    """
    print("\n=== Sidecar-driven predicate pushdown ===")
    # Read only trips whose maximum x-coord is below 4.45 (excludes trip 3)
    filt_table = pq.read_table(path, filters=[("trip__xmax", "<", 4.45)])
    df = pl.from_arrow(filt_table)
    print(f"  filter [trip__xmax < 4.45] → {filt_table.num_rows} rows kept")
    print(df.select(["vehicle_id"]).to_series().to_list())

    # Same filter, but reconstruct PyMEOS objects on the kept rows
    out = read_temporal(path, filters=[("trip__xmax", "<", 4.45)])
    print(f"\n  read_temporal with same filter: {len(out['trip'])} PyMEOS objects reconstructed")


def main():
    pymeos_initialize()
    try:
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "polars_temporalparquet_demo.parquet")
            demo_roundtrip_via_pymeos(path)
            demo_roundtrip_via_polars(path)
            demo_predicate_pushdown(path)
    finally:
        pymeos_finalize()

    print("\n✓ All three demos completed.")


if __name__ == "__main__":
    main()
