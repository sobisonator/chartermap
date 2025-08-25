from src import *

if True:
    witness_tree = WitnessData(WITNESS_PROCESSED_XML_PATH)
    witness_tree.create_witness_csv(WITNESS_PROCESSED_CSV_PATH)
    # TODO: Lookup and save the witness ID from PASE