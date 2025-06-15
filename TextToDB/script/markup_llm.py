from google import genai
from google.genai.types import HttpOptions, CreateTuningJobConfig
import time
import pandas
import json

DEBUG = True

ABOVE_PROJECT_PATH = "../../../" # TODO: Use globals for these
SECRETS_PATH = ABOVE_PROJECT_PATH + "secrets/" 
GEMINI_API_KEY_PATH = SECRETS_PATH + "gemini_api_key.txt" # TODO: Use environment variable in prod
GEMINI_API_KEY = open(GEMINI_API_KEY_PATH).readline()

MARKUP_TYPES_PATH = "../data/markup_types.csv"

# We're going to try using OpenAI's gpt-4.1
# 4.1 is markedly better than nano in picking out whole phrases which match.
# It seems to work much better than Google AI's even without fine tuning
# Using a relatively straightforward system prompt (below)

# o3-mini has up to 2.5 million free tokens per day compared to 4.1's 250,000
# Quality of responses needs some more prompting, it does not pick out the whole sentence UNLESS
# we include in the prompt " MatchString must include the entire relevant sentence of the matching string's context."

SYSTEM_PROMPT = f"""
User message contains two parameters, delimited by XML tags. The paramaters are as follows:
Parameter 1, searchtext: <SEARCHTEXT></SEARCHTEXT>
Parameter 2, examples: <EXAMPLES></EXAMPLES>
<EXAMPLES> contains a compressed utf-8 encoded bytes CSV where rows are delimited by a pipe character `|`
Decompress the CSV
The first row contains the column headers
Every example row contains an Object, Type and Class
System must find the substring within <SEARCHTEXT> which most closely matches the class of text within <EXAMPLES> Object fields. This substring is MatchString. MatchString must include the entire relevant sentence of the matching string's context.
System must find the <EXAMPLES> Type which corresponds to MatchString. This is TypeString
Give a level of certainty that MatchString matches any object in the <EXAMPLES>, HIGH, MEDIUM or LOW. This is TextCertaintyLevel
Give a level of certainty that MatchString corresponds to any subset of <X> objects with a known TypeString. This is TypeCertaintyLevel
System message must follow the following format:
<MATCH>MatchString</MATCH>
<TYPE>TypeString</TYPE>
<TEXT_CERTAINTY>TextCertaintyLevel</TEXT_CERTAINTY>
<TYPE_CERTAINTY>TypeCertaintyLevel</TYPE_CERTAINTY>
"""
# We are going to avoid using <EXAMPLES> though, because this eats up tokens with every message - v inefficient
# We instead fine-tune GPT-4.1-nano with the full example dataset
# https://platform.openai.com/docs/guides/supervised-fine-tuning

LLM_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
LLM_MODEL = "gemma-3-12b-it" # TBD gemini-2.0.flash-lite might be used for finetuning

class MarkupFlagger():
    # Uses Google AI Studio's Gemma 3 12B (free model, text )
    def __init__(self):
        if "gemma" not in LLM_MODEL:
            http_options = HttpOptions(api_version="v1")
        else:
            http_options = None
        self.client = genai.Client(
            api_key = GEMINI_API_KEY,
            http_options = http_options
        )

        markup_types_file = open(MARKUP_TYPES_PATH)
        self.markup_types = pandas.read_csv(markup_types_file, sep="|")

        self.end_prompt = "\\n<end_of_turn>\\n<start_of_turn>model\\n"

        self.generate_training_dataset()
    
    def generate_training_dataset(self):
        # Transform input CSV into a dict with model and user roles
        # see https://platform.openai.com/docs/guides/supervised-fine-tuning
        
        # This function generates a .jsonl file which is uploaded to the OpenAI platform
        # The file is saved in ABOVE_PROJECT_PATH/data/generated_training_datasets
        # Thence it is used to finetune the model
        training_dataset = {
            "messages":
            [
                {
                    "role":"user",
                    "content":"<SEARCHTEXT></SEARCHTEXT>"
                }
            ]
        }
        with open(ABOVE_PROJECT_PATH + "data/generated_training_datasets/markup_training.jsonl", "w") as f:
            json.dump(training_dataset, f)
        

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

    def generate_system_prompt(self, class_example_string):
        # We define a structure to create a "system-prompt" equivalent
        # Following https://ai.google.dev/gemma/docs/core/prompt-structure
        # Gemma is instruction tuned and so accepts a system prompt
        system_prompt = f"""
        <start_of_turn>system
        Find the closest match in <SEARCHTEXT> for <EXAMPLES>
        This is called MatchString
        Give a level of certainty, either HIGH, MEDIUM, or LOW
        This value is called CertaintyLevel
        If certainty is LOW, MatchString = `NO MATCH`
        Model responses must follow the following format:
        <match_string>MatchString</match_string><certainty>CertaintyLevel</certainty>
        
        <EXAMPLES>
        {class_example_string}
        </EXAMPLES>
        <end_of_turn>

        <start_of_turn>user
        """ # Input proceeds here and is capped by end_prompt
        # ^ May be obsolete
        # TODO: Review above in light of using fine tuned model

        return system_prompt

    def get_response(self, model, prompt, class_example_text):
        system_prompt = self.generate_system_prompt(class_example_text)
        compiled_prompt = system_prompt + prompt + self.end_prompt
        response = self.client.models.generate_content(
            model=model,
            contents = compiled_prompt
        )
        return response.text
    
    def flag_markups(self, markup_class, search_text): # TODO: Add charter_id arg (or just use search_text?)
        # Return a list of markups in a given text which match the markup class

        # TODO: Investigate whether it would be useful to associate list items with a % certainty
        # May not be necessary as there will not be many of each type of markup and there will be 
        # human validation
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
        # Send this to GPT-4.1 API
        # Get the position of the <MATCH> text in the original, and apply to it the markup
        # Research TODO: Define a subset of markups to use in the geobureaucracy case study.
        # We don't need to do them all
        if DEBUG:
            with open(ABOVE_PROJECT_PATH+"test_message.txt","w",-1,"utf-8") as f:
                f.write(user_message)
                


# TESTING
if True:
    test = MarkupFlagger()
    test.flag_markups(markup_class="Dating clause",search_text="∂is wæs gedon ymbe [VIIII] hund wintra and hund eahtatig on ˇy [XX] teoˇan geare ˇæs ˇe Osuuold arcebisceop to folgoˇe fengc. [Sanctae Mariae and sanctus Michahel, cum sancto Petro] and allum Godes halgum gemiltsien ˇis haldendum, gief hwa buton gewrihtum hit abrecan wille, hæbbe him wi∂ God gemæne buton he to dædbote gecyrre, Amen. ∂is syndon ˇa londgemæru ˇæra [V] hida into Wæreslæge. ˇæt is, ærest of ˇære stræt ˇe sceot to heortla byrig on ˇa dic. Andlang dices on ˇone mor. Of ˇam more ondlang geardes on ˇæt hlypgeat. Of ˇæm hlypgeate on Elmsetena gemære. Ondlong gemæres on Ombersetena gemære. Ondlong ˇæs gemæres ˇæt on ˇa portstræt. Ondlong stræte on hakedes stub. Of ˇæm stubbe on Cumbrawylle. Of Cumbrawylle on faganstan. Of faganstane on Æˇelno∂es croft. Of ˇæm crofte ondlong ˇæs gemæres eft on ˇa dic. Her is seo hondseten.")
    # test.tune_markup_model()