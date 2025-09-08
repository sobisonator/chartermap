from src import *
import pandas as pd

if True:
    flagger = MarkupFlagger()
    charters_data = pd.read_csv(ALL_CHARTERS_PATH)
    valid_ids = pd.read_csv(MASTER_SHEET_DIPLOMAS_CSV_PATH)["Sawyer number"].tolist()
    flagger.create_witness_xml(charters_data,valid_ids)

if False:
    witness_tree = WitnessData(WITNESS_PROCESSED_XML_PATH)
    witness_tree.create_witness_csv(WITNESS_PROCESSED_CSV_PATH)
    # TODO: Lookup and save the witness ID from PASE