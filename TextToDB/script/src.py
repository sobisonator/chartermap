from chartertext import *
#from db import * # Temporarily disabled to minimise package reqs
from import_csv import *
from markup_llm import * # Temporarily disabled to minimise package reqs
from witness_search import *
import pathlib

# TODO: Move the paths into a config file with guidance

SOURCE_TEXT_FOLDER_NAME = "Source texts"
# TODO: Add a way to feed the program source texts via an API? 
# Is it worth it, if the submission of new editions will be so irregular?
SCRIPT_PATH = pathlib.Path(__file__).parent
SOURCE_TEXT_FOLDER_PATH = pathlib.Path(SCRIPT_PATH / SOURCE_TEXT_FOLDER_NAME)
SOURCE_TEXT_FILES = list(SOURCE_TEXT_FOLDER_PATH.glob("*.txt"))

SCHEMA_PATH = pathlib.Path(SCRIPT_PATH.parent / "db/charterDB.sql")
DATABASE_CFG_PATH = pathlib.Path(SCRIPT_PATH.parent / "db/db_connection.cfg")

DB_PATH = pathlib.Path(SCRIPT_PATH.parent / "db/charterDB.sql")

WITNESS_PROCESSED_XML_PATH = f"{SCRIPT_PATH.parent}/data/classified_witnesses.xml" # TODO: Bodge. Fix
WITNESS_PROCESSED_CSV_PATH = f"{SCRIPT_PATH.parent}/data/classified_witnesses.csv"

MASTER_SHEET_DIPLOMAS_CSV_PATH = f"{SCRIPT_PATH.parent}/data/master_sheet_diplomas.csv"