import pathlib
from src import *

SOURCE_TEXT_FOLDER_NAME = "Source texts"
#TODO Add a way to feed the program source texts via an API? Is it worth it, if the submission of new editions will be so irregular?
SCRIPT_PATH = pathlib.Path(__file__).parent
SOURCE_TEXT_FOLDER_PATH = pathlib.Path(SCRIPT_PATH / SOURCE_TEXT_FOLDER_NAME)
SOURCE_TEXT_FILES = list(SOURCE_TEXT_FOLDER_PATH.glob("*.txt"))

SCHEMA_PATH = pathlib.Path(SCRIPT_PATH.parent / "db/charterDB.sql")
DATABASE_CFG_PATH = pathlib.Path(SCRIPT_PATH.parent / "db/db_connection.cfg")

DB_PATH = pathlib.Path(SCRIPT_PATH.parent / "db/charterDB.sql")

def setup_database():
    # This should only be called at first-time installation of the database.
    db = DB(schema_path = SCHEMA_PATH,
            cfg_path = DATABASE_CFG_PATH,
            db_path = DB_PATH
            )
    db.clear_database() # Scrap everything in the schema
    db.create_database() # Re-make it

######################
### Database setup ###
######################
# reset_database = input("Clear and remove database? Type y to clear or any other input to proceed: ")
# if reset_database.lower() == "y":
#    setup_database()


###############
### Testing ###
###############
ABOVE_PROJECT_PATH = "../../../" # One folder above project root # TODO: Define global values for this
TEST_CSV_PATH = ABOVE_PROJECT_PATH + "data/test/Anglo-Saxon_Charters_transformed_v2.csv"

if False:

    test_csv = ImportedCSV(
        csv_input = TEST_CSV_PATH,
        separator = ";"
        )

    test_id = test_csv.charter_get_data_by_uid(charter_uid = 10, field = "Charter id")
    test_gist = test_csv.charter_get_data_by_uid(charter_uid = 10, field = "Date of issue")
    print(f"Test ID = {test_id} | Test gist = {test_gist}")

    #test_lookup = test_csv.charter_lookup(lookup_field = "Charter id", lookup_value = "S 308")
    #print(f"Test lookup = {test_lookup}")

if True:
    markup_flagger = MarkupFlagger()
    print("Testing genai")
    print(markup_flagger.get_response("Say hello and tell me about yourself"))