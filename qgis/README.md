# Chartermap QGIS project

## Dependencies

### First party

#### Master CSV
The charter geodata is currently stored as a CSV

#### Auxiliary geopackages
The auxiliary geopackages are groups of fields based on filters run on the CSV. This seems an inefficient way to break down the data, so we need to investigate a better approach.

### Third party
Third party data should be stored in `../gis`



## Transformation
OS Terrain 50: Inverse of British National Grid + OSGB to WGS 84 (9)