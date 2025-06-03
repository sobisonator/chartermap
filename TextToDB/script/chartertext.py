from typing import Optional

class CharterText():
    # Handles interactions with texts
    # Accepts a string, transcribed_text
    # Actions are performed on this object, and committed to the database (TBD) on command
    # This concerns the preparation of texts and is separate to the JS interface for interacting with texts
    # Consider however the risk of duplicating functionality (e.g. add markup) if this exists in two contexts
    def __init__(self, 
                 charter_text: str,
                 ):
        self.charter_text = charter_text

    def add_markup(self):
        # Create a markup in the DB
        query = "INSERT INTO markups" \
        "(markup_class, creator, has_language_of, has_style, employs_script, was_written_by," \
        "grantor, beneficiary, former_title_holder,)"
