from src import *

if True:
    # TODO: Make this a class defined in witness_search
    witness_tree = WitnessData(WITNESS_PROCESSED_XML_PATH)
    witness_tree.create_witness_csv()
    # TODO: Lookup and save the witness ID from PASE