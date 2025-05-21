import re
import pandas as pd

class ImportedCSV():
    def __init__(self,
                 csv_input, # String; FIlepath
                 separator): # String; CSV separator char
        # Ensure input is a CSV
        # TODO
        self.import_charter_csv(csv_input, separator)

    def import_charter_csv(self, csv_input, separator):
        ####################
        ### Clean up CSV ###
        ####################
        """
        1. Get number of columns defined in first line of CSV by counting the number of separators
        """
        with open(csv_input, encoding="utf-8") as f:
            self.all_data = {}
            first_line = f.readline()
            # Find text/separator matches
            pattern = r'\s*([^;]+?)\s*(?=;)'
            columns = re.findall(pattern, first_line)
            self.num_cols = len(columns)
            print(f"Found {self.num_cols} columns in CSV")

            row_index = 0 # Tracks row as it is in the CSV
            row_real_index = 0 # Tracks row as it is in the original data
            all_rows = f.readlines()
            for row in all_rows:
                row = row.split(separator)
                # If there are fewer columns than expected, presume there has been a newline
                # Append the following line onto this one and re-check length
                while len(row) < self.num_cols:
                    row = row + all_rows[row_index+1].split(separator)
                    row_index += 1
                row_data = {}
                row_data["charter_uid"] = row_real_index
                for column in columns:
                    row_data[column] = row[columns.index(column)]
                self.all_data[row_index] = row_data
                row_index += 1
                row_real_index += 1
            print(f"CSV loaded successfully with {row_real_index+1} entries.")
            
    def get_data(self, charter_uid, field):
        return self.all_data[charter_uid][field].replace("<semicolon>",";")

    def charter_lookup(self):
        # Gets charter UIDs based on a matching attribute in a field
        pass
                
        # Import CSV into pandas
        #self.import_csv = pd.read_csv(csv_input)
        #print("Imported CSV ")

###############
### Testing ###
###############
ABOVE_PROJECT_PATH = "../../../" # One folder above project root # TODO: Define global values for this
TEST_CSV_PATH = ABOVE_PROJECT_PATH + "data/test/Anglo-Saxon_Charters_transformed_v2.csv"

test_csv = ImportedCSV(
    csv_input = TEST_CSV_PATH,
    separator = ";"
    )

test_id = test_csv.get_data(charter_uid = 10, field = "Charter id")
test_gist = test_csv.get_data(charter_uid = 10, field = "Gist")

print(f"Test ID = {test_id} | Test gist = {test_gist}")