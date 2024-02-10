import openai, requests
import azure.cognitiveservices.speech as speechsdk
import load_env_var
from prompts.prompts import SYSTEM_MESSAGE

# Load environment variables OpenAI
openai.api_type, openai.api_base, openai.api_version, openai.api_key, llm_model = load_env_var.load_env_variables_openai()

# Load environment variables Azure Search
search_endpoint, search_key, search_index_name = load_env_var.load_env_variables_azure_search()

# Load environment variables Azure Speech
speech_api_key = load_env_var.load_env_variables_azure_speech()

# Setup speech configuration 
speech_config = speechsdk.SpeechConfig(subscription=speech_api_key, region='francecentral')


def setup_byod(llm_model: str) -> None:
    '''
    Sets up the OpenAI Python SDK to use your own data for the chat endpoint.
    Params:
    -llm_model: the deployment ID for the model to use with your own data.
    To remove this configuration, simply set openai.requestssession to None.
    '''

    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):

        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{llm_model}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()

    # Mount a custom adapter which will use the extensions endpoint for any call using the given `llm_model`
    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{llm_model}",
        adapter=BringYourOwnDataAdapter()
    )

    openai.requestssession = session

setup_byod(llm_model)


def get_completion_from_audio(system_message: str):
    '''

    '''
    # Get the text from the microphone
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_config.speech_recognition_language="es-ES"
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)

    print("Say something...")
    speech_result = speech_recognizer.recognize_once_async().get()

    message_text = [{"role": "user", "content": speech_result.text}]

    print(message_text[0]['content'])

    # Get the completion from the OpenAI API
    completion = openai.ChatCompletion.create(
        messages=message_text,
        deployment_id=llm_model,
        dataSources=[  # camelCase is intentional, as this is the format the API expects
        {
    "type": "AzureCognitiveSearch",
    "parameters": {
        "endpoint": search_endpoint,
        "indexName": search_index_name,
        "queryType": "vectorSimpleHybrid",
        "fieldsMapping": {},
        "inScope": True,
        "roleInformation": system_message,
        "strictness": 3,
        "topNDocuments": 5,
        "key": search_key,
        "embeddingDeploymentName": "embedding-scalian"
    }
    }
        ],
        temperature=0,
        top_p=1,
        max_tokens=800,
        seed=42
    )
    print(completion)


    # Play the response on the computer's speaker
    speech_config.speech_synthesis_voice_name = 'es-ES-LaiaNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config)
    speech_synthesizer.speak_text(completion['choices'][0]['message']['content'])


def get_completion_from_messages(system_message: str, user_message: str):
    '''

    '''
    message_text = [{'role': 'system', 'content': system_message}, 
                {'role': 'user', 'content': f"{user_message}"}]

    # Get the completion from the OpenAI API
    completion = openai.ChatCompletion.create(
        messages=message_text,
        deployment_id=llm_model,
        dataSources=[  # camelCase is intentional, as this is the format the API expects
        {
    "type": "AzureCognitiveSearch",
    "parameters": {
        "endpoint": search_endpoint,
        "indexName": search_index_name,
        "queryType": "vectorSimpleHybrid",
        "fieldsMapping": {},
        "inScope": True,
        "roleInformation": system_message,
        "strictness": 3,
        "topNDocuments": 5,
        "key": search_key,
        "embeddingDeploymentName": "embedding-scalian"
    }
    }
        ],
        temperature=0,
        top_p=1,
        max_tokens=800,
        seed=42
    )
    print(completion)

    return completion['choices'][0]['message']['content']