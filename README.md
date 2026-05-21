# PyMEOS Examples


The examples provided are divided in two folders:
- [PyMEOS Examples](./PyMEOS_Examples)  
  Replicas of [Tutorial Programs of MEOS](https://www.libmeos.org/tutorialprograms/) using PyMEOS.
  - [AIS](./PyMEOS_Examples/AIS.ipynb): Contains the PyMEOS examples using AIS data 
    - [Reading from File](https://libmeos.org/tutorialprograms/meos_read_ais/)
    - [Assembling Trips](https://libmeos.org/tutorialprograms/meos_assemble_ais/)
    - [Storing in MobilityDB](https://libmeos.org/tutorialprograms/meos_store_ais/)
  - [BerlinMOD](./PyMEOS_Examples/BerlinMOD.ipynb): Contains the PyMEOS examples using BerlinMOD data
    - [Disassembling Trips](https://libmeos.org/tutorialprograms/meos_disassemble_berlinmod/)
    - [Clipping Trips to Geometries](https://libmeos.org/tutorialprograms/meos_clip_berlinmod/)
    - [Tiling Trips](https://libmeos.org/tutorialprograms/meos_tile_berlinmod/)
    - [Simplifying Trips](https://libmeos.org/tutorialprograms/meos_simplify_berlinmod/)
    - [Temporal Aggregation of Trips](https://libmeos.org/tutorialprograms/meos_aggregate_berlinmod/)
  - [Polars × TemporalParquet](./PyMEOS_Examples/Polars_TemporalParquet.py): zero-copy
    round-trip between PyMEOS' `pymeos.io` data-lake layer and the
    [Polars](https://pola.rs/) DataFrame engine. Writes a temporal-point
    dataset to TemporalParquet (opaque MEOS-WKB payload + native-scalar
    sidecar columns + self-describing `temporal` footer), reads it back
    both with PyMEOS (full object reconstruction) and with Polars (via
    `pl.from_arrow`, native primitives + sidecar-driven row-group
    pruning). Depends on the `pymeos.io` module shipping in
    [PyMEOS PR #84](https://github.com/MobilityDB/PyMEOS/pull/84) —
    until that merges, install with
    `pip install "git+https://github.com/MobilityDB/PyMEOS.git@feat/datalake-consumer#egg=pymeos[parquet]"`.
- [MovingPandas](./MovingPandas):  
  Replicas of [MovingPandas examples](https://github.com/anitagraser/movingpandas-examples) using PyMEOS. (WIP)
