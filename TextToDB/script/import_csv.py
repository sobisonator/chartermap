import os
import pandas as pd

class ImportedCSV():
    def __init__(self,
                 csv_input):
        self.import_csv = pd.read_csv(csv_input)
        print("Imported CSV ")

###############
### Testing ###
###############
ABOVE_PROJECT_PATH = "../../../" # One folder above project root # TODO: Define global values for this
TEST_CSV_PATH = ABOVE_PROJECT_PATH + "data/test/Anglo-Saxon_Charters_transformed_v2.csv"

test_csv = ImportedCSV(csv_input = TEST_CSV_PATH)