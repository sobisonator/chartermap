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
SYSTEM_PROMPT = f"""
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

        # We need to record the column position of the witnesses.

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
    test.flag_markups(markup_class="Dating clause",search_text="+ [Greek letters: alpha omega] Alti[thro]ni [moderatoris imperio triuiatim instruimur ut illi] opp[ido subiecti subp]editantes famulemur qui totius mun[di fa]bricam miro ineffabilique serie dis[ponens] microcosmum Adam uidelicet tandem quadriformi plasmatum materia . almo ad sui similitudinem instinctum spiramine . uniuersis quae in infimis formauerat uno probandi causa excepto uetitoque praeficiens paradisiace amoenitatis iocunditate conlaterana [Aeua scilic]et comite decentissime collocauit . Laruarico pro dolor seductus cauillatione uersipellis suasilibilisque tergiuersatione uiraginis pellectus . anathematis alogia ambro pomum momordit uetitum . et sibi ac posteris in [hoc aer]umnoso deiectus saeculo loetum promeruit perpetuum . Uati[cina]ntibus siquidem prophetis et celitus superni regis diuturna clandestino praesagia dogmate promentibus nitide orthodoxis . eulogium ex supernis deferens . non ut Iudaeorum seditiosa elingue fatetur loquacitas . sed priscorum atque modernorum lepidissimam ambiens facundiam Arrianas Sabellianasque proterendo nenias anagogico infrustrans famine . nosque ab obtunsi cecitate umbraminis . ad supernorum alacrimoniam patrimoniorum aduocans . angelus supernis elapsus liminibus in aurem intemerate uirginis ut euangeli[ca] promulgant famina . stupenda cecinisse uidetur carmina . cui eclesia tota uidelicet catholica consona uoce altibohando proclamat . Beata es uirgo MARIA que credidisti perficientur in te que dicta sunt tibi a Domino . Mirum dictu incarnatur uerbum et incorporatur scilicet illud . de quo euangel[ista] supereminens [uniuers]orum altitudine sensum inquit . In principio erat uerbum . et uerbum erat apud Deum . et Deus erat uerbum . et reliqua . Qua uidelicet sumpta de uirgine incarnatione antique uirginis facinum demitur . et cunctis mulieribus nitidis precluens taumatibus decus irrogatur . Intacta igitur [redol]ente [Christi diu]initate . passaque ipsius humanitate . libertas addictis clementer contigit seruulis . Hinc ego ÆÞELRÆD altithrono aminiculante Anglorum ceterarumque gentium in circuitu triuiatim persistentium basileus . non immemor angustiarum michi meaeque nationi septimo regn[i mei ann]o et deinceps frequenter ac multipliciter accidentium . post decessum uidelicet beatae memorie . michique interno amore dilectissimi ADELUUOLDI episcopi . cuius industria ac pastoralis cura non solum [mee] uerum etiam uniuersorum huius patrie tam pr[elatorum] quam subditorum utilitati superno plasmatore inspirante consuluit . mecum plurima uoluere tacitus cepi . et que tantorum causa periculorum existeret . studiose percunctari sollicitus curaui . Tanto igitur tali[que stu]dio magnopere incitatus . et archana quaeque di[ligenti cura] mecum examinans . tandem Domini conpunctus gratia ad memoriam reduxi . partim hec infortunia pro meae iuuentutis ignorantia que diuersis solet uti moribus . partim etiam pro quorundam illorum detestand[a] philargiria qui meae utilitati consulere debebant accid[isse] . Siquidem inter caetera memoriae occurrit . me rogatu quorundam talium . UULGARI scilicet episcopi defuncti . at[que duc]is Ælfrici qui adhuc superest . sacri ÆBBANDUNENSIS coenob[ii lib]ertatem . pro munere in se[ruitute redigisse . quod prefatus beate memorie] episcopus ADELUUOLD a predecessoribus meis EADREDO scilicet rege . patruo patris mei . necnon et a [patru]o meo rege EADUUIGE nec minus et a patre meo rege uidelicet EADGARO ad usum monachorum Domino [Iesu Christo eiusque] genitrici MARIAE humilitatis et obedientiae ceterarumque uirtutum meritis . in aeternam promeruit hereditatem . et [in] perhennem adquisiuit libertatem . Haec igitur mecum uigilanti p[e]ctore uoluens . et citius a tanto tamque exhorrendo anathemate liberari [cu]piens . anno dominice incarnationis .dccccxciii. . mei autem regni xvii . sinodale concilium UUINTONIAE in die sancto Pentecosten fieri iussi . illucque episcopis . et abbatibus ac ceteris optimatum meorum [pri]moribus uerba salutatoria et pacifica benignissime destinaui . cunctosque Christi inspirante gratia monui . ut quaeque superno creatori digna . quaeque spiritali anime meae saluti . seu regali meae dignitati congrua . quaeque [etiam] omni Anglorum populo op[ort]una ualerent . Domino consulente in commune tractarent . uouens etiam [me u]ita comite et retroactas ad purum cohercere neglegentias . et iuxta praedecessorum meorum decreta . Iesu Christo Domino nostro eiusque genitrici priscum restituere libertatis cyrographum . Hoc illi meo . immo Christi monitu simul et hortatu magnopere delectat[i . uo]ti compotes saluatori Christo gratias egerunt . et quaeque condigna salubriter instituta sanxerunt . pacto spiritali confirmauerunt . Nunc autem ego ÆÞELRÆD Anglorum Christo opitulante basileus . quo debitum uoti mei factis adimpleam [et ut] aeternae libertatis altithroni moderatoris clementia merear optinere consortium . pretium quod michi dux praefatus Ælfric . pro fratris sui EADUUINI prioratu contulit . q[uo] praefata Christi sanctaeque eius genitricis hereditas iniqua seruitute est uenundata . perpetualiter anathematizando reicio . et gratuita Domini inspirante gratia meorumque optimatum tam laicorum quam ordinatorum rogatus simul et usus consilio . eidem sanctae Christi genitricis aecclesiae monachisque inibi degentibus aeternam priuilegii ut praedecessores mei renouandam concedo libertatem . Huius etenim renouande libertatis auctoritas . Christi auctoritate nostraque largitate concessa et corroborata est die .xvi. kalendarum Augustarum . in oratorio uici qui usitato GILLINGAHAM nominari solet . missaeque caelebratione peracta sub horum testium presentia me assensum prebente confirmata est . abbatis scilicet Ælfsini . consanguineique mei Æþelmæri . necnon et auunculi [mei] Ordulfi . ac prioratum prefati ÆBBANDUNENSIS coenobii in manu et potestate UULFGARI abbatis michi humillima deuotione subiecti . gratis sine pretio uoluntariae renouando commisi . hancque priuilegii libertatem tam sibi quam cunctae simul eiusdem sanctae aeclesiae congregationi pro mille quingentis missarum solemniis . ac mille ducentis psalteriorum melodiis quas spontanea deuotione pro aeterna anime meae redemptione decantauerunt . aeternaliter renouandam cum sanctae crucis impressione concessi . quatinus post decessum eiusdem prefati abbatis UULFGARI . cuius temporibus hec ipsa libertatis restauratio Christo suf[frag]ante concessa est quem sibi uniuersa praefati coenobii congre[gati]o apto elegerit consilio secundum regularia beati BENEDICTI instituta abbatem iuste ex eodem [fratrum] cuneo eligens constituat . Huius priuilegii libertas deinceps usu perpetuo a cunctis teneatur catholicis . nec extraneorum quispiam tyrannica fretur contumacia in predicto monasterio ius arripiens exerceat potestatis . sed eiusdem coenobii collegium perpetuae ut predixi libertatis glorietur priuilegio . Sit autem prefatum monasterium omni terrene seruitutis eodem tenore liberum . quo a predecessoribus nostris catholicis a sancto LEONE uidelicet papa . et COENULFO rege catholico uetusto continetur priuilegio HRETHUNO abbate optinente solutum . Agri equidem ad usus monachorum Domino nostro Iesu Christo eiusque genitrici MARIAE priscis modernisque temporibus a regibus et religiosis utriusque sexus hominibus et a me ipso . meoque patre EADGARO rege . fratreque eius meo patruo rege EADWIGO eorumque patruo scilicet EADREDO rege fidelissimo restituendo iure concessi sunt . eiusdem perpetue sint libertatis . Nam reges prefati rus quod ABBANDUN nuncupatur quod rex CEADWEALLA Domino nostro eiusque genitrici MARIAE priscis temporibus deuoto concesserat animo . in quo predecessores nostri diabolica decepti auaritia edificium sibi regale iniuste construxerant . aeclesiae Dei restituentes interdixerunt . ut regum nemo inibi pastum requireret . nec edificium in sempiternum constru[eret] . Quod ego ÆÐELRED Anglorum basileus optimatum meorum us[us co]nsilio tam meis quam meorum successorum temporibus . fixum in nomine Patris et Filii et Spiritus Sancti fieri in aeternum precipio . Tempore siquidem quo rura quae Domino deuote per hoc modernum priuilegium restauraui animo iniuste a sancta Dei aeclesia ablata [fuerant] . perfidi quique nouas sibi hereditarias kartas usurpantes ediderunt . Sed in Patris et Filii et Spiritus Sancti nomine precipimus . ut catholicorum nemo easdem recipiat. sed a cunctis repudiate fidelibus in anathemate deputentur ueteri iugiter uigente priuilegio . Si quis uero tam epylempticus phylargirie seductus amentia quod non optamus . hanc nostrae munificentiae renouatam libertatem ausu temerario infringere temptauerit . sit ipse alienatus a consortio sanctae Dei aeclesie necnon et a participatione sacrosancti corporis et sanguinis Domini nostri Iesu Christi . per quem totus terrarum orbis ab antiquo humani generis inimico liberatus est . et cum Iuda Christi proditore in sinistra parte deputatus . ni prius hic digna satisfactione humilis penituerit . quod contra sanctam Dei aeclesiam rebellis agere praesumpsit . nec in uita hac practica ueniam . nec in theorica requiem apostata optineat ullam . sed aeternis barathri incendiis trusus iugiter miserrimus crucietur. Anno dominice incarnationis ut predixi dccccxciii . indictione .vi. humillimo rogatu prefati et deuoti abbatis UULFGARI scriptum est huius renouate libertatis priuilegium . his testibus consentientibus quorum inferius nomina secundum uniuscuiusque dignitatem utriusque ordinis decusatim Domino disponente karaxantur. + Ego ÆÞELRED Brittanie Anglorum monarchus . hoc taumate agie crucis roboraui. + Ego SIGERIC Dorobernensis aeclesie archiepiscopus . eiusdem regis beniuolentiam subscripsi. + Ego Ælfstan Lundoniensis aeclesie episcopus . hanc regis munificentiam confirmaui. + Ego Ælfheah Uuintoniensis ecclesiae episcopus hanc renouationis libertatem corroboraui. + Ego Ælfric Coruinensis parrochie episcopus . qua prefatum adiacet monasterium huic dono sanctam crucem impressi. + Ego Ælfheah Licetfeldensis aeclesie episcopus . testudinem sancte crucis depinxi. + Ego Æscwig Dorcensis eclesie episcopus . hoc regalem donum consolidaui. + Ego Þeodred Orientalium Anglorum episcopus . huic largitati assensum prebui. + Ego Ælfstan Hrofensis eclesie episcopus . huic dapsilitati crucem imposui. + Ego Ordbyrht Australium Saxonum episcopus . sigillum sancte crucis annotaui. Px + Ego Wulfsige Scirburnensis eclesiae episcopus . gaudenter consensi. + Ego Ealdulf Wigornensis eclesiae episcopus . hilari uultu subscripsi. Ego Aþulf Herefordensis eclesie episcopus . mihi placere respondi. Ego Sigar Wyllensis eclesie episcopus . ita posse fieri dignum duxi. Ego Alfwold Cridiensis eclesie episcopus . huic statuto non contradixi. Ego Ealdred Cornubiensis eclesie episcopus hoc decretum consentiendo laudaui. Ego Ælfðryð mater eiusdem regis huius doni fautrix extiti. Ego Æþelstan eiusdem regis filius . hoc stare non rennui. Ego Ecgbyrht eiusdem quoque regis filius . assensum prebere non distuli. Ego Eadmund eiusdem etiam regis filius . hoc posse fieri non interdixi. Ego Eadred eiusdem quidem regis filius . hoc mihi placere professus sum. Ego UULFGAR abbas Abbandunensis coenobii hoc sintagma triumphans dictaui. Ego Ælfweard Glæst' abbas. + Ego Wulfric Aug' abbas. + Ego Ælfsige Niw' abbas. + Ego Byrhtnoþ Ælig' abbas. + Ego Lyfinc [Ceort'] abbas. + Ego Ælfric . Meal' abbas. Ego Ælfhere . Baþan' abbas. Ego Leofric . Micel' abbas. + Ego Ælfhun . Middel' abbas. Ego Byrhthelm . Eaxc' abbas. Ego Æþelric . Æþel' abbas. Ego Wulfsige . Westm' abbas. Ego Germanus . Ram' abbas. Ego Kenulf . Burh' abbas. Ego Godeman . Þorn' abbas. Ego Alfwold . Wincl' abbas. + Ego [Leofric Al]ban' abbas. [Ego Æþel]weard dux. Ego Ælfric dux. Ego Ælfhelm dux. Ego [Ælf]sige minister. Ego Æþelsige minister [Eg]o Æþelmær minister. [Ego Bri]htwold minister. [Ego O]rdulf minister. [Ego W]ulfheah minister. [Ego W]ulfric minister. [Ego W]ulfgeat minister. + Egfo Ælfwig Westm' abbas.")
    # test.tune_markup_model()