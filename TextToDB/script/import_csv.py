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
                    row_data[column] = row[columns.index(column)].replace("<semicolon>",";") # Semicolon hidden for CSV parsing is restored in dict
                self.all_data[row_real_index] = row_data
                row_index += 1
                row_real_index += 1
            print(f"CSV loaded successfully with {row_real_index+1} entries.")           
            
    def charter_get_data_by_uid(self, charter_uid, field):
        return self.all_data[charter_uid][field]

    def charter_lookup(self, lookup_field, lookup_value):
        # Gets charter UIDs based on a matching attribute in a field        
        matches = []
        for row in self.all_data.values():
            if row[lookup_field] == lookup_value:
                matches.append(row)
        return matches

###############
### Testing ###
###############
ABOVE_PROJECT_PATH = "../../../" # One folder above project root # TODO: Define global values for this
TEST_CSV_PATH = ABOVE_PROJECT_PATH + "data/test/Anglo-Saxon_Charters_transformed_v2.csv"

test_csv = ImportedCSV(
    csv_input = TEST_CSV_PATH,
    separator = ";"
    )

#test_id = test_csv.charter_get_data_by_uid(charter_uid = 10, field = "Charter id")
#test_gist = test_csv.charter_get_data_by_uid(charter_uid = 10, field = "Gist")
#print(f"Test ID = {test_id} | Test gist = {test_gist}")

test_lookup = test_csv.charter_lookup(lookup_field = "Charter id", lookup_value = "S 308")
print(f"Test lookup = {test_lookup}")