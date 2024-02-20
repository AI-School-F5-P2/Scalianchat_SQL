import openai, requests
import azure.cognitiveservices.speech as speechsdk
import load_env_var

# Load environment variables OpenAI
openai.api_type, openai.api_base, openai.api_version, openai.api_key, llm_model, emb_model = load_env_var.load_env_variables_openai()
chart_model, intention_model, explanation_model = load_env_var.load_env_variables_models()

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
                                    "topNDocuments": 10,
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


def get_completion_from_messages(system_message: str, user_message: str):
    '''
    Get the completion from the OpenAI API using text as input.
    Params:
    -system_message: initial prompt.
    -user_message: user input from streamlit app.
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
        top_p=0.4,
        max_tokens=500,
        seed=42
    )
    
    print(completion)

    return completion['choices'][0]['message']['content']


def generate_plot(system_message_chart: str, user_message: str):
    '''
    This function generates a Plotly chart code based on the specified dataframe
    Params:
    -system_message_chart: initial prompt for the chart.
    -df_chart: dataframe to generate the chart code (type df_chart: pd.DataFrame)
    Returns:
    the chart code using plotly.
    '''
    response = openai.ChatCompletion.create(
        deployment_id=chart_model,
        messages=[{"role": "system", "content": system_message_chart},
                  {"role": "user", "content": user_message}],
        temperature=0,
        max_tokens=800,
        seed = 42
    )
    
    print(response)
    
    return response['choices'][0]['message']['content']


def chart_intention(system_message_intention: str, user_message: str):
    '''
    This function determines if the user is asking for a chart.
    Params:
    -system_message_intention: initial prompt for the system.
    -user_message: user input from streamlit interface.
    Returns:
    True or False as string.
    '''
    response = openai.ChatCompletion.create(
        deployment_id=intention_model,
        messages=[{"role": "system", "content": system_message_intention},
                  {"role": "user", "content": user_message}],
        temperature=0,
        max_tokens=100,
        seed = 42
    )
    
    print(response)
    
    return response['choices'][0]['message']['content']


def get_explanation_for_speech(system_message_speech: str, user_message: str):
    '''
    This function generates an explanation for the results of the query based on the provided information.
    Params:
    -system_message_speech: initial prompt for the system.
    -user_message: user input from streamlit interface.
    '''
    response = openai.ChatCompletion.create(
        deployment_id=explanation_model,
        messages=[{"role": "system", "content": system_message_speech},
                  {"role": "user", "content": user_message}],
        temperature=0,
        max_tokens=250,
        seed = 42
    )
    
    print(response)
    
    return response['choices'][0]['message']['content']