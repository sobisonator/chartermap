from openai import OpenAI
import pandas
from import_csv import *

DEBUG = True
SECRETS_PATH = "../../../secrets/" 
OPENAI_API_KEY_PATH = SECRETS_PATH + "openai_api_key.txt" # TODO: Use environment variable in prod
OPENAI_API_KEY = open(OPENAI_API_KEY_PATH).readline()
WITNESS_SAMPLES_PATH = "../data/witness_samples.csv"
WITNESS_PROCESSED_XML_PATH = "../data/classified_witnesses.xml"
MARKUP_TYPES_PATH = "../data/markup_types.csv"

# OpenAI's o3-mini is the minimum suitable model for this task
# It performs consistently with the system prompt in the playground
# 4.1 has a smaller token limit (10% of oe-mini) but if we finetune it, we can come in well under 10%
# As one-shot prompting can require enormous datasets.
# There is a hard-to-measure difference in cost between finetuning and one-shot prompting
# Finetuning has a higher one-off cost
# One-shot prompting can end up being more costly over time, but it might be suitable for markups with small
# ...datasets

# o3-mini has up to 2.5 million free tokens per day compared to 4.1's 250,000
# Quality of responses needs some more prompting, it does not pick out the whole sentence UNLESS
# we include in the prompt " MatchString must include the entire relevant sentence of the matching string's context."
# TODO: Alter the system prompt to do the following:
# 1. Return a list of all possible matches
# 2. Return the start and end characters of each match
SYSTEM_PROMPT_MARKUPS = f"""
User message contains two parameters, delimited by XML tags. The parameters are as follows:
Parameter 1, searchtext: <SEARCHTEXT></SEARCHTEXT>
Parameter 2, examples: <EXAMPLES></EXAMPLES>
<EXAMPLES> contains a CSV where rows are delimited by a pipe character `|`
The first row contains the column headers
Every example row contains an Object, Type and Class
System must find the substring within <SEARCHTEXT> which most closely matches the class of text within <EXAMPLES> Object fields. This substring is MatchString.
MatchString must include the entire context of the relevant string, which may be a phrase or sentence before or after the exact match.
System must find the <EXAMPLES> Type which corresponds to MatchString. This is TypeString
Give a level of certainty that MatchString matches any object in the <EXAMPLES>, HIGH, MEDIUM or LOW. This is TextCertaintyLevel
Give a level of certainty that MatchString corresponds to any subset of <X> objects with a known TypeString. This is TypeCertaintyLevel
System message must follow the following format:
<MATCH>MatchString</MATCH>
<TYPE>TypeString</TYPE>
<TEXT_CERTAINTY>TextCertaintyLevel</TEXT_CERTAINTY>
<TYPE_CERTAINTY>TypeCertaintyLevel</TYPE_CERTAINTY>
"""
# We may avoid using <EXAMPLES> though, because this eats up tokens with every message - v inefficient
# An alternative could be to finetune GPT-4.1 with the full example dataset
# https://platform.openai.com/docs/guides/supervised-fine-tuning
# Doing this will require creating a list of user prompts with the full text, the class, and the assistant response with just the desired text
# o3-mini cannot be finetuned using the OpenAI API
# Ultimately it's a question therefore of what is cheaper, finetuning 4.1 or ad-hoc tuning o3

# TODO: Change this to return a CSV with the S number at the end of each ro
SYSTEM_PROMPT_WITNESSES = f"""
You are an information extraction system. 
Your only task is to extract witness signatures from Anglo-Saxon charters.

Input:
<EXAMPLES> ... annotated examples ... </EXAMPLES>
<SEARCHTEXT> ... charter text ... </SEARCHTEXT>

The <EXAMPLES> block is always provided in the user message. 
It shows correct extractions and mappings for reference. 
Use the rules below to guide your output, and use the examples only as illustration.

Output format:
For each valid witness, output ONLY the following XML structure:
<MATCH>
  <FULLSIGNATURE>...</FULLSIGNATURE>
  <NAME>...</NAME>
  <TYPE>...</TYPE>
  <ORDER>...</ORDER>
  <RISKY>...</RISKY>
</MATCH>

Rules (STRICT):

1. Witness list boundaries
   - The witness list begins after one of these signals:
     "hiis testibus", "testibus consentientibus", "quorum nomina infra",
     OR when a series of clauses begins with "+ Ego", "+ Name", "+ Signum".
   - Stop extraction immediately at the first sign of boundaries or narrative:
     keywords = terminibus, gemære/gemaere, circumcincta, gebohte/gebōhte,
     ærest/Ærest, Ferst, endelang/endelang(e), "from", "unto", "into", "eastwards".
   - Never include land boundaries, purchases, measurements, or descriptive narrative.

2. Witness extraction
   - Extract every full witness line inside the list.
   - <FULLSIGNATURE> = the exact text of the witness line, truncated before any boundary keywords.
   - <NAME> = only the personal name (strip out "ego", "signum", "crucis", verbs, or other tokens).
   - Do not output non-names, partial words, or tokens such as "signum", "crucis", or "me".

3. Type classification
   - Use ONLY these ontology values: Sovereign, Archbishop, Bishop, Abbot, Comes, Dux, Minister,
     Priest, Queen, Aetheling, Miles, Staller.
   - Map Latin words to ontology values:
       rex → Sovereign
       regina → Queen (includes queen mothers)
       filius regis / king’s brother → Aetheling
       episcopus → Bishop
       archiepiscopus → Archbishop
       abbas/abbot → Abbot
       comes → Comes
       dux → Dux
       minister → Minister
       sacerdos/presbyter → Priest
       miles → Miles
       staller → Staller
   - ONLY if no mapping is possible, set <TYPE> to unknown. If there is no title and only a Name present in the FullSignature, DO NOT USE unknown. Unknown must only be used if there is a title which cannot be mapped.
   - Never output raw Latin as <TYPE>.

4. Order and Risky
   - <ORDER> starts at 1 for the first valid witness in each charter and increments sequentially.
   - <RISKY> = FALSE for witnesses clearly inside the witness list.
   - <RISKY> = TRUE only if the entry is uncertain or outside the witness list.

5. Output constraints
   - Use EXACT tag names: MATCH, FULLSIGNATURE, NAME, TYPE, ORDER, RISKY.
   - Do not invent or misspell tags.
   - Do not output anything except <MATCH> blocks.

"""

