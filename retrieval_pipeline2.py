import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import google.generativeai as genai
from dotenv import load_dotenv 

load_dotenv()

def main():
    #1. Embeddings: same as ingestion
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    #2. Load existing Chroma DBs
    statute_db = Chroma(persist_directory="statute_db", embedding_function = embeddings)
    self_help_db = Chroma(persist_directory="self_help_db", embedding_function = embeddings)
    rule_db = Chroma(persist_directory="rule_db", embedding_function = embeddings)
    form_db = Chroma(persist_directory="form_db", embedding_function = embeddings)
    print("Chroma DBs loaded")
    #print("Total chunks in DB:", db._collection.count())

    ###Delete Later
    #results = db.similarity_search("6110", k=5) 
    #for doc in results: 
    #    print(doc.page_content[:300])

    #3. Initialize Gemini LLM
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    print("Gemini LLM initialized")

    while True:
        query = input("\nAsk a question (or 'q' to quit): ")
        if query.lower() in {"q", "quit", "exit"}:
            break 

        #4. Retrieve top k results with scores(Cosine Distance)
        form_keywords = ["form", "file", "submit", "attach", "de-", "de -", "ge-", "ge -", "app-", "app -", "jv-", "jv -"]
        rule_keywords = ["notice", "deadline", "hearing", "inventory", "petition", "time limit"]
        statute_keywords = ["inherit", "liable", "duty", "power"]
        self_help_keywords = ["what is", "when is", "explain", "overview", "basics", "summary", "summarize"]

        if any(w in query.lower() for w in form_keywords):
            db = form_db
        elif any(w in query.lower() for w in rule_keywords):
            db = rule_db
        elif any(w in query.lower() for w in statute_keywords):
            db = statute_db
        elif any(w in query.lower() for w in self_help_keywords):
            db = self_help_db
        else:
            db = statute_db

        raw_results = db.similarity_search_with_score(query.lower(), k=10)
        print("\n--- Similarities ---")
        for doc, dist in raw_results:
            similarity = 1 - dist  # Convert distance to similarity
            print(f"distance={dist:.4f}, similarity={similarity:.4f}")

        
        #5 Set cosine similarity threshold
        similarities = [1 - dist for _, dist in raw_results]
        #threshold = max(similarities) * 0.2 # keep any document that is at least 20% of the top similarity
        filtered_docs = []
        # Sort similarities descending
        sorted_sims = sorted(similarities, reverse=True)
        # Compute index for top 50%
        cutoff_index = int(len(sorted_sims) * 0.5) #keep top 50%
        # The similarity at that position becomes the threshold
        threshold = sorted_sims[cutoff_index]


        for doc, distance in raw_results:
            similarity = 1 - distance  # Convert distance to similarity
            if similarity >= threshold:
                filtered_docs.append((doc, distance))
        
        #Handle no results(Useless currently as we keep 50%)
        
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
        contents = [
            {"role": "user",
             "parts": [{"text": "You are a helpful assistant answering questions based only on the provided context. Answer clearly and concisely citing the source. If the answer is not in the context, say you don't know."},
            {"text": f"Question: {query.lower()}"}]
            }
        ]
        # Add retreived documents as one part
        parts = []
        for doc, score in filtered_docs:
            parts.append(f"{doc.metadata.get("source")}\n{doc.page_content}")
        to_append = "\n\n".join(parts) 
        contents[0]["parts"].append({"text": f"Context: {to_append}"})

        #7. Get answer from Gemini
        print("\n--- Answer ---\n")

        config = {
            "temperature":0.1,
            "top_p":1.0,
            "top_k":10,
            "max_output_tokens":2048,}

        model = genai.GenerativeModel(model_name="gemini-2.5-flash", generation_config=config)

        response = model.generate_content(contents)

        print(response.text.strip())


if __name__ == "__main__":
    main()



    

