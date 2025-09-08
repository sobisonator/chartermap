import requests
from ratelimiter import RateLimiter
import urllib.robotparser
import json
import pandas as pd
import csv

PASE_url = "https://pase.ac.uk/pase/"
PASE_names_search = "search/filters/persons/names/"
PASE_person_list = "list/person/"

user_agent = "anglo_saxon_diploma_project"

rp = urllib.robotparser.RobotFileParser(url=f"https://pase.ac.uk/robots.txt")
rp.read()
crawl_delay = rp.crawl_delay(useragent=f"{user_agent}")
print(crawl_delay)

headers = {
    "User-Agent": f"{user_agent}"
}

@RateLimiter(max_calls=1, period=crawl_delay)
def request(request_type, query, params=None):
    request_method = getattr(requests, request_type)
    response = request_method(query, params)
    return response

def name_and_charter_query(name, sawyer_number):
    return f"""
https://pase.ac.uk/pase/list/person/?searchcriteria=[
{{"dbField":"eventterm_id","dbValue":"312","labelField":"Event","labelValue":"Charter-witnessing"}},
{{"dbField":"personheadname","dbValue":"{name}",
"labelField":"Persons","labelValue":"{name}"}},
{{"dbField":"_searchtext","dbValue":"{sawyer_number}",
"labelField":"Search Text","labelValue":"{sawyer_number}"}}]
"""

# STEP 1:
# Get all the normalised names in the alphabet, save them in local JSON to manipulate them
# and limit calls to PASE
start_letters = ["A","Æ","B","C","D","E","F","G","H","I","J","K","L","M","N","O","Ø","P","Q",
                "R","S","T","U","V","W","X","Y","Z"]

def get_name_list(filepath, output_csv=False):
    """
    Get list of normalised names from PASE
    """
    if True:
        with open(f"{filepath}","w+",encoding="utf-8") as f:
            f.write(
                """
    {
        "data":[
    """
            )
            for letter in start_letters:
                response = request(
                    request_type="get",
                    query=PASE_url+PASE_names_search,
                    params={"startsWith": letter})
                f.write(f"{json.dumps(response.json())},\n")
                print(f"Wrote {response.json()}")
            f.write(
                """
        ]
    }
    """
            )

    # STEP 2:
    # Create a CSV of all the normalised names with 2 columns, ID and Name
    if output_csv:
        create_names_csv_from_json(json_filepath=filepath,csv_filepath=filepath)
        # TODO: Ensure proper file extensions for whatever export type is specified

def create_names_csv_from_json(json_filepath, csv_filepath):
    with open(f"{json_filepath}","r",encoding="utf-8") as json_file:
        with open(f"{csv_filepath}","w+",encoding="utf-8",newline="") as csv_file:
            name_writer = csv.writer(
                csv_file, delimiter=",",quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            df = pd.read_json(json_file.read())
            for record in df["data"]:
                for object_list in record:
                    for object in object_list["objects"]:
                        name_writer.writerow([object["id"],object["name"]])