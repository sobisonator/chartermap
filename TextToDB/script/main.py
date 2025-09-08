from src import *
import pandas as pd

if False:
    def fix_tag_content(xml_text):
        pattern = re.compile(r"<([A-Za-z0-9_]+)>(.*?)</\1>", re.DOTALL)

        def replacer(match):
            tag = match.group(1)
            content = match.group(2).strip()
            fixed_content = content.replace("<","&lt;").replace(">","&gt;")
            return f"<{tag}>{fixed_content}</{tag}>"
        
        return pattern.sub(replacer, xml_text)

    with open(WITNESS_PROCESSED_XML_PATH) as f:
        data = f.readlines()
        with open(f"{WITNESS_PROCESSED_XML_PATH}_fixed", "a") as newfile:
            for line in data:
                fixed_xml = fix_tag_content(line)
                newfile.write(fixed_xml)
        


if True:
    flagger = MarkupFlagger()
    charters_data = pd.read_csv(ALL_CHARTERS_PATH)
    valid_ids = pd.read_csv(MASTER_SHEET_DIPLOMAS_CSV_PATH)["Sawyer number"].tolist()
    flagger.create_witness_xml(charters_data,valid_ids)

if False:
    witness_tree = WitnessData(WITNESS_PROCESSED_XML_PATH)
    witness_tree.create_witness_csv(WITNESS_PROCESSED_CSV_PATH)
    # TODO: Lookup and save the witness ID from PASE