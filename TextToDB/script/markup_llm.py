from openai import OpenAI
import time
import pandas
from import_csv import *
import json

DEBUG = True

ABOVE_PROJECT_PATH = "../../../" # TODO: Use globals for these
SECRETS_PATH = ABOVE_PROJECT_PATH + "secrets/" 
ALL_CHARTERS_PATH = ABOVE_PROJECT_PATH + "data/test/Anglo-Saxon_Charters_transformed_v2.csv"
OPENAI_API_KEY_PATH = SECRETS_PATH + "openai_api_key.txt" # TODO: Use environment variable in prod
OPENAI_API_KEY = open(OPENAI_API_KEY_PATH).readline()
WITNESS_SAMPLES_PATH = "../data/witness_samples.csv"

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

Input:
<SEARCHTEXT>...</SEARCHTEXT>
<EXAMPLES>...</EXAMPLES>

Rules:
1. Only extract witnesses from the witness list section of <SEARCHTEXT>.
   - The witness list always follows a formula such as "hiis testibus", "testibus consentientibus", "quorum nomina infra", or similar.
   - Stop the witness list when land boundaries, property descriptions, or closing narrative resumes.
   - Ignore dispositive clauses (gifts, grants, confirmations) and ignore land boundary clauses (words like "Ærest", "terminibus", "gemære").
2. Within that section, extract every FullSignature.
3. For each:
   - MatchString = exact text of the signature.
   - NameOnly = the personal name inside (may be new).
   - TypeString = one of the Types listed in <EXAMPLES>. Always choose the closest match. Use "unknown" only if no match is possible.
   - OrderValue = order of appearance starting at 1.
   - RiskyMatch = FALSE if within the witness list, TRUE otherwise.
4. Output format (only this):
<MATCH><FULLSIGNATURE>MatchString</FULLSIGNATRUE><NAME>NameOnly</NAME><TYPE>TypeString</TYPE><ORDER>OrderValue</ORDER><RISKY<RiskyMatch</RISKY></MATCH>
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
        

    def tune_markup_model(self):
        # This function may be redundant if the model is tuned via the Google GenAI dashboard
        # https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini-use-supervised-tuning#google-gen-ai-sdk
        tuning_job = self.client.tunings.tune(
            base_model = "gemini-2.0-flash-lite-001",
            training_dataset = self.training_dataset_json,
            config = CreateTuningJobConfig(
                tuned_model_display_name = "Charter markup identifier test"
            )
        )
        running_states = set([
            "JOB_STATE_PENDING",
            "JOB_STATE_RUNNING"
        ])
        while tuning_job.state in running_states:
            print(tuning_job.state)
            tuning_job = self.client.tunings.get(name=tuning_job.name)
            time.sleep(60)
        print(tuning_job.tuned_model.model)
        print(tuning_job.tuned_model.endpoint)
        print(tuning_job.experiment)
        # Test tuned model
        response = self.get_response(
            model = tuning_job.tuned_model.endpoint,
            prompt = "anno secundo regni nostri, indictione secunda, sub die kalendarum Martis"
        )
        print(response)

        if tuning_job.tuned_model.checkpoints:
            for i, checkpoint in enumerate(tuning_job.tuned_model.checkpoints):
                print(f"Checkpoints {i+1}: {checkpoint}")

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
    
    def classify_witnesses(self, search_text): # TODO: Get search_text from charter_id
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
        print(response)
        return(response)

                


# TESTING
if True:
    flagger = MarkupFlagger()
    charters = ImportedCSV(ALL_CHARTERS_PATH, ";")
    i = 1
    for charter in charters.list_all():
        if charter["Year of issue (numerical)"].isnumeric():
            if int(charter["Year of issue (numerical)"]) > 870 and i < 2:
                sawyer_number=charter["Charter id"]
                print("Looking up " + sawyer_number)
                # Get two fields from charter DF: SNumber and Text
                witnesses = flagger.classify_witnesses(search_text=charter["Original text"])
                # TODO: Associate the Sawyer Number with each set of matches per charter
                # TODO: Lookup and save the witness ID from PASE
                i += 1
        # test.tune_markup_model()