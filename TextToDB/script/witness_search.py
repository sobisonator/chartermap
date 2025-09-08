from googlesearch import search
import xml.etree.ElementTree as ET
import csv
import re

# TODO: Create a Googlesearch lookup for the names
# results = search(f"site:https://pase.ac.uk/pase/?list=person {witness_name} {sawyer_number}",advanced=True)

class WitnessData():
    def __init__(self, witness_xml_path: str):
        witness_tree = ET.parse(witness_xml_path)
        self.witness_root = witness_tree.getroot()

    def google_search_pase(self, witness_name: str, sawyer_number: str) -> str:
        try:
            results = search(f"site:https://pase.ac.uk/pase/?list=person {witness_name} {sawyer_number}",
                            sleep_interval=1, num_results=1)
            for result in results:
                return result
        except Exception as e:
            print(f"Could not search for PASE ID given name {witness_name} and sawyer number {sawyer_number}: {e}")

    def create_witness_csv(self, witness_csv_path: str):
        with open(witness_csv_path, "w") as f:
            # TODO: Use CSV to handle writing to file
            # writer = csv.writer(f, delimiter=";")
            f.write("Signature;Name;Title;Position;RiskyMatch;SawyerNo;PASE_ID\n")
            for charter in self.witness_root:
                sawyer_id = (charter.attrib["sawyer_id"])
                for witness_match in charter:
                    for field in witness_match:
                        f.write(f"\"{field.text}\";")
                    f.write(f"{sawyer_id};;\n")
    
    def search_csv_for_pase(self, witness_csv_path):
        with open(witness_csv_path, "r") as f:
            pass
            #name = witness_match.find("NAME").text
            #pase_id = self.google_search_pase(name, sawyer_id)
                    

# Testing
if False:
    first_result = next(results)
    print(first_result.url)