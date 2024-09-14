import psycopg2
from typing import Optional

### BEGIN DATABASE DEF ###

class DB():
    def __init__(self,
                 schema_path: str,
                 cfg_path: str,
                 db_path: str,
                 ):
        
        self.schema_path = schema_path

        with open(schema_path) as _f:
            self.schema = _f.read()

        self.connection = psycopg2.connect(
            # TODO: Use cfg file to load this information
            # Should include an example file only
            # Consider how to safely store password info
            database = "charterdb"
        )
        # Set autocommit to True to allow creating DB
        self.connection.autocommit = True

        self.cursor = self.connection.cursor()

        print("Finished initialising database")

    def create_database(self):
        self.cursor.execute(self.schema)
        print("Creating tables from schema " + str(self.schema_path))
    
### END DATABASE DEF ###

### BEGIN CHARTERTEXT CLASS DEF ###
### Move this out of the main.py file ###

class CharterText():
    def __init__(self, 
                 text_path: str,
                 title: Optional[str] = None
                 ):
        
        if not title:
            # Default to filename
            self.title = str(text_path.stem)
        elif isinstance(title, str):
            self.title = title
        else:
            raise TypeError("Title must be a string")

        self.text_data = open(text_path, "rb") # Accept a filepath, and read the bytes

        print("Instantiating text " + self.title)

    # This object needs to be able to access a sqlite database where:
    # 1. There is a "text" table.
    # 2. Every character is stored as a row in the table, with the following columns: UID | TEXT | POS
    # 2a. Text, refers to a title UID - Sawyer number? A question for the SYMPOSIUM
    # 2b. Position, contains a number which records the position of the character in the text, counting from 1 being the first char
    # 2bi. Position should be unique within a text (should it..? What about texts with multiple versions where texts are stored)
    # 2bii. Consider special characters for, e.g., lacunae where space is taken up by non-text and non-spaces, such as the absence of parchment!
    # ... how is that handled in transcriptions? Is an attempt even made at measuring that space or do we ignore it? A question for the SYMPOSIUM
    # 3. There is a "markups" table, UID | CHARS
    # 4. Every markup is stored with a reference to a [list] of the relevant characters by their key value (which is a sequential UID)
    # ... that lets us find which text and, within that text, part of the text to which the markup refers.
    # 4a. The markup's UID is a hex value of some sort to allow for practically infinite markups

    # Consider how editing a text would work.
    # Do we allow it at all, or does a whole new version of the text need to be submitted and marked up separately?
    # A question for the SYMPOSIUM
    # The downside of not allowing editing is that if a change needs to be made, we lose all markups.
    # If we allow editing, we'd need to, when we delete a character, find that character row and delete it
    # ... then shunt all the following characters down in their "position" order
    # If we add a character, we'd need to slot that character in at +1 from the position of the character after which it was added
    # ... then shunt all the following characters up in their "position" value
    # If we do these DB operations live, it could be slow(??). Cache this information somehow, then commit it all at the end when submitting?

### END CHARTERTEXT CLASS DEF ###