import re
import openai
import azure.cognitiveservices.speech as speechsdk
import load_env_var

# Load environment variables OpenAI
openai.api_type, openai.api_base, openai.api_version, openai.api_key, llm_model, emb_model = load_env_var.load_env_variables_openai()
chart_model, intention_model = load_env_var.load_env_variables_models()

# Load environment variables Azure Speech
speech_api_key = load_env_var.load_env_variables_azure_speech()

# Setup speech configuration 
speech_config = speechsdk.SpeechConfig(subscription=speech_api_key, region='francecentral')


def get_text_from_speech():
    '''
    Gets text from the microphone and returns a string.
    '''
    # Get the text from the microphone
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_config.speech_recognition_language="es-ES"
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)

    print("Say something...")
    speech_result = speech_recognizer.recognize_once_async().get()

    user_input = speech_result.text

    print(user_input)

    return user_input


def get_speech_from_text(response: str):
    '''
    Play the response on the computer's speaker
    '''
    # speech_config.speech_synthesis_voice_name = 'es-ES-LaiaNeural'
    # speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config)
    # response_as_text = completion['choices'][0]['message']['content']
    # speech_synthesizer.speak_text(response_as_text)


def get_sql_code_from_response(response: str):
    '''
    This function extracts the SQL code from the response of the LLM model.
    Params:
    -response: the response from the LLM model as a string.
    Returns:
    -sql_code: the SQL code cleaned and ready to execute.
    '''
    match = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL)
    
    if match:
        sql_code = match.group(1)
        return sql_code.strip()  # Eliminate leading and trailing whitespaces
    else:
        print("SQL code not found in response.")
        return None


def get_plotly_code_from_response(response: str):
    '''
    This function extracts the Plotly code from the response of the LLM model.
    Params:
    -response: the response from the LLM model as a string.
    Returns:
    -plotly_code: the Plotly code cleaned and ready to execute.
    '''
    match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
    
    if match:
        plotly_code = match.group(1)
        plotly_code = plotly_code.replace('fig.show()', '').strip()
        return plotly_code  # Eliminate leading and trailing whitespaces
    else:
        print("Plotly code not found in response.")
        return None