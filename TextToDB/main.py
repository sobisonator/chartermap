import pathlib
from typing import Optional

### BEGIN CHARTERTEXT CLASS DEF ###
### Move this out of the main.py file ###

class CharterText():
    def __init__(self, 
                 text_path: str,
                 title: Optional[str] = None):
        
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
    # 1. There is a "texts" table.
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


SOURCE_TEXT_FOLDER_NAME = "Source texts"
#TODO Add a way to feed the program source texts via an API? Is it worth it, if the submission of new editions will be so irregular?
# Consider this as a question for the SYMPOSIUM
SCRIPT_PATH = pathlib.Path(__file__).parent
SOURCE_TEXT_FOLDER_PATH = pathlib.Path(SCRIPT_PATH / SOURCE_TEXT_FOLDER_NAME)
SOURCE_TEXT_FILES = list(SOURCE_TEXT_FOLDER_PATH.glob("*.txt"))


### BEGIN TESTING SCRIPT - MOVE THIS TO ANOTHER FILE ###

test_file = SOURCE_TEXT_FILES[0]

test_text = CharterText(text_path = test_file)

### END TESTING SCRIPT ###