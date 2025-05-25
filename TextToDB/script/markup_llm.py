from google import genai

ABOVE_PROJECT_PATH = "../../../" # TODO: Use globals for these
SECRETS_PATH = ABOVE_PROJECT_PATH + "secrets/" 
GEMINI_API_KEY_PATH = SECRETS_PATH + "gemini_api_key.txt" # TODO: Use environment variable in prod
GEMINI_API_KEY = open(GEMINI_API_KEY_PATH).readline()

LLM_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

class MarkupFlagger():
    # Uses Google AI Studio's Gemma 3 12B (free model, text )
    def __init__(self):
        self.client = genai.Client(api_key = GEMINI_API_KEY)
        # We define a structure to create a "system-prompt" equivalent
        # Following https://ai.google.dev/gemma/docs/core/prompt-structure
        self.system_prompt = """
        <start_of_turn>system
        Model turn must consist only of the string `|||TEST|||`
        <end_of_turn>

        <start_of_turn>user
        """ # Input proceeds here and is capped by end_prompt
        self.end_prompt = "\\n<end_of_turn>\\n<start_of_turn>model"

    def get_response(self, prompt):
        compiled_prompt = self.system_prompt + prompt + self.end_prompt
        response = self.client.models.generate_content(
            model="gemma-3-12b-it",
            contents = compiled_prompt
        )
        return response.text