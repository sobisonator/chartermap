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

if True:
    test_csv = ImportedCSV(
        csv_input = TEST_CSV_PATH,
        separator = ";"
        )

    #test_id = test_csv.charter_get_data_by_uid(charter_uid = 10, field = "Charter id")
    #test_gist = test_csv.charter_get_data_by_uid(charter_uid = 10, field = "Date of issue")
    #print(f"Test ID = {test_id} | Test gist = {test_gist}")

    test_lookup = test_csv.charter_lookup(lookup_field = "Charter id", lookup_value = "S 308")
    print(f"Test lookup = {test_lookup}")

if True:
    print("Testing genai")
    test_s1 = """
    + In nomine Domini nostri Iesu Christi. Omnem hominem qui secundum Deum uiuit et remunerari a Deo sperat et optat, oportet ut piis precibus consensum hilariter ex animo prebeat, quoniam certum est tanto facilius ea que ipse a Deo poposcerit consequi posse, quanto et ipse libentius Deo aliquid concesserit. Quocirca ego Æthilberhtus rex Cantie, cum consensu uenerabilis archiepiscopi Agustini ac principum meorum, dabo et concedo Deo in honore sancti Petri aliquam partem terre iuris mei quæ iacet in oriente ciuitatis Dorobernie, ita dumtaxat ut monasterium ibi construatur, et res quæ supra memoraui in potestate abbatis sit, qui ibi fuerit ordinatus. Igitur adiuro et precipio in nomine Domini Dei omnipotentis qui est omnium rerum iudex iustus ut prefata terra subscripta donatione sempiternaliter sit confirmata, ita ut nec mihi nec alicui successorum meorum regum aut principum siue cuiuslibet conditionis dignitatibus et ecclesiasticis gradibus de ea aliquid fraudare liceat. Si quis uero de hac donatione nostra aliquid minuere aut irritum facere temptauerit, sit in presenti separatus a sancta communione corporis et sanguinis Christi, et in die iudicii ob meritum malitie suæ a consortio sanctorum omnium segregatus. Circumcincta est hec terra his terminibus: in oriente ecclesia sancti Martini, in meridie uia oþ Burhgat, in occidente et in aquilone Drutingestræte. Acta in ciuitate Dorouerni anno ab incarnatione Christi .dcv., indictione .vi. + Ego Æthelbertus rex Cancie sana mente integroque consilio donacionem meam signo sancte crucis propria manu roboraui confirmauique. Ego Ægustinus gratia Dei archiepiscopus testis consenciens libenter subscripsi. Eadbald. Hamigils. Augemund referendarius. Hocca. Grafio. Thangil. Pinca. Geddi.
    """
    markup_flagger = MarkupFlagger()
    markup_flagger.flag_markups(
        markup_class = "Dating clause",
        search_text = test_s1
        )