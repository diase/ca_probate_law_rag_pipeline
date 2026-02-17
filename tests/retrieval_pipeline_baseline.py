#Retrieval pipeline that doesn't give the added context for comparison

import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import google.generativeai as genai
from dotenv import load_dotenv 
 
load_dotenv()

def main():

    #Initialize Gemini LLM
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    print("Gemini LLM initialized")

    #Get user input
    while True:
        query = input("\nAsk a question (or 'q' to quit): ")
        if query.lower() in {"q", "quit", "exit"}:
            break 

        #Sets up context and question for Gemini
        contents = [
            {"role": "user",
                "parts": [{"text": "You are a helpful assistant answering questions from users. Answer clearly and concisely"},
                {"text": f"Question: {query.lower()}"}]
            }
        ]

        #7. Get answer from Gemini
        print("\n--- Answer ---\n")

        config = {
            "temperature":0.2,
            "top_p":1.0,
            "top_k":10,
            "max_output_tokens":2048,}

        model = genai.GenerativeModel(model_name="gemini-2.5-flash", generation_config=config)

        response = model.generate_content(contents)

        print(response.text.strip())

if __name__ == "__main__":
    main()


