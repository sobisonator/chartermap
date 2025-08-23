from src import *

if True:
    # TODO: Make this a class defined in witness_search
    witness_tree = ET.parse(WITNESS_PROCESSED_XML_PATH)
    witness_root = witness_tree.getroot()
    for charter in witness_root:
        print(charter.tag, charter.attrib)
        for witness_match in charter:
            for element in witness_match:
                print(element.tag, element.text)
                # TODO: Save each witness_match into a CSV for alignment with the master spreadsheet

    # TODO: Lookup and save the witness ID from PASE