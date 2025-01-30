# 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

from groq import Groq

def chat_with_llama(user_input):
    api_key = "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"

    client = Groq(api_key=api_key)

    # Static system prompt
    system_prompt = {
        "role": "system",
        "content": "I am here to assist you. Please ask your question or share your problem."
    }

    # Get user input dynamically
    user_input = user_input

    # Prepare the messages payload
    messages = [
        system_prompt,
        {
            "role": "user",
            "content": user_input,
        }
    ]

    # Call the API
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        # Print the assistant's response
        print("Assistant:", end=" ")
        for chunk in completion:
            ans = chunk.choices[0].delta.content 
            print(ans or "", end="")
        print()  # Newline for better readability
    except Exception as e:
        print("An error occurred:", str(e))



        

# Run the chat function
# if __name__ == "__main__":
#     while True:
#         chat_with_llama()
