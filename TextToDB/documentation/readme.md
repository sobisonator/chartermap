## Instructions for populating the database

### General rules
All relationships in reference fields must refer only to the UID of the referenced object. No other values can be used.

### Class-specific rules

#### Character
- Symbol: values must be the byte value of the character in unicode
- Every character must be linked to a text which exists in the texts table by referencing the UID integer of the character's text.