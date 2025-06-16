from openai import OpenAI
import time
import pandas
import json

DEBUG = True

ABOVE_PROJECT_PATH = "../../../" # TODO: Use globals for these
SECRETS_PATH = ABOVE_PROJECT_PATH + "secrets/" 
OPENAI_API_KEY_PATH = SECRETS_PATH + "openai_api_key.txt" # TODO: Use environment variable in prod
OPENAI_API_KEY = open(OPENAI_API_KEY_PATH).readline()

MARKUP_TYPES_PATH = "../data/markup_types.csv"

# We're going to try using OpenAI's gpt-4.1
# 4.1 is markedly better than nano in picking out whole phrases which match.
# It seems to work much better than Google AI's even without fine tuning
# Using a relatively straightforward system prompt (below)

# o3-mini has up to 2.5 million free tokens per day compared to 4.1's 250,000
# Quality of responses needs some more prompting, it does not pick out the whole sentence UNLESS
# we include in the prompt " MatchString must include the entire relevant sentence of the matching string's context."
# TODO: Alter the system prompt to do the following:
# 1. Return a list of all possible matches
# 2. Return the start and end characters of each match
SYSTEM_PROMPT = f"""
User message contains two parameters, delimited by XML tags. The paramaters are as follows:
Parameter 1, searchtext: <SEARCHTEXT></SEARCHTEXT>
Parameter 2, examples: <EXAMPLES></EXAMPLES>
<EXAMPLES> contains a compressed utf-8 encoded bytes CSV where rows are delimited by a pipe character `|`
Decompress the CSV
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

LLM_MODEL = "o3-mini"

class MarkupFlagger():
    # Uses Google AI Studio's Gemma 3 12B (free model, text )
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

    def get_response(self, message):
        response = self.client.responses.create(
            model = LLM_MODEL,
            input = [
                {
                    "role": "developer",
                    "content": SYSTEM_PROMPT
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

        # TODO: Investigate whether it would be useful to associate list items with a % certainty
        # May not be necessary as there will not be many of each type of markup and there will be 
        # human validation
        # TODO: Return alter the system prompt to return matches as a list
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
<SEARCHTEXT>{search_text}</SEARCHTEXT>
<EXAMPLES>{class_example_nospace}</EXAMPLES>
"""

        # TODO:
        # Send this to GPT-o3-mini API (DONE)
        # Get the position of the <MATCH> text in the original, and apply to it the markup
        # Research TODO: Define a subset of markups to use in the geobureaucracy case study.
        # We don't need to do them all
        response = self.get_response(
            message = user_message
        )
        print(response)
                


# TESTING
if True:
    test = MarkupFlagger()
    test.flag_markups(markup_class="Dating clause",search_text="∂is wæs gedon ymbe [VIIII] hund wintra and hund eahtatig on ˇy [XX] teoˇan geare ˇæs ˇe Osuuold arcebisceop to folgoˇe fengc. [Sanctae Mariae and sanctus Michahel, cum sancto Petro] and allum Godes halgum gemiltsien ˇis haldendum, gief hwa buton gewrihtum hit abrecan wille, hæbbe him wi∂ God gemæne buton he to dædbote gecyrre, Amen. ∂is syndon ˇa londgemæru ˇæra [V] hida into Wæreslæge. ˇæt is, ærest of ˇære stræt ˇe sceot to heortla byrig on ˇa dic. Andlang dices on ˇone mor. Of ˇam more ondlang geardes on ˇæt hlypgeat. Of ˇæm hlypgeate on Elmsetena gemære. Ondlong gemæres on Ombersetena gemære. Ondlong ˇæs gemæres ˇæt on ˇa portstræt. Ondlong stræte on hakedes stub. Of ˇæm stubbe on Cumbrawylle. Of Cumbrawylle on faganstan. Of faganstane on Æˇelno∂es croft. Of ˇæm crofte ondlong ˇæs gemæres eft on ˇa dic. Her is seo hondseten.")
    # test.tune_markup_model()