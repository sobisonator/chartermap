# Chartermap QGIS project

## Dependencies
Dependency data should be stored in `../gis`

| Title   |  Availability   |
| ------- | --------------- |
| Historic England National Heritage List | https://osdatahub.os.uk/downloads/open/Terrain50 |

## Transformation

## Filters

## Normalising data
The data in CSV format must have one "configuration" per row. That is:
- One promulgation site
- One date
- One charter
- One estate

CSV is not good for one-to-many relationships, especially when playing with QGIS.

A database or JSON structure could potentially manage these one-to-many relationships more effectively, and then transform them into this "flat" "single sheet" format which has one "configuration" per row.

An example of this is S891 with promulgation sites Wantage and Calne