from google import genai
from google.genai.types import HttpOptions, CreateTuningJobConfig
import time
import pandas
import json

ABOVE_PROJECT_PATH = "../../../" # TODO: Use globals for these
SECRETS_PATH = ABOVE_PROJECT_PATH + "secrets/" 
GEMINI_API_KEY_PATH = SECRETS_PATH + "gemini_api_key.txt" # TODO: Use environment variable in prod
GEMINI_API_KEY = open(GEMINI_API_KEY_PATH).readline()

MARKUP_TYPES_PATH = "../data/markup_types.csv"

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
        # We define a structure to create a "system-prompt" equivalent
        # Following https://ai.google.dev/gemma/docs/core/prompt-structure
        # Gemma is instruction tuned and so accepts a system prompt
        self.system_prompt = """
        <start_of_turn>system
        Summarise in one sentence the class of text delimited by the string `<EXAMPLE>`
        <end_of_turn>

        <start_of_turn>user
        """ # Input proceeds here and is capped by end_prompt
        # ^ May be obsolete
        # TODO: Review above in light of using fine tuned model
        self.end_prompt = "\\n<end_of_turn>\\n<start_of_turn>model\\n"

        markup_types_file = open(MARKUP_TYPES_PATH)
        self.markup_types = pandas.read_csv(markup_types_file, sep="|")

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

    def get_response(self, model, prompt):
        compiled_prompt = self.system_prompt + prompt + self.end_prompt
        response = self.client.models.generate_content(
            model=model,
            contents = compiled_prompt
        )
        return response.text
    
    def flag_markups(self, markup_class): # TODO: Add charter_id arg
        # Return a list of markups in a given text which match the markup class

        # TODO: Investigate whether it would be useful to associate list items with a % certainty
        # May not be necessary as there will not be many of each type of markup and there will be 
        # human validation
        matching_markups = []
        # Send the AI a list of examples objects from the markup_types CSV
        class_example_df = self.markup_types.query(f"Class == '{markup_class}'").get("Object")
        class_example_list = []
        accumulated_tokens = self.client.models.count_tokens(
            model = LLM_MODEL,
            contents = "0"
        )
        for example in class_example_df:
            # https://huggingface.co/google/gemma-3-12b-it
            # Output context limit is 8192 tokens
            # We need to find a way to limit the number of tokens used by examples
            # while leaving space for instructions
            # TODO: Rewrite this function to use the finetuned Chartermap-markup-flagger model
            while accumulated_tokens.total_tokens < 8193:
                class_example_list.append(example)
                class_example_string = "<EXAMPLE>".join(class_example_list)
                accumulated_tokens = self.client.models.count_tokens(
                    model = LLM_MODEL,
                    contents = class_example_string
                )
        print(self.get_response(
            model = LLM_MODEL,
            prompt = class_example_string))

# TESTING
if False:
    test = MarkupFlagger()
    test.generate_training_dataset()
    # test.tune_markup_model()