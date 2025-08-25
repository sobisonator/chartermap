from googlesearch import search
import xml.etree.ElementTree as ET

witness_name = "Ealdred"
sawyer_number = "S1507"

results = search(f"site:https://pase.ac.uk/pase/?list=person {witness_name} {sawyer_number}",advanced=True)

class WitnessData():
    def __init__(self, witness_xml):
        witness_tree = ET.parse(witness_xml)
        self.witness_root = witness_tree.getroot()
    
    def create_witness_csv(self, witness_csv_path):
        with open(witness_csv_path, "a") as f:
            for charter in self.witness_root:
                sawyer_id = (charter.attrib["sawyer_id"])
                f.write("Signature;Name;Title;Position;RiskyMatch;SawyerNo\n")
                for witness_match in charter:
                    for field in witness_match:
                        f.write(f"{field.text};")
                    f.write(f"{sawyer_id}\n")

# Testing
if False:
    first_result = next(results)
    print(first_result.url)