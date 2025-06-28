import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

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

# Geocode missing entries
for index, row in df.iterrows():
    if pd.isna(row["Latitude"]) or row["Latitude"] == "":
        query = f"{row['Location']}, {row['Shire']}, United Kingdom"
        try:
            location = geocode(query)
            if location:
                df.at[index, "Latitude"] = location.latitude
                df.at[index, "Longitude"] = location.longitude
                if row["Shire"].lower() in location.address.lower():
                    df.at[index, "Certainty"] = "Shire match"
                else:
                    df.at[index, "Certainty"] = "No shire match"
                df.at[index, "Sources"] = "Nominatim"
            else:
                df.at[index, "Certainty"] = "Not found"
                df.at[index, "Sources"] = "Not found"
        except Exception as e:
            df.at[index, "Certainty"] = "Low"
            df.at[index, "Sources"] = f"Error: {str(e)}"
        time.sleep(1) # Doubly comply with usage policy
        print(f"Completed {row["Location"]}, location is {location.latitude}, {location.longitude}")

# Save output
df.to_csv(OUTPUT_FILE, index=False)
print(f"Saved geocoded data to {OUTPUT_FILE}")