LLM_MODEL = "o3-mini"

# TODO: Move WITNESS_SAMPLES out of here into a separate CSV file
WITNESS_SAMPLES = open(WITNESS_SAMPLES_PATH, "r")

class MarkupFlagger():
    def __init__(self):
        self.client = OpenAI(
            api_key = OPENAI_API_KEY
        )

        markup_types_file = open(MARKUP_TYPES_PATH)
        self.markup_types = pandas.read_csv(markup_types_file, sep="|")
        
    def get_response(self, message, system_prompt):
        response = self.client.responses.create(
            model = LLM_MODEL,
            input = [
                {
                    "role": "developer",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )
        return response.output_text
    
    def flag_markups(self, markup_class, search_text): # TODO: Add charter_id arg (or just use search_text?)
        # Return a list of markups in a given text which match the markup class

        # We need to record the column position of the witnesses.

        # TODO: Investigate whether it would be useful to associate list items with a % certainty
        # May not be necessary as there will not be many of each type of markup and there will be 
        # human validation
        # TODO: Alter the system prompt to return matches as a list
        matching_markups = []
        # Send the AI a list of examples objects from the markup_types CSV
        class_example_df = self.markup_types.query(f"Class == '{markup_class}'").get(["Object","Type"])

        # It takes up fewer tokens to submit example text as a CSV than as XML
        class_example_string = class_example_df.to_csv(
            path_or_buf = None, # return as string
            sep = "|",
            header = True,
            index = False,
            encoding=""
            )
        # Remove spaces to reduce token usage
        # 26.1kt
        class_example_nospace = class_example_string.replace(" ","")

        user_message = f"""
<EXAMPLES>{class_example_nospace}</EXAMPLES>
<SEARCHTEXT>{search_text}</SEARCHTEXT>
"""
        # Get the position of the <MATCH> text in the original, and apply to it the markup
        # Research TODO: Define a subset of markups to use in the geobureaucracy case study.
        # We don't need to do them all
        response = self.get_response(
            message = user_message,
            system_prompt = SYSTEM_PROMPT_MARKUPS
        )
        print(response)
        return(response)
    
    def classify_witnesses(self, search_text):
        witness_example_data = WITNESS_SAMPLES.read()

        user_message = f"""
<EXAMPLES>{witness_example_data}</EXAMPLES>
<SEARCHTEXT>{search_text}</SEARCHTEXT>
"""
        # TODO: Account for use of backslash in transcriptions, which can be misinterpreted as an escape character
        response = self.get_response(
            message = user_message,
            system_prompt = SYSTEM_PROMPT_WITNESSES
        )
        return(response)
    
    def validate_witness_xml(self, witness_xml):
        pass
        # TODO: Add the XML validation logic into this and return the string if valid, else keep retrying

    def create_witness_xml(self, charters: pandas.DataFrame, valid_ids):
        valid_xml_format = re.compile(r"<MATCH>.*?<FULLSIGNATURE>.*?</FULLSIGNATURE>.*?<NAME>.*?</NAME>.*?<TYPE>.*?</TYPE>.*?<ORDER>.*?</ORDER>.*?<RISKY>.*?</RISKY>.*?</MATCH>", re.DOTALL)
        max_attempts = 3
        with open(WITNESS_PROCESSED_XML_PATH, "a", encoding="utf-8") as f:
            #f.write("<data>")
            for index, charter in charters.iterrows():
                attempts = 0 # Counts number of attempts with the LLM API to limit overusage if it is acting up
                valid_xml_returned = False
                sawyer_number=charter["Charter id"]
                if sawyer_number in valid_ids and int(charter["Sawyer no. (numeral)"]) > 917:
                    print(f"Looking up {sawyer_number}")
                    if not pandas.isnull(charter["Original text"]):
                        # TODO: Make the XML CRMTex compliant
                        while not valid_xml_returned and attempts < 3:
                            attempts += 1
                            witnesses_raw_xml = f'<charter sawyer_id="{sawyer_number}">\n {self.classify_witnesses(search_text=charter["Original text"])}\n</charter>'
                            print(witnesses_raw_xml)
                            if re.search(valid_xml_format, witnesses_raw_xml):
                                f.write(witnesses_raw_xml)
                                valid_xml_returned = True
                                print(f"Successfully wrote XML for {sawyer_number}")
                            else:
                                print(f"Warning: Invalid XML returned for {sawyer_number}, retrying classification. Attempt {attempts} out of {max_attempts}")
                    else:
                        print(f"Warning: Skipping {sawyer_number}: text is null")
            f.write("</data>")