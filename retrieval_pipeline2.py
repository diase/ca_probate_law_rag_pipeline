import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import google.generativeai as genai
from dotenv import load_dotenv 

load_dotenv()

def main():
    #1. Embeddings: same as ingestion
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    #2. Load existing Chroma DB
    db = Chroma(persist_directory="full_db", embedding_function=embeddings)
    print("Chroma DB loaded")

    #3. Initialize Gemini LLM
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    print("Gemini LLM initialized")

    while True:
        query = input("\nAsk a question (or 'q' to quit): ")
        if query.lower() in {"q", "quit", "exit"}:
            break 

        #4. Retrieve top k results with scores(Cosine Distance)
        raw_results = db.similarity_search_with_score(query.lower(), k=10)
        print("\n--- Similarities ---")
        for doc, dist in raw_results:
            similarity = 1 - dist  # Convert distance to similarity
            print(f"distance={dist:.4f}, similarity={similarity:.4f}")

        
        #5 Set cosine similarity threshold
        similarities = [1 - dist for _, dist in raw_results]
        
        filtered_docs = []
        
        threshold = 0.4

        for doc, distance in raw_results:
            similarity = 1 - distance  # Convert distance to similarity
            if similarity >= threshold:
                filtered_docs.append((doc, distance))
        
        if not filtered_docs:
            print(f"\nNo documents found above similarity threshold {threshold}.")
            continue
        
        #Print Retrieved Docs
        print("\n--- Retrieved Documents ---\n") 
        for i, (doc, score) in enumerate(filtered_docs, 1): 
            print(f"[Document {i}]")
            print(doc.metadata.get("source"))
            print(doc.page_content) 
            print("\n---\n")

        #6. Build content for Gemini
        system_instructions = (
            "You are 'California Probate Guide,' an expert legal assistant specialized in California Probate Law. "
            "Your tone is professional, clear, and supportive. Use the provided legal context to explain complex rules "
            "as if you are speaking to a person who is not a lawyer. "
            "\n\nRULES:"
            "\n- ONLY use the provided legal context. If a question is outside the legal context, say 'I don't have that specific data, but you might check the following sources:https://leginfo.legislature.ca.gov/faces/codesTOCSelected.xhtml?tocCode=PROB&tocTitle=+Probate+Code+-+PROB, https://courts.ca.gov/cms/rules/index/seven, https://selfhelp.courts.ca.gov/find-forms?query=probate, https://selfhelp.courts.ca.gov/probate-index'"
            "\n- CITATIONS: You MUST cite the source URL for every fact you state. Format: (Source: [SECOND LINE OF EVERY CHUNK])"
            
        )

        # Add retreived documents as one part
        parts = []
        for i, (doc, score) in enumerate(filtered_docs, 1):
            parts.append(f"DOCUMENT {i}\nSOURCE: {doc.metadata.get('source')}\nLEGAL CONTEXT: {doc.page_content}")
        to_append = "\n\n".join(parts)

        contents = [
            {"role": "user",
             "parts": [{"text": f"{system_instructions}"}, 
                       {"text": f"USER QUESTION: {query.lower()}"},
                       {"text": f"LEGAL CONTEXT: {to_append}"}]
            }
        ]

        #7. Get answer from Gemini
        print("\n--- Answer ---\n")

        config = {
            "temperature":0.1,
            "top_p":0.9,
            "top_k":40,
            "max_output_tokens":2048,}

        model = genai.GenerativeModel(model_name="gemini-2.5-flash", generation_config=config)

        response = model.generate_content(contents)

        print(response.text.strip())


if __name__ == "__main__":
    main()



    

