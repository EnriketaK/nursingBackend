from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from tutorials.models import *
from tutorials.serializers import *
from rest_framework.decorators import api_view

from llm_commons.proxy.base import set_proxy_version
set_proxy_version('aicore')
from llm_commons.proxy.openai import ChatCompletion, Embedding
from llm_commons.langchain.proxy import ChatOpenAI
from llm_commons.langchain.proxy import OpenAIEmbeddings

from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
# The model access is pre-configured and consumable via IDs. For readability we define a mapping here.
# models = [RECEIVE FROM SAP]

@api_view(['GET'])
def forms_list(request):

    if request.method == 'GET':
        forms = AdmissionForm.objects.all()
        forms_serializer = AdmissionFormSerializer(forms, many=True)
        
        return JsonResponse(forms_serializer.data, safe=False)
    

@api_view(['GET', 'PUT'])
def form_detail(request, pk):
    try: 
        form = AdmissionForm.objects.get(pk=pk) 
    except AdmissionForm.DoesNotExist: 
        return JsonResponse({'message': 'The admission form does not exist'}, status=status.HTTP_404_NOT_FOUND) 
 
    if request.method == 'GET': 
        f_serializer = AdmissionFormSerializer(form) 
        return JsonResponse(f_serializer.data) 
    
    elif request.method == 'PUT': 
        f_data = JSONParser().parse(request) 
        f_serializer = AdmissionFormSerializer(form, data=f_data) 
        if f_serializer.is_valid(): 
            f_serializer.save() 
            
            return JsonResponse(f_serializer.data) 
        return JsonResponse(f_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


@api_view(['POST'])
def save_admission_form(request):
    if request.method == 'POST':
        f_data = JSONParser().parse(request)
        f_serializer = AdmissionFormSerializer(data=f_data)
        if f_serializer.is_valid():
            f_serializer.save()
            print(f_serializer.data)
        
            return JsonResponse(f_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(f_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def save_summary(request):
    if request.method == 'POST':
        s_data = JSONParser().parse(request)
        s_serializer = FormSummaryDtoSerializer(data=s_data)
        
        if s_serializer.is_valid():
            try: 
                admission_form = AdmissionForm.objects.get(pk=s_serializer.validated_data['admissionFormFk'])
                summary_obj = FormSummary()
                summary_obj.content = s_serializer.validated_data['content']
                summary_obj.admissionFormFk = admission_form
                summary_obj.save()
                
                return JsonResponse(s_serializer.data, status=status.HTTP_201_CREATED) 
            
            except AdmissionForm.DoesNotExist: 
                return JsonResponse({'message': 'The admission form does not exist'}, status=status.HTTP_404_NOT_FOUND) 
            
        return JsonResponse(s_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['POST'])
def get_suggestion(request):
    if request.method == 'POST':
        f_data = JSONParser().parse(request)
        f_serializer = AdmissionFormSerializer(data=f_data)
        if f_serializer.is_valid():
            print(f_serializer.data)
            summary_suggestion = create_suggestion(f_serializer.data)
                        
            return JsonResponse(summary_suggestion, safe=False, status=status.HTTP_201_CREATED) 
        return JsonResponse(f_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
def get_translated_summaries(request):
    if request.method == 'POST':
        f_data = JSONParser().parse(request)
        f_serializer = TranslateTypeSerializer(data=f_data)
        if f_serializer.is_valid():
            print(f_serializer.data)
            summaries_translated = translate_summaries(f_serializer.data)
            print(summaries_translated)
                        
            return JsonResponse(summaries_translated, safe=False, status=status.HTTP_201_CREATED) 
        return JsonResponse(f_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_summaries(request, pk):
    
    if request.method == 'GET':
        all_summaries = FormSummary.objects.all()
        summaries = all_summaries.filter(admissionFormFk=pk)
        s_serializer = FormSummarySerializer(summaries, many=True)
        
        print("summaries")
        print(summaries)
        
        return JsonResponse(s_serializer.data, safe=False)
 


def translate_summaries(translate_data):
    
    template = '''Translate these paragraphs to the given language.
    After translating put them in a json. The key should be for example 'summary1'
    while the value is the paragraph.'''

    
    prompt = f'''Language to translate to: {translate_data['language']}.
                Paragraphs to translate:
                1) {translate_data['summary1']}
                2) {translate_data['summary2']}
                3) {translate_data['summary3']}
            '''
    
    chat_llm = ChatOpenAI(config_id=models['gpt-4'])
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    
    example_human = HumanMessagePromptTemplate.from_template("")
    example_ai = AIMessagePromptTemplate.from_template("")
    human_template = "{text}"
    
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, example_human, example_ai, human_message_prompt])
    
    chain = LLMChain(llm=chat_llm, prompt=chat_prompt)
    
    response = chain.run(prompt)
    
    return response



def create_suggestion(form_data):    
        
    # perfect for gpt4 ????
    template = '''You are a helpful nursing assistant that provides a summary of the form filled out by a patient. 
    The summary should consist of bullet points.
    Do not include question in the summaries that patient answered true for option 'no impairment'.
    Do not include question in the summaries that patient answered true for option 'no'.
    Do not include question in the summaries that patient left answer empty.
    One bullet point should consist of only the question option choosen.
    Put the summary in a json. 
    The json will have only have 1 field: 'summary'.
    The value of this field will be the summary.
    
    /// EXAMPLE OF ONE OF THE SUMMARIES OF YOUR RESPONSE ///
        "summary1": [
        "Living alone"
        "Elevator available",
        "Degree of care: 2",
        "Visual impairment in left eye",
        "Hard of hearing in right ear",
        "Disability amputation, hemiplegia",
        "Parenteral nutrition",
        "Former smoker",
        "Pressure ulcers present",
        "General skin condition: no findings",
        "Personal care / ability to dress oneself: Self-employed",
    ] '''
    
    
    prompt = f'''
                    1. Care situation
                    Living alone: ax)yes: {form_data['liveAloneYes']}. az)no: {form_data['liveAloneNo']}. b)floor: {form_data['liveAloneFloor']}. d) elevator: {form_data['liveAloneLift']}.
                    Obligations resulting from personal environment: {form_data['obliationsYes']}.
                
	                1iii) Degree of care: {form_data['careYes']}. If true, degree of care is
                        b1)1: {form_data['careDegree1']}
                        b2)2: {form_data['careDegree2']}
                        b3)3: {form_data['careDegree3']}
                        b4)4: {form_data['careDegree4']}
                        b5)5: {form_data['careDegree5']}
                    
                    2. Current medical state 
                    2i) Communication
                    a)	no impairment: {form_data['commNoImpairment']}.
                    b)	measures for communication in a foreign language: a)No: {form_data['commForeignLangNo']}.
                    c)	sign language: {form_data['commSignLang']}.
                    d)	speech disorder: {form_data['commDisorder']}.
                    e)	tracheostoma: {form_data['commTrach']}.

                    2ii) Vision
                    a)	visual impairment ax)left eye: {form_data['visionLeft']} az)right eye: {form_data['visionRight']}.
                    b)	blindness bx)left eye: {form_data['blindnessLeft']} bz)right eye: : {form_data['blindnessRight']}.
                    c)	visual aids in place dx)yes: {form_data['visualAidLeft']}.

                    2iii) Hearing
                    a)	no impairment: {form_data['hearingNoImp']}.
                    b)	hearing aid in place ax) right ear: {form_data['hearingAidRight']} az) left ear: {form_data['hearingAidLeft']}.
                    c)	hard of hearing bx) right ear: {form_data['hearingHardRight']} bz) left ear: {form_data['hearingHardLeft']}.
                    d)	deafness dx)right ear: {form_data['deafnessRight']} dz) left ear: {form_data['deafnessLeft']}.

                    2v) Disorientation
                    a)	no impairment: {form_data['disorNoImp']}.
                    b)	disorientation of 
                    b1)time: {form_data['disorTime']}
                    b2)place: {form_data['disorPlace']}
                    b3)person: {form_data['disorPerson']}.

                    2vi) Understanding (thinking)
                    a)	no impairment: {form_data['understNoImp']}.
                    b)	confusion: {form_data['understConfusion']}.
                    c)	nervousness / restlessness: {form_data['understNerv']}.
                    d)	altered consciousness: {form_data['understAltered']}.
                    
                    2vii) Disability
                    b)	Yes: {form_data['disabilityYes']}. 
                    b1)Hemiplegia: {form_data['disabilityHemiYes']}. Hemiplegia: : {form_data['disabilityHemi']}. 
                    b2)Amputation: {form_data['disabilityAmputYes']}. Amputation: {form_data['disabilityAmput']}. 
                    b3)Paraplegia: {form_data['disabilityParaYes']}. Paraplegia: {form_data['disabilityPara']}. 
                    b4)Tetraplegia: {form_data['disabilityTetraYes']}. Tetraplegia: {form_data['disabilityTetra']}. 
                    b5)Missing limbs: {form_data['disabilityLimbsYes']}. Missing limbs: {form_data['disabilityLimbs']}. 
                    b6)Misalignment: {form_data['disabilityMisalYes']}. Misalignment: {form_data['disabilityMisal']}.
                    c)	Prosthetic aids in place? x)yes: {form_data['disabilityProYes']}.

                    2viii) Sleep
                    a)	no impairment: {form_data['sleepNoImp']}.
                    b)	difficulty falling asleep or staying asleep (more than 30 min.): {form_data['sleepDiff']}.
                    c)	breathing interruptions / dyspnoea (anamnesis determined): {form_data['sleepBreath']}.

                    2ix) Diet
                    a)	whole food: {form_data['dietWhole']}.
                    b)	whole food without sugars: {form_data['dietNoSugar']}.
                    c)	vegetarian: {form_data['dietVeg']}.
                    d)	diabetic diet: {form_data['dietDiabetic']}.

                    2x) Ingestion
                    a)	oral: {form_data['ingestOral']}.
                    b)	feeding tube: {form_data['ingestFeed']}.
                    c)	parenteral nutrition: {form_data['ingestParent']}.

20) Excretion
21) Urine
a)	no impairment: {form_data['excNoImp']}.
b)	incontinence: {form_data['excIncont']}.
c)	increased urination at night: {form_data['excIncrease']}.
d)	bladder catheter: {form_data['excBladder']}.

21) Bowel movement
a)	no impairment: {form_data['bowelNoImp']}.
b)	incontinence: {form_data['bowelIncon']}.
c)	diarrhoea: {form_data['bowelDiarr']}.
d)	constipation: {form_data['bowelCons']}.
e)	anus praetor: {form_data['bowelPraetor']}.
f)	laxative intake: {form_data['bowelLax']}.
g)	uses aids: {form_data['bowelAids']}.

2xii) Pains
x)	Pain: ax)Yes: {form_data['painYes']}.
a1) Body part: {form_data['painPart1']}.
a2) Side:  {form_data['painSide1']}.
a3) Condition: {form_data['painState1']}.
a4) Intensity at rest (1 hardly any pain; 10 strongest pain): {form_data['painRest1']}.
a5) Intensity during exercise (1 hardly any pain; 10 strongest pain): {form_data['painExc1']}.
a6) Occurrences: {form_data['painFreq1']}.
a7) Type of pain: {form_data['painType1']}.

b1) Body part: {form_data['painPart2']}.
b2) Side: {form_data['painSide2']}.
b3) Condition: {form_data['painState2']}.
b4) Intensity at rest (1 hardly any pain; 10 strongest pain): {form_data['painRest2']}. 
b5) Intensity during exercise (1 hardly any pain; 10 strongest pain): {form_data['painExc2']}.
b6) Occurrences: {form_data['painFreq2']}.
b7) Type of pain: {form_data['painType2']}.

c1) Body part: {form_data['painPart3']}.
c2) Side:  {form_data['painSide3']}.
c3) Condition: {form_data['painState3']}.
c4) Intensity at rest (1 hardly any pain; 10 strongest pain): {form_data['painRest3']}. 
c5) Intensity during exercise (1 hardly any pain; 10 strongest pain):  {form_data['painExc3']}.
c6) Occurrences: {form_data['painFreq3']}.
c7) Type of pain: {form_data['painType3']}.

2xiii) Substance use
a)	yes: {form_data['substYes']}.
b)	smoker: {form_data['substSmoker']}. Number of cigarettes: {form_data['substSmokerNr']}.
c)	former smoker: {form_data['substFormer']}.
d)	alcohol consumption: {form_data['substAlcohol']}. da) regular: {form_data['substAlcoholReg']}. db) occasional: {form_data['substAlcoholOcc']}.
e)	narcotics: {form_data['substNarc']}.

2xiv) Skin condition/pressure ulcers
a)	Pressure ulcers: yes: {form_data['ulcersYes']}. 
a1) Is there another wound a) yes: {form_data['ulcersWoundYes']}.
b)	General skin condition ba) no findings: {form_data['skinNoFind']}.bb) dry: {form_data['skinDry']}. 
bc) moist: {form_data['skinMoist']}. bd) dermatological disease: {form_data['skinDerm']}. 
be) parchment skin: {form_data['skinParch']}. bf) hematoma: {form_data['skinHema']}.

3. Self-care ability

3i) personal care / ability to dress oneself
a)	Support required: {form_data['careDressSupp']}.
b)	Self-employed: {form_data['careDressSelf']}.

3ii) food, drink
a)	Support required: {form_data['careFoodSupp']}.
b)	Self-employed: {form_data['careFoodSelf']}.

3iii) excretion
a)	Support required: {form_data['careExcSup']}.
b)	Self-employed: {form_data['careExcSelf']}.

3iv) walking / transfer
a)	Support required: {form_data['careWalkSupp']}.
b)	Self-employed: {form_data['careWalkSelf']}.

3v) Objects close to body
a)	Yes: {form_data['objYes']}. 
b1) compression stockings: {form_data['objCompress']}. 
b2) O2 device: {form_data['objDevice']}. a3) orthoses: {form_data['objOrtho']}. 
b4) prostheses: {form_data['objPros']}. a5) others: {form_data['objOthers']}.
3va) Skin condition of the item a) intact: {form_data['skinIntact']}. 
b) not intact: {form_data['skinNotInt']}. c) not ascertainable: {form_data['skinNotAsc']}.

3vi) Inlets and outlets
a)	Yes: {form_data['inletsYes']}.
b)	Port bx) yes: {form_data['inletsPortYes']}.
c)	Probes cx) yes: {form_data['inletsProbesYes']}.
d)	Urinary diversion dx) yes: {form_data['inletsUrineYes']}.
e)	Stomata ex) Yes: {form_data['stomataYes']}. 

3vii) Risk of falling 
3viia) Have you fallen in the last 12 months a) yes: {form_data['fallYes']}. 
b1) 1x: {form_data['fall1x']}. 
b2) 2x: {form_data['fall2x']}. 
b3) 3x: {form_data['fall3x']}. 
b4)More common: {form_data['fallMore']}.
3viii) psychotropic drugs / sedatives a) yes: {form_data['drugsYes']}.
3ix Diagnoses: a) syncope (fainting): {form_data['diagnoseSync']}. b) epilepsy TIA (mini stroke): {form_data['diagnoseEpil']}. 
c) Huntington’s disease (CNS related): {form_data['diagnoseHunt']}.  d) Type 2 diabetes: {form_data['diagnoseDiab']}. e) No: {form_data['diagnoseNo']}.

4. Allergies
a) known: {form_data['allergyYes']}. 
1.{form_data['allergyKnown1']}. 2.{form_data['allergyKnown2']}. 3.{form_data['allergyKnown3']}.
'''

    print(prompt)
    
    chat_llm = ChatOpenAI(config_id=models['gpt-4'])
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    
    example_human = HumanMessagePromptTemplate.from_template('')
    example_ai = AIMessagePromptTemplate.from_template('')
    human_template = "{text}"
    
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, example_human, example_ai, human_message_prompt])
    
    chain = LLMChain(llm=chat_llm, prompt=chat_prompt)
    
    response = chain.run(prompt)
    
    return response
