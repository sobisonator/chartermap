import pathlib

SOURCE_TEXT_PATH = "source texts"
#TODO Add a way to feed the program source texts via an API? Is it worth it, if the submission of new editions will be so irregular?
# Consider this as a question for the symposium
SOURCE_TEXT_FILES = list(pathlib.Path(SOURCE_TEXT_PATH).glob("*.txt"))