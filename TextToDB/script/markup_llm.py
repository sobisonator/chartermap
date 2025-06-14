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

# We're going to try using OpenAI's gpt-4.1-nano short context
# It seems to work much better than Google AI's even without fine tuning
# Using a relatively straightforward system prompt:

SYSTEM_PROMPT = f"""
User message contains two parameters, delimited by XML tags. The paramaters are as follows:
Parameter 1, searchtext: <SEARCHTEXT></SEARCHTEXT>
Parameter 2, class_samples: <EXAMPLES></EXAMPLES>
Each example within <EXAMPLES> is delimited by <X></X>
Within each Example Are sub-tags:
<TE></TE> for the text of the example
<TY></TY> for the type into which its text can be categorised
System must find the substring within <SEARCHTEXT> which most closely matches the class of text within <EXAMPLES> <TE> objects. This substring is MatchString
System must find the type of substring within <EXAMPLES> <TY> objects which corresponds to MatchString. This is TypeString
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
        # see https://cloud.google.com/vertex-ai/generative-ai/docs/models/tune_gemini/text_tune
        # In practice, the LLM should return a classification like this:
        # <type>typename</type><class>classname</class>
        # In future we can train this to use the IDs for the type and class
        # ...but for now we will use names
        
        # This function generates a .jsonl file which is uploaded to Google Cloud storage
        # The file is saved in ABOVE_PROJECT_PATH/data/generated_training_datasets
        # Thence it is used to finetune the model
        training_dataset = {
            "systemInstruction": {
                "role": "system",
                "parts": [
                    {
                        "text": "All model role text must consist only of strings in the following format "
                        "<type>typename</type><class>classname</class>"
                    }
                ]
            },
            "contents": []
        }
        for index, row in self.markup_types.iterrows():
            training_sample = [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": row["Object"], # Input sample
                        }
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        {
                            "text": f"<type>{row["Type"]}</type><class>{row["Class"]}</class>"
                        }
                    ]
                }
            ]
            for message in training_sample:
                training_dataset["contents"].append(message)
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
        class_example_list = []

        for index, row in class_example_df.iterrows():
            class_example_list.append(f"<X><TE>{row["Object"]}</TE><TY>{row["Type"]}</TY></X>")
            class_example_string = "".join(class_example_list)
        
        user_message = f"""
<SEARCHTEXT>{search_text}</SEARCHTEXT>
<EXAMPLES>{class_example_string}</EXAMPLES>
"""

        if DEBUG:
            with open(ABOVE_PROJECT_PATH+"test_message.txt","a") as f:
                f.write(user_message)
                


# TESTING
if True:
    test = MarkupFlagger()
    test.flag_markups(markup_class="Dating clause",search_text="Regnante in perpetuum domino nostro Iesu Christo saluatore . mense Aprilio . sub die iiii . kalendas Maias . indictione vii . ego Æthelberhtus rex filio meo Eadbaldo admonitionem catholice fidei optabilem . Nobis est aptum semper inquirere . qualiter per loca sanctorum pro anime remedio uel stabilitate salutis nostre aliquid de portione terre nostre in subsidiis seruorum dei deuotissimam uoluntatem debeamus offerre . Ideoque tibi Sancte Andrea tueque ecclesiae que est constituta in ciuitate Hrofibreui ubi preesse uidetur Iustus episcopus . trado aliquantulum telluris mei . Hic est terminus mei doni . Fram suðgeate west andlanges wealles oð norðlanan to stræte . 7 swa east fram st\r/æte oð Doddinghyrnan ongean bradgeat . Siquis uero augere uoluerit hanc ipsam donationem; augeat illi dominus dies bonos . Et si presumpserit minuere aut contradicere; in conspectu dei sit damnatus et sanctorum eius hic et in eterna secula . nisi emendauerit ante eius transitum quod inique gessit contra Christianitatem nostram . Hoc cum consilio Laurentii episcopi et omnium principum meorum signo sancte crucis confirmaui . eosque iussi ut mecum idem facerent . Amen .")
    # test.tune_markup_model()