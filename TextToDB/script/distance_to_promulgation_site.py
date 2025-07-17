from geopy import distance
import pandas as pd

GEODATA = "../../qgis/data/All estates main map.csv"

df = pd.read_csv(GEODATA,sep=",")

for index, row in df.iterrows():
    estate_location = (row["Estate Lat"],row["Estate Lon"])
    promulgation_location = (row["Prom Lat"], row["Prom Lon"])
    try:
        promulgation_estate_distance = distance.geodesic(estate_location, promulgation_location).km
        df.at[index, "Distance"] = promulgation_estate_distance
    except Exception as e:
        print(e)

df.to_csv(GEODATA, index=False)