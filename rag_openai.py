import openai, requests
import azure.cognitiveservices.speech as speechsdk
import load_env_var

# Load environment variables OpenAI
openai.api_type, openai.api_base, openai.api_version, openai.api_key, llm_model, emb_model = load_env_var.load_env_variables_openai()

# Load environment variables Azure Search
search_endpoint, search_key, search_index_name = load_env_var.load_env_variables_azure_search()

# Load environment variables Azure Speech
speech_api_key = load_env_var.load_env_variables_azure_speech()

# Setup speech configuration 
speech_config = speechsdk.SpeechConfig(subscription=speech_api_key, region='francecentral')


def get_search_config(system_message: str) -> list:
    '''
    Returns the search configuration for the OpenAI API (RAG pattern).
    Params:
    -system_message: initial prompt.
    Returns:
    -data_sources: list of dictionaries with the search configuration.
    '''
    # camelCase is intentional, as this is the format the API expects
    data_sources = [{"type": "AzureCognitiveSearch",
                     "parameters": {"endpoint": search_endpoint, 
                                    "indexName": search_index_name, 
                                    "queryType": "vectorSimpleHybrid",
                                    "fieldsMapping": {"vectorFields": ["categoryVector", "contentVector"], "textFields": ["category", "content"]}, 
                                    "inScope": True,
                                    "roleInformation": system_message,
                                    "strictness": 1,
                                    "topNDocuments": 5,
                                    "key": search_key,
                                    "embeddingDeploymentName": emb_model}}]
    
    return data_sources


def setup_byod(llm_model: str) -> None:
    '''
    Sets up the OpenAI Python SDK to use our own data for the chat endpoint.
    Params:
    -llm_model: the deployment ID for the model to use with our own data.
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
    Get the completion from the OpenAI API using the microphone as input
    and speakers as output.
    Params:
    -system_message: initial prompt.
    '''
    # Get the text from the microphone
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_config.speech_recognition_language="es-ES"
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)

    print("Say something...")
    speech_result = speech_recognizer.recognize_once_async().get()

    user_input = speech_result.text

    message_text = [{"role": "user", "content": user_input}]

    print(message_text[0]['content'])

    # Get the completion from the OpenAI API
    completion = openai.ChatCompletion.create(
        messages=message_text,
        deployment_id=llm_model,
        dataSources=get_search_config(system_message),
        temperature=0,
        top_p=0.5,
        max_tokens=800,
        seed=42
    )
    
    print(completion)

    # Play the response on the computer's speaker
    speech_config.speech_synthesis_voice_name = 'es-ES-LaiaNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config)
    response_as_text = completion['choices'][0]['message']['content']
    speech_synthesizer.speak_text(response_as_text)

    return user_input, response_as_text


def get_completion_from_messages(system_message: str, user_message: str):
    '''
    Get the completion from the OpenAI API using the text as input.
    Params:
    -system_message: initial prompt.
    -user_message: user input from streamlit interface.
    Returns:
    -completion['choices'][0]['message']['content']: the response from the model.
    '''
    message_text = [{'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': f"{user_message}"}]

    # Get the completion from the OpenAI API
    completion = openai.ChatCompletion.create(
        messages=message_text,
        deployment_id=llm_model,
        dataSources=get_search_config(system_message),
        temperature=0,
        top_p=0.5,
        max_tokens=800,
        seed=42
    )
    
    print(completion)

    return completion['choices'][0]['message']['content']


def generate_plot(system_message_chart, df_chart):
    '''
    This function generates a Plotly chart code based on the specified dataframe
    Params:
    -system_message_chart: initial prompt for the chart.
    -df_chart: dataframe to generate the chart code (type df_chart: pd.DataFrame)
    Returns:
    the chart code using plotly.
    '''
    # Call the LLM model to generate the Plotly chart code
    response = openai.ChatCompletion.create(
        deployment_id=llm_model,
        messages=[{"role": "system", "content": system_message_chart},
                  {"role": "user", "content": f"Generate a Plotly chart code based on the following dataframe:{df_chart}." 
                   f"Never include fig.show() in the generated code."}],
        temperature=0,
        max_tokens=800,
        seed = 42,
    )
    
    print(response)
    
    return response['choices'][0]['message']['content']