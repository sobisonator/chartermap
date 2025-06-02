from google import genai
import pandas

ABOVE_PROJECT_PATH = "../../../" # TODO: Use globals for these
SECRETS_PATH = ABOVE_PROJECT_PATH + "secrets/" 
GEMINI_API_KEY_PATH = SECRETS_PATH + "gemini_api_key.txt" # TODO: Use environment variable in prod
GEMINI_API_KEY = open(GEMINI_API_KEY_PATH).readline()

MARKUP_TYPES_PATH = "../data/markup_types.csv"

LLM_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
LLM_MODEL = "gemma-3-12b-it"

# TODO: Finetuning Gemma on cloud GPU https://huggingface.co/blog/gemma-peft

class MarkupFlagger():
    # Uses Google AI Studio's Gemma 3 12B (free model, text )
    def __init__(self):
        self.client = genai.Client(api_key = GEMINI_API_KEY)
        # We define a structure to create a "system-prompt" equivalent
        # Following https://ai.google.dev/gemma/docs/core/prompt-structure
        # Gemma is instruction tuned and so accepts a system prompt
        self.system_prompt = """
        <start_of_turn>system
        Summarise in one sentence the class of text delimited by the string `<EXAMPLE>`
        <end_of_turn>

        <start_of_turn>user
        """ # Input proceeds here and is capped by end_prompt
        self.end_prompt = "\\n<end_of_turn>\\n<start_of_turn>model\\n"

        markup_types_file = open(MARKUP_TYPES_PATH)
        self.markup_types = pandas.read_csv(markup_types_file, sep="|")

    def get_response(self, prompt):
        compiled_prompt = self.system_prompt + prompt + self.end_prompt
        response = self.client.models.generate_content(
            model=LLM_MODEL,
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
            while accumulated_tokens.total_tokens < 8193:
                class_example_list.append(example)
                class_example_string = "<EXAMPLE>".join(class_example_list)
                accumulated_tokens = self.client.models.count_tokens(
                    model = LLM_MODEL,
                    contents = class_example_string
                )
        print(self.get_response(class_example_string))
