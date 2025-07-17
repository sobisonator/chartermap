# Chartermap QGIS project


## First party dependencies

### Master CSVs
The charter geodata is currently stored as a CSV.

### All estates main map
Estates and promulgation sites are two different tables. Currently they do not have numeric IDs, so the estates use the promulgation site's name as the foreign key. This is probably easier for filtering in GIS software, anyway.

### promulgation_sites
The auxiliary geopackages are groups of fields based on filters run on the CSV. This seems an inefficient way to break down the data, so we need to investigate a better approach.

## Third party dependencies
Third party data should be stored in `../gis`


## Transformation
OS Terrain 50: Inverse of British National Grid + OSGB to WGS 84 (9)