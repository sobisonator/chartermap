import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import csv

# Uses data from OpenStreetMap via https://osmfoundation.org/
# OpenStreetMap data is available under the Open Database License

INPUT_FILE = "../data/royal_diplomas_geocoding_template.csv"
OUTPUT_FILE = "../data/royal_diplomas_geocoded_full.csv"

# Initialise Nominatim geocoder
geolocator = Nominatim(user_agent="anglo-saxon_diploma_placename_geocoder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
# Comply with usage policy https://operations.osmfoundation.org/policies/nominatim/

# Load CSV
df = pd.read_csv(INPUT_FILE,sep=";")

# Ensure necessary columns exist
for col in ["Latitude (programmatic)", "Longitude (programmatic)", "Certainty", "Sources"]:
    if col not in df.columns:
        df[col] = ""

# Geocode promulgation sites
promulgation_sites = []
for location in df["Donated in royal diploma at (location)"].unique():
    query = f"{location}, United Kingdom"
    try:
        geolocated_location = geocode(query)
        if geolocated_location:
            promulgation_sites.append({"location": location,
                                       "latitude": geolocated_location.latitude, 
                                        "longitude": geolocated_location.longitude})
            print(f"Completed {location}, location is {geolocated_location.latitude}, {geolocated_location.longitude}")
    except Exception as e:
        print(f"No geolocation for {location}")
    time.sleep(1) # Doubly comply with usage policy
    
keys = promulgation_sites[0].keys()
with open("promulgation_sites.csv", "w", newline="") as f:
    w = csv.DictWriter(f, keys)
    w.writeheader()
    w.writerows(promulgation_sites)

# Geocode missing entries
#for index, row in df.iterrows():
#    for location in promulgation_sites:
#        if df.at[index, "Donated in royal diploma at (location)"] == location["location"]:
#            df.at[index, "Prom Lat"] = location["latitude"]
#            df.at[index, "Prom Lon"] = location["longitude"]
