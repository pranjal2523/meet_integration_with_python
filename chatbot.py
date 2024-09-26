import openai

# Set your OpenAI API key
api_key = # saved in .env file
openai.api_key = # saved in .env file


def list_available_models():
    models = openai.Model.list()
    for model in models['data']:
        print(model['id'])

def get_chatbot_response(prompt):
    # client = openai.OpenAI()
    client = openai.OpenAI(
        api_key=api_key,  # this is also the default, it can be omitted
    )
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        # model="gpt-4o-mini",  # You can also use "gpt-4" if you have access
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def main():
    print("Welcome to the Chatbot! Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = get_chatbot_response(user_input)
        print("Chatbot:", response)

if __name__ == "__main__":
    main()
