import get_speech
import api_calls


u_question = get_speech.voice_to_text()

if u_question == "text No speech detected" or "Error : In generating":
    print("Error related speech recognition")

else:
    ans = api_calls.chat_with_llama(u_question)
    print(ans)