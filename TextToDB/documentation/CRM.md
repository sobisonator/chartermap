# CRM
The Conceptual Reference Model (CRM) of CharterDB is based on [CIDOC CRM](https://cidoc-crm.org/) using the extension [CRMTex](https://www.cidoc-crm.org/crmtex/sites/default/files/CRMtex_v2.0_June_2023.pdf). This applies an interdisciplinary approach to the study of the documents in scope so that the output of research is classified in a way that can be interpreted within the wider textual research field, and the methodology itself can be applied more broadly once tested.

CRMTex lends itself to the study of texts as both containers of information and as physical artefacts, distinguishing attributes of the text which it is desirable to be able to map, as from them can be inferred information about the text's production. Features of individual characters, script, etc.

CRMTex classes inherit CIDOC CRM E-classes and are therefore interoperable in less fine-grained systems

This implementation takes a relational database and structures its tables as storing Classes ("E" or "TX" numbers), and Properties ("P" or "TXP" numbers).
- Class tables are lists of objects all sharing a class
- Property tables are lists of relationships between two objects of different classes, all sharing a type of relationship (their "property")
The only exception to this is the characters table, whose column forms_part_of implies a TXP17 relationship to the referenced text

## Shared properties
By the way that markups are linked to the text, it will be possible to identify where markups are linked where they share association with the same characters. The association can be described by a ratio of two percentages, where the percentage overlap of either markup is displayed.

e.g. ++//markup one (//) covers this text// and markup two (++) covers the whole text++

With markup 1 selected and 74 characters in the text (ignoring the markup delineators // and ++) the ratio is 100:43, because markup 1 overlaps 100% with markup 2, and markup 2 overlaps 43% with markup 1.

From this, associations can be drawn. One can ask the questions of selected markups:
- Does the name of king X always appear in a certain script?
- What is the level of association between the Old English language and any given script, or hand?

## General textual properties
Because of the positional metadata available for all characters in texts, markups can also provide implicit information about the position of or amount of text used to contain information. Does the name of King X always appear in the first 100 characters in all charters? Perhaps certain phrases are always above or below a certain length in characters.

## Database tables
Each table is listed by its English name and its CRMTex class in parentheses.
The description lays out the contents of the table rows.
### Characters (TX11 - "Grapheme Occurrence")
All characters across all charters. A grapheme occurrence is the instance of the grapheme (the abstract symbol)  
id: Unique ID
grapheme_unicode: Unicode hex value of the character
forms_part_of: References texts(i): denotes with which text this character is associated
manuscript: References the manuscript in which a document is stored

pos_x: Denotes the horizontal position of the character in the text. In the instance that the grid-position of a character is not preserved by a transcription, then this contains the ordinal position of the character in the text and other values may be null. When importing a text, if no other positional data is provided then this is used as the only position value and characters are printed left-to-right top-to-bottom in whatever text renderer displays this information.
pos_y: Denotes the vertical position of the character in the text
pos_facing: Denotes whether the character is on the charter's recto or verso
folio: Denotes the page of the manuscript on which the character appears

UNIQUE (manuscript, pos_x, pos_y, pos_facing, folio): No two characters can share the same position in a manuscript.
### Markups (TX7 - "written text segment")
Every markup, which links a set of characters to metadata
id: Unique ID
type: What class this markup reference? Tells the system which column to check
creator: ID of the user who created this markup
{Reference columns}: One reference column for each available class, always should be null except for that of the relevant class.

#### Reference columns within markups
##### Has language of (P72)
References languages(id)
##### Has style (TPX12)
References styles(id)
##### Employs script (TPX16)
References scripts(id)
##### People references
Every person reference follows the same structure, with its table implying the type of relationship.
All people are implicitly an instance of E39 "Actor"
References a PASE ID where available
Otherwise, references a person via people(id)
id: Unique ID
pase_id: PASE reference
backup_id: references a person via people(id)
scope: English description of the scope of the classification
###### Was written by (TPX5)
###### Refers to grantor (P23 - "transferred title from")
###### Refers to grantee (P22 - "transferred title to")
###### Refers to former title holder (P23 - "transferred title from")
###### Refers to witness (P11 - "had participant")
A witness' name against a charter does not mean that the charter was actually signed or transferred in the presence of the named person. P11 participation can include a reference to, e.g. a depiction of, the individual without requiring their direct contribution to the production of the object.
All other references also imply a P11 relationship; a bare P11 relationship is reserved only for instances where the individual is recorded as a witness. The individual may be recorded otherwise elswhere in the document, with a different property code.
###### Refers to individual (P67 - "refers to")
Any individual referred to in the charter but not in any way specified otherwise should be recorded in this table. Other information about the individual remains encoded in the prosopography record.
#### Non-boundary location references
Some location references follow the same structure, with their table implying the type of relationship
It may be desirable also to store tables of geometries and their properties
id: Unique ID
name: English name of the location
geometry: GeoJSON object describing the geometry of the location., following the CharterDB convention
scope: English description of the scope of the classification
##### Took place at (P7)
Refers to where the charter was signed, implies a relationship of E8 Acquisition (which is P45 Incorporated in the TX1 Text) Taking place at the given location 
#### Boundary location references (E27- "site")
Boundary location references are different because boundaries are made up of polygons for which each point and vertex must be linked to a markup of the text which constitutes a section of the boundary date.
Altogether the boundary locations of a text constitute its boundaries
##### Boundary loc instruction (E29 - "Design or procedure")
id: Unique ID
next: References boundary_loc_element(id). Denotes the boundary location instruction which follows this one
geometry: GeoJSON object describing the geometry included in the instruction, following the CharterDB convention
### Styles (TX10)
Selected styles which can be attributed to a grapheme.
id: Unique ID
label: The label given to the style
type: References style_types(id). The type of style property.
desc: Short description of the style
### Style_types (no ID)
Different types of styles which can be differentiated
id: Unique ID
Name: The English name given to the type of style
The following style types are available:
- hand: A particular scribe's hand
- script design: e.g. Carolingian minuscule
- ductus: Describes the direction of the script
desc: Short description of the style type
### Texts (TX1)
All texts
ID: Unique ID
Sawyer Number: The Sawyer number of this object (stored as integer, the S is implied)
### Manuscripts (E22)
All manuscripts
ID: Unique ID
#### Text relationships
##### Text creation events (E65)
All creation events which can be attributed to a text
ID: Unique ID
Time-span (E52): Date of creation, to degree of certainty
### Modifications (E11)
Tags which indicate a modification was carried out on the text
id: Unique ID
modified_by: (P31 - "was modified by") refers to a PASE id
modified_by_backup: (P31) reference to people(id)
### Languages (E56)
Latin, English, P-Celtic, Q-Celtic, Norse
This will mostly be Latin and English, but others may be used where place names are not written in their Latin or English equivalents
id: Unique ID
label: The English name given to the language
### Scripts (TX13)
All scripts said to be used in the corpus
id: Unique ID
label: The English name givent to the script
desc: Short plaintext description of the script

### Structured bibliographic references: a nice-to-have
It will be necessary to store references because the system's purpose is NOT to make judgements on the validity of information, but rather to present all information with minimal interpretation.

As a nice to have...
Encourage the structuring of references in a systematic manner for best interoperability.
However, this is not a reference management system, and that's a whole system of its own to design.
### Ref texts unnamed
All references that can be linked to markup either in support or negation of a position. Columns constitute the [ISO 690](https://en.wikipedia.org/wiki/ISO_690).
Because it is difficult to maintain consistency when creating references, all fields will be checked when creating a new reference and the user presented with partial or full matches.
ID: Unique ID
Creator: Creator's(') name(s)
Translator: Translator's name
Editor: Editor's(') name(s)
Edition: Edition version
#### Reference relationships
Stores the relationships between markups and references, either with support or negation, and the specific pages if relevant
id: Unique ID
markup: References markups(ID)
reference: References ref_texts(ID)
pages: Optional free-text describing which pages of the text
Support: Boolean value, if True then this reference is in support of the markup's information, if False then it is in negation.


At time of writing, the CIDOC CRM version accessed is [7.1.3](https://www.cidoc-crm.org/sites/default/files/cidoc_crm_version_7.1.3.pdf) and CRMTex is version 2.0

All markups in CharterDB refer implicitly, by their association with a portion of the text, to instances of CIDOC's [E33 Linguistic Object](https://cidoc-crm.org/Entity/e33-linguistic-object/version-7.1.1)

Creating a markup implictly assigns the E33 instance a [P67 refers to](https://cidoc-crm.org/Property/p67-refers-to/version-6.2.1) property.

Every text is made up of a series of characters, classified as [E90 symbolic objects](https://cidoc-crm.org/Entity/e90-symbolic-object/version-7.1.1]) which are stored as individual objects in the database.

We do not use E62 string because the native format of the charters is not digital, the transcriptions are a matter of convenience.

# Geodata

Geodata in CharterDB consists of [GeoJSON](https://datatracker.ietf.org/doc/html/rfc7946) which follows a convention that is set out below.

## Boundary loc instructions
Boundary loc instructions must be a series of points which are then compiled into a geoJSON LineString or Polygon, according to the recorder's choice.
The boundary loc information is stored in a database table as individual points referring to their original text, and, where relevant, which point follows the given point in the instructions.

When a written instruction describes a line rather than a point, going "along", "by" a feature, the line should be described by a sequence of points which all share a "part of line" property. When editing this line, the user sees the line connected as if it were part of a GeoJSON LineString instead of a sequence of individual x,y points

Each point has the following properties:
- ID: A unique ID
- x_pos: X position of the point
- y_pos: Y position of the point
- Markup: References the markup to which this point belongs, thereby connecting it to the written instruction in the text
- Range of certainty: a measure in metres of the degree of certainty to which the point can be identified. The point itself remains the centre, but a circle can be displayed around the point indicating the range of certanty. Default is 0m (maximum certainty). Where used alongside other databases with their own spatial data, this should act as a suggested extra minimum radius of the search area for "nearby objects". 
- References: A list of bibliographic references supporting or negating the validity of this location
- Part of line: References a line ID, if this is part of a line. Can be left null

The boundary points of a text can be compiled into a single GeoJSON polygon object, at the cost of losing the vertex-specific properties. All properties of the polygon are moved into the "properties" of the new polygon object with the key for each property structured as "`point x`-`point-y`-`property`", accompanied by the property belonging to that point.

## Other location data
Wherever possible, other location data should make reference to external sources.

Where this is not possible, a location should be defined in CharterDB's own records as a GeoJSON object.