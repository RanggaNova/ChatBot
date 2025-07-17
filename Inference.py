from google.generativeai import configure, GenerativeModel
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

configure(api_key=api_key)

model = GenerativeModel('gemini-2.0-flash') 

def chat_bot(prompt):
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    user_input = input("Chat: ")
    print(chat_bot(user_input))
