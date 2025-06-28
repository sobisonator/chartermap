import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

ABOVE_PROJECT_PATH = "../../../" # TODO: Use globals for these
DATA_PATH = "../data/"
MARKUP_TYPES_PATH = DATA_PATH + "/markup_types.csv"

debug = True

def extract_full_text(url):
    # Fetches the charter transcript from the given URL and returns its full text.
    # Tries several common selectors, then falls back to the entire page text.

    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # TODO: Create evals for the various classes of markup https://platform.openai.com/docs/guides/evals
    
    # 1. Find the empty marker div
    marker = soup.find("div", id="x01")
    # 2. Select its very next sibling <div>
    target_div = marker.find_next_sibling("div")
    # 3. Ignore all linkLegend spans which contain markup class titles 
    # (maybe we can do something with this to train more effectively)
    for legend in target_div.select("span.linkLegend"):
        legend.decompose()
    # 4. Extract all of its text
    full_text = target_div.get_text(separator="\n", strip=True)

    return full_text

def main():
    # Input CSV and output JSONL file paths
    input_csv = MARKUP_TYPES_PATH
    output_jsonl = ABOVE_PROJECT_PATH + "training_data.jsonl"

    # Read the pipe-delimited dataset
    df = pd.read_csv(input_csv, sep="|")

    with open(output_jsonl, "w", encoding="utf-8") as out:
        for _, row in df.head(10).iterrows(): # Just do the first 10 for testing
            url = row["Appears_in"]
            try:
                full_text = extract_full_text(url)
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                # Fall back to the example snippet if fetch fails
                full_text = row["Object"]

            # Construct prompt and completion
            prompt = (
                f"<SEARCHTEXT>{full_text}</SEARCHTEXT>\n"
                f"<CLASS>Dating clause</CLASS>\n"
            )
            completion = (
                f"<MATCH>{row["Object"]}</MATCH>\n"
                f"<TYPE>{row["Type"]}</TYPE>"
            )
            # Write JSONL line
            out.write(json.dumps({"messages":
                                  [
                                      {"role": "user",
                                       "content": prompt
                                       },
                                       {"role": "assistant",
                                        "content": completion}
                                  ]
                                  }, 
                                  ensure_ascii=False) + "\n")

    print(f"Generated {output_jsonl} with {len(df)} entries.")

if debug:
    main()