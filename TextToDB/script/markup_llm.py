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

SYSTEM_PROMPT_WITNESSES = f"""
You are an information extraction system.

Input: 
<SEARCHTEXT>...</SEARCHTEXT>
<EXAMPLES>...</EXAMPLES>

Rules:
1. Look only inside substrings matching WitnessList in <EXAMPLES>.
2. Extract every FullSignature within <SEARCHTEXT>.
3. For each:
   - MatchString = exact text of the FullSignature.
   - NameOnly = the personal name within the signature. This may be a new name not present in <EXAMPLES>.
   - TypeString = one of the Types listed in <EXAMPLES>. Always choose the closest match. Use "unknown" only if no match is possible.
   - OrderValue = sequential order starting at 1.
   - RiskyMatch = FALSE if within WitnessList, TRUE otherwise.
4. Output format (no other text):
<MATCH>MatchString;NameOnly;TypeString;OrderValue;RiskyMatch</MATCH>
"""

LLM_MODEL = "o3-mini"

# TODO: Move WITNESS_SAMPLES out of here into a separate CSV file
WITNESS_SAMPLES = f"""
<EXAMPLES>
Text,Class,Type
+ Ego Æ∂elstan rex Anglorum hanc meam donationem cum sigillo sanctæ crucis impressi . + Ego Eadmund indolis clito . consensi . + Ego Wulfhelm archiepiscopus dictavi . + Ego Ælfheah episcopus adquievi . + Ego Æ∂elgar episcopus notavi . + Ego Brihtelm episcopus favi . + Ego Wynsige episcopus conclusi . + Wulfgar dux . + Ælfhere dux . + Æ∂elstan dux . + Odda minister . + Wulfhelm minister . + Ælfheah minister . + Æ∂elfer∂ minister . + Wihtgar minister . ,WitnessList,
+ Ego Æ∂elstan rex Anglorum hanc meam donationem cum sigillo sanctæ crucis impressi .,FullSignature,Sovereign
+ Ego Eadmund indolis clito . consensi,FullSignature,Aetheling
Æ∂elstan,Name,
Eadmund,Name,
+ Ego Wulfhelm archiepiscopus dictavi .,FullSignature,Archbishop
Wulfhelm,Name,
+ Ego Ælfheah episcopus adquievi .,FullSignature,Bishop
Ælfheah,Name,
+ Ego Æ∂elgar episcopus notavi .,FullSignature,Bishop
Æ∂elgar,Name,
+ Ego Brihtelm episcopus favi .,FullSignature,Bishop
Brihtelm,Name,
+ Ego Wynsige episcopus conclusi .,FullSignature,Bishop
Wynsige,Name,
+ Wulfgar dux .,FullSignature,Dux
Wulfgar,Name,
+ Ælfhere dux .,FullSignature,Dux
+ Æ∂elstan dux .,FullSignature,Dux
Ælfhere,Name,
+ Odda minister .,FullSignature,Minister
Odda,Name,
+ Wulfhelm minister .,FullSignature,Minister
+ Ælfheah minister .,FullSignature,Minister
+ Æ∂elfer∂ minister .,FullSignature,Minister
Æ∂elfer∂,Name,
+ Wihtgar minister .,FullSignature,Minister
Wihtgar,Name,
Ælfheah ,Name,
Wulfhelm,Name,
+ Ego Edelred singularis priuilegii ierarchia preditus rex . huius indiculi acumen cum signo sancte crucis sempiterneque uenerande corroboraui et subscripsi + Ego Wulfstan archiepiscopus regie roboram donationis agie triumphale crucis signaculum depinxi + Ego Elfhun Lundonie ciuitatis presul hanc cartulam aliasque duas scilicet at Totanham et at Hatfeld dictitans rege suiusque precipientibus perscribere iussi + Ego Adulf episcopus consensi + Ego Ethelsige episcopus confirmaui + Ego Godwine episcopus adiuui + Ego Elfgar episcopus adquieui + Ego Britwold episcopus + Ego Eadnod episcopus non renui + Ego Elfmer episcopus corroboraui + Ego Eadric dux consensi + Ego Elfric dux consensi + Ego Leofwine dux consensi + Ego Utred dux consensi + Ego Germanus abbas + Ego Leofric abbas + Ego Wulfgar abbas + Ego Elfsige abbas + Ego Britred abbas + Ego Elfric abbas + Ego Elfuere abbas + Ego Brithold abbas + Ego Elfwig abbas + Ego Eadric abbas + Ego Bristan abbas + Ego Ethelmer minister + Ego Elfgar minister + Ego Odda minister + Ego Ethelric minister + Ego Elfgar minister + Ego Godric minister + Ego Ethelwine minister + Ego Ulfcitel minister + Ego S[...]elyred minister + Ego Brisige minister + Ego Wulfric minister,WitnessList,
+ Ego Edelred singularis priuilegii ierarchia preditus rex . huius indiculi acumen cum signo sancte crucis sempiterneque uenerande corroboraui et subscripsi,FullSignature,Sovereign
+ Ego Wulfstan archiepiscopus regie roboram donationis agie triumphale crucis signaculum depinxi +,FullSignature,Archbishop
Edelred,Name,
Wulfstan,Name,
+ Ego Elfhun Lundonie ciuitatis presul hanc cartulam aliasque duas scilicet at Totanham et at Hatfeld dictitans rege suiusque precipientibus perscribere iussi +,FullSignature,Archbishop
Elfhun,Name,
Ego Cuthred comes consensi.,FullSignature,Comes
Cuthred,Name,
Ego Seaftuwine consensi.,FullSignature,Comes
Seaftuwine,Name,
Ego Alricus comes consensi. Ego Eadberhtus comes consensi. Ego Sceafthere comes consensi. Ego Westheah comes consensi. Ego Seaftuwine consensi. Ego Cuthred comes consensi. [.............],WitnessList,
Ego Ceolnodus gracia Dei archiepiscopus ad confirmandam huius testimonium carticulam signum sancte crucis exaravi . + Ego Athelwolf rex ad roborandam haunc meam donacionem almi trophei signaculum impressi . + Cum multis aliis .,WitnessList,
Ego Ceolnodus gracia Dei archiepiscopus ad confirmandam huius testimonium carticulam signum sancte crucis exaravi .,FullSignature,Archbishop
Ceolnodus,Name,
+ Ego Athelwolf rex ad roborandam haunc meam donacionem almi trophei signaculum impressi .,FullSignature,Sovereign
Athelwolf,Name,
+ Ego Æþelfled hanc meam licentiam confirmo signaculo sancte crucis. + Ego Ælfwyn episcopus consensi et subscripsi. + Ego Ælfwine episcopus consensi et subscripsi. + Ego Æþelhun episcopus consensi et subscripsi. + Ego Eadgar consensi et subscripsi. + Ego Ælfred episcopus consensi et subscripsi. + Ego Æþelferd dux consensi et subscripsi. + Ego Ælfred dux consensi et subscripsi. + Ego Æþelhun abbas consensi et subscripsi. + Ego Ecgberht abbas consensi et subscripsi. + Ego Cynað abbas consensi et subscripsi. + Ego Wihtred consensi et subscripsi. + Ego Berhsige consensi et subscripsi. + Ego Æþelnaþ consensi et subscripsi. + Ego Æþelward consensi et subscripsi. + Ego Ælfstan consensi et subscripsi.,WitnessList,
+ Ego Æþelfled hanc meam licentiam confirmo signaculo sancte crucis.,FullSignature,Sovereign
Æþelfled,Name,
+ Ego Ælfwyn episcopus consensi et subscripsi.,FullSignature,Bishop
+ Ego Eadgar consensi et subscripsi.,FullSignature,NoTitle
Eadgar,Name,
+ Ego Æþelhun abbas consensi et subscripsi.,FullSignature,Abbot
Æþelhun,Name,
+ Ego Ecgberht abbas consensi et subscripsi.,FullSignature,Abbot
+ Ego Cynað abbas consensi et subscripsi.,FullSignature,Abbot
+ Ego Wihtred consensi et subscripsi.,FullSignature,NoTitle
+ Ego Berhsige consensi et subscripsi.,FullSignature,NoTitle
+ Ego Æþelnaþ consensi et subscripsi.,FullSignature,NoTitle
+ Ego Æþelward consensi et subscripsi.,FullSignature,NoTitle
+ Ego Ælfstan consensi et subscripsi.,FullSignature,NoTitle
Ego Ælfred gratia Dei Saxonum rex propriæ donationi signum crucis confirmavi . Ego Æˇered archiepiscopus manum adpono . Ego Denewulf episcopus huic donationi consentiens subscribo . Ego Æˇelnod Dux . Ego Wlfred Dux . Ego Orddulf Dux . Ego Bucca Dux . Ego Æ∂elwald Dux . Ego Wullaf Dux . Ego Garulf Dux . Ego Byrhtnod Dux . Ego Osric minister . Ego Eggwulf minister . Ego Æ∂elm minister . Ego Witbrord minister . Ego Deormod minister . Ego Acca minister . Ego Ælfhere minister . Ego Wullaf minister . Ego Babba minister . Ego Ealdwulf minister . Ego Æˇelstan minister Ego Tata minister . Ego Burlaf minister . Ego Æffa minister .,WitnessList,
Ego Ælfred gratia Dei Saxonum rex propriæ donationi signum crucis confirmavi .,FullSignature,Sovereign
Ego Æˇered archiepiscopus manum adpono .,FullSignature,Archbishop
Ego Denewulf episcopus huic donationi consentiens subscribo .,FullSignature,Archbishop
Ego Wlfred Dux .,FullSignature,Dux
Ego Orddulf Dux,FullSignature,Dux
Ego Bucca Dux .,FullSignature,Dux
Ego Æ∂elwald Dux .,FullSignature,Dux
Ego Osric minister .,FullSignature,Minister
Ego Eggwulf minister .,FullSignature,Minister
Eggwulf,Name,
Aelfred rex saxonum. Wulfsige episcopus. Wulred dux. Aeˇelred dux. Eadweard filius regis. Johannes presbyter. Wærulf presbyter. Deormod cellerarius. Aelfric thesaurarius. Sigewulf pincerna. Byrnstan miles. Berchtmund miles. Wulfsige miles. Aeˇelm miles. Ae∂elhelm miles. Owald miles. Vchfer∂ miles. Ocea miles. Byrhthelm miles.,WitnessList,
Aelfred rex saxonum.,FullSignature,Sovereign
Eadweard filius regis.,FullSignature,Aetheling
Johannes presbyter.,FullSignature,Priest
Wærulf presbyter.,FullSignature,Priest
Deormod cellerarius.,FullSignature,Staller
Aelfric thesaurarius.,FullSignature,Staller
Sigewulf pincerna.,FullSignature,Staller
Byrnstan miles.,FullSignature,Miles
Berchtmund miles.,FullSignature,Miles
Wulfsige miles.,FullSignature,Miles
Ae∂elhelm miles.,FullSignature,Miles
Owald miles.,FullSignature,Miles
Vchfer∂ miles.,FullSignature,Miles
Et ego Plegmundus archiepiscopus Dorobernensis consencio æt subscribo . +. Et ego Ethelbaldus archiepiscopus Eboracensis consencio æt subscribo . +. Ego Ethelstanus Herfordensis antistes . consencio et subscribo . +. Ego Werbertus Lagaces[trensis episcopus] consencio æt subscribo . +. Ego Tynebertus Lichefeldensis episcopus consencio æt subscribo . +. Ego Herefredus Wygorniensis Minister consencio æt signum sancte crucis appono . +. Ego Elfstanus Londoniensis episcopus signum crucis appono . +. Ego Denewuolfus Wentanæ urbis episcopus assencio æt conscribo . +. Ego Eylmerus Cicestrensis minister assensum prebeo æt suscribo . +. Ego Eaddredus Norwuycensis minister consencio æt signum crucis appono . +. Ego Haroldus Dorkcestrensis minister consencio æt subscribo . +. Ego Grymbaldus sacerdos ad honorem Dei consencio . æt signum crucis appono . +. Ego Johannes abbas signum crucis appono . +. Ego Eaddredus comes consencio æt subscribo . +. Ego Etheldredus Ganniorum dux subscribo . +. Ego Ælwytha regina . consencio æt subscribo . +. Ego Etheldredus dux Merciorum consencio æt subscribo . +.,WitnessList,
Et ego Plegmundus archiepiscopus Dorobernensis consencio æt subscribo . +,FullSignature,Archbishop
 +. Ego Ethelstanus Herfordensis antistes . consencio et subscribo .,FullSignature,Priest
+. Ego Werbertus Lagaces[trensis episcopus] consencio æt subscribo .,FullSignature,Bishop
+. Ego Tynebertus Lichefeldensis episcopus consencio æt subscribo .,FullSignature,Bishop
+. Ego Grymbaldus sacerdos ad honorem Dei consencio . æt signum crucis appono .,FullSignature,Priest
+. Ego Johannes abbas signum crucis appono .,FullSignature,Abbot
+. Ego Eaddredus comes consencio æt subscribo .,FullSignature,Comes
+. Ego Etheldredus Ganniorum dux subscribo .,FullSignature,Dux
+. Ego Ælwytha regina . consencio æt subscribo .,FullSignature,Queen
+. Ego Etheldredus dux Merciorum consencio æt subscribo .,FullSignature,Dux
Ego Denewulf episcopus .,FullSignature,Bishop
Denewulf,Name,
Ego A∂elweard filius regis . ,FullSignature,Aetheling
A∂elweard,Name,
Ego Asser episcopus .,FullSignature,Bishop
Ego Ælfweard filius regis .,FullSignature,Aetheling
Ego Æˇelweard episcopus consensi et subscripsi .,FullSignature,Bishop
Ego Ceolmund episcopus consensi et subscripsi .,FullSignature,Bishop
Ego Wighelm episcopus consensi et subscripsi .,FullSignature,Bishop
Ego Wulfsige episcopus consensi et subscripsi .,FullSignature,Bishop
Ego Fri∂estan . episcopus cum consilio eiusdem regis hoc roboraui atque conexi cum triumpho regis eterni .,FullSignature,Bishop
Ego Plegmund archiepiscopus mellifluam donationem prefati regis subscribsi cum signaculo sancte crucis .,FullSignature,Archbishop
Ego Eadwardus . Rex hanc restaurationem a me renouatam signum sancte crucis propria manu scribendo firmaui .,FullSignature,Sovereign
Ego Eadwardus . Rex hanc restaurationem a me renouatam signum sancte crucis propria manu scribendo firmaui . Ego Plegmund archiepiscopus mellifluam donationem prefati regis subscribsi cum signaculo sancte crucis . Ego Fri∂estan . episcopus cum consilio eiusdem regis hoc roboraui atque conexi cum triumpho regis eterni . Ego Wulfsige episcopus consensi et subscripsi . Ego Wighelm episcopus consensi et subscripsi . Ego Ceolmund episcopus consensi et subscripsi . Ego Æˇelweard episcopus consensi et subscripsi . Ego Æˇelstan filius regis . Ego Ælfweard filius regis . Ego Osfer∂ dux . Ego Ordlaf dux . Ego Beorhtulf dux . Ego Ordgar dux . Ego Heahferd dux . Ego Werulf presbyter . Ego Æˇelstan presbyter . Ego Beornstan presbyter . Ego Ealhstan presbyter . Ego Deormod minister . Ego Withbrord minister . Ego Odda minister . Ego Ælwold minister . Ego Elred minister . Ego A∂ulf minister . Ego Æˇelfer∂ minister . Ego Wulfhear∂ minister . Ego Ælfric minister . Ego Wulfhelm minister . Ego Uffa minister . Ego Ælfstan minister . Ego Ælfred minister . Ego Ælfstan minister . Ego Wulfhere minister . Ego A∂ulf minister . Ego Wulfhun minister . Ego Wullaf minister . Ego Buga minister . Ego Ælfre∂ minister . Ego Æˇelno∂ minister . Ego Wulfric minister .,WitnessList,
"Adlem archiepiscopus. Alla episcopus. Siglem episcopus. Wlflem episcopus. Wlbred episcopus. Berneth episcopus. Eatolw episcopus. Winsige episcopus. Ordgar princeps. Aelwald princeps, et Odda minister regis, et Cened abbas, et Alfeth sacerdos, et alius Alfeth sacerdos et monachus.",WitnessList,
Adlem archiepiscopus.,FullSignature,Archbishop
Alla episcopus.,FullSignature,Bishop
Siglem episcopus.,FullSignature,Bishop
Ordgar princeps.,FullSignature,Princeps
"Aelwald princeps,",FullSignature,Princeps
Odda minister regis,FullSignature,Minister
Cened abbas,FullSignature,Abbot
Alfeth sacerdos,FullSignature,Priest
+ Feologeld presbyter abbas,FullSignature,Priest
+ Æðelnoð,FullSignature,NoTitle
</EXAMPLES>
"""

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
        witness_example_data = WITNESS_SAMPLES

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
    test = MarkupFlagger()
    test.classify_witnesses(search_text="""+ In nomine Domine Ego Ælfrædus gratia Dei Saxonum rex . meo fideli duce Sigilmo concedo in perpetuam posessionem terram iuris mei uniusque manentis in loco qui dicitur Fearnleag et an myclan wisce vi æceres mæde into ðam lande an norðeweardre wið Eadweald Sibirhtigne pro eius amabilii pecunia ut abeat et possedeat quamdiu uiuat . postque suum ab ac uita decessum liberam abeat potestatem dandi cuicumque placuerit Acta est autem hæc donatio anno ab incarnatione Christi .dcccxcviii. in loco qui dicitur Wulfamere . hiis testibus consentientibus quorum nomina infra karaxata esse fidentur. + Ego Ælfred rex Saxonum hanc meum donationem signo sancte crucis confirmo + Eadweard rex . hanc regis donationem stabilito. + Ordlaf dux. + Sigulf dux. + Wullaf dux. + Beorhtsige minister + Osferð minister + Wulfhere minister + Eadweald minister + Æðelstan sacerdos + Cuðulf minister + Ecgferð minister + Eadhelm minister Ista autem præfata terra hiis terminibus circumcincta esse uidetur. + Ærest easteweard ðæt ealde bocland to Fearnleage lið ðonne is ðæt suð land gemære ðæs cinges west andlang ðæs fyrhðes oð ðone bradan weg ðe uppan scet to fealcnes forda ðonne helt Medewæge ðæt norð land gemære:-""")
    # test.tune_markup_model()