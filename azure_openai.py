import load_env_var
import openai


# Load environment variables
openai.api_base, openai.api_version, openai.api_key = load_env_var.load_env_variables_openai()


def get_completion_from_messages(system_message, user_message, model="test-ejemplo", temperature=0,
                                 max_tokens=500) -> str:
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{user_message}"}
    ]

    response = openai.ChatCompletion.create(
        engine=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response['choices'][0]['message']['content']


if __name__ == "__main__":
    system_message = "You are a helpful assistant"
    user_message = "Hello, how are you?"
    print(get_completion_from_messages(system_message, user_message))