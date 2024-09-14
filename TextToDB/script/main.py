import pathlib
from src import *

SOURCE_TEXT_FOLDER_NAME = "Source texts"
#TODO Add a way to feed the program source texts via an API? Is it worth it, if the submission of new editions will be so irregular?
# Consider this as a question for the SYMPOSIUM
SCRIPT_PATH = pathlib.Path(__file__).parent
SOURCE_TEXT_FOLDER_PATH = pathlib.Path(SCRIPT_PATH / SOURCE_TEXT_FOLDER_NAME)
SOURCE_TEXT_FILES = list(SOURCE_TEXT_FOLDER_PATH.glob("*.txt"))

SCHEMA_PATH = pathlib.Path(SCRIPT_PATH.parent / "db/charterDB.sql")
DATABASE_CFG_PATH = pathlib.Path(SCRIPT_PATH.parent / "db/db_connection.cfg")

DB_PATH = pathlib.Path(SCRIPT_PATH.parent / "db/charterDB.sql")

def setup_database():
    db = DB(schema_path = SCHEMA_PATH,
            cfg_path = DATABASE_CFG_PATH,
            db_path = DB_PATH
            )

    db.create_database()

setup_database()