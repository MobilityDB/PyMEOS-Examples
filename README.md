# PyMEOS Examples


The examples provided are divided in three folders:
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
- [MovingPandas](./MovingPandas):  
  Replicas of [MovingPandas examples](https://github.com/anitagraser/movingpandas-examples) using PyMEOS. (WIP)
- [Portable](./Portable):  
  The portable bare-name dialect — every MobilityDB operator under one
  stable, cross-binding name, type-agnostic across all temporal families.
  - [Portable](./Portable/Portable.ipynb): Calling operators by their
    canonical portable bare name in PyMEOS (`pymeos.portable`).
