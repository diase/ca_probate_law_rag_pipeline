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
    db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    print("Chroma DB loaded")
    print("Total chunks in DB:", db._collection.count())

    #3. Initialize Gemini LLM
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    print("Gemini LLM initialized")

    while True:
        query = input("\nAsk a question (or 'q' to quit): ")
        if query.lower() in {"q", "quit", "exit"}:
            break 

        #4. Retrieve top k results with scores(Cosine Distance)
        raw_results = db.similarity_search_with_score(query, k=5)
        print("\n--- Similarities ---")
        for doc, dist in raw_results:
            similarity = 1 - dist  # Convert distance to similarity
            print(f"distance={dist:.4f}, similarity={similarity:.4f}")

        """
        #5 Set cosine similarity threshold
        similarities = [1 - dist for _, dist in raw_results]
        #threshold = max(similarities) * 0.2 # keep any document that is at least 20% of the top similarity
        filtered_docs = []
        # Sort similarities descending
        sorted_sims = sorted(similarities, reverse=True)
        # Compute index for top 80%
        cutoff_index = int(len(sorted_sims) * 0.8) #keep top 80%
        # The similarity at that position becomes the threshold
        threshold = sorted_sims[cutoff_index]


        for doc, distance in raw_results:
            similarity = 1 - distance  # Convert distance to similarity
            if similarity >= threshold:
                filtered_docs.append(doc)
        """
        filtered_docs = raw_results

        #Handle no results
        """
        if not filtered_docs:
            print(f"\nNo documents found above similarity threshold {threshold}.")
            continue
        """

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
             "parts": [{"text": "You are a helpful assistant answering questions based only on the provided context. Answer clearly and concisely. If the answer is not in the context, say you don't know."}]
            },
            {"role": "user",
             "parts": [
                 {"text": f"Question: {query}"}
            ]
            }
        ]
        # Add each retrieved document as its own part
        for doc, score in filtered_docs: 
            contents.append({ "role": "user", "parts": [ {"text": doc.page_content} ] })

        #7. Get answer from Gemini
        print("\n--- Answer ---\n")

        config = {
            "temperature":0.2,
            "top_p":1.0,
            "top_k":1,
            "max_output_tokens":2048,}

        model = genai.GenerativeModel(model_name="gemini-2.5-flash", generation_config=config)

        response = model.generate_content(contents)

        print(response.text.strip())


if __name__ == "__main__":
    main()



    

