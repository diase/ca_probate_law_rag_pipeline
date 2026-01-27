from json import load
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
#from langchain_ollama import OllamaLLM
#print("Imported Ollama =", OllamaLLM)
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv 

load_dotenv()

def build_context(docs, max_chars=2000):
    #concatenate retrieved docs into single string
    parts = []
    total = 0
    for d in docs:
        text = d.page_content
        if total + len(text) > max_chars:
            text = text[: max_chars - total]
        parts.append(text)
        total += len(text)
        if total >= max_chars:
            break
    return "\n\n---\n\n".join(parts)

def main():
    #1. Embeddings: same as ingestion
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    #2. Load existing Chroma DB
    db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    print("Chroma DB loaded")
    print("Total chunks in DB:", db._collection.count())

    #3. Initialize Ollama LLM
    llm = ChatGoogleGenerativeAI( model="gemini-pro", api_key="AIzaSyCTznmCUyEEAvFm9TTUfNuIqU3RaQcr1_E", temperature=0.2 )
    response = llm.invoke(prompt)

    while True:
        query = input("\nAsk a question (or 'q' to quit): ")
        if query.lower() in {"q", "quit", "exit"}:
            break 

        #4. Retrieve top k results with scores(Cosine Distance)
        raw_results = db.similarity_search_with_score(query, k=10)
        print("\n--- Similarities ---")
        for doc, dist in raw_results:
            similarity = 1 - dist  # Convert distance to similarity
            print(f"distance={dist:.4f}, similarity={similarity:.4f}")
        ##
        #print("\n--- RAW RESULTS ---")
        #for doc, dist in raw_results:
        #    print("Distance:", dist)
        #    print(doc.page_content[:200], "\n")

        #5 Set cosine similarity threshold
        similarities = [1 - dist for _, dist in raw_results]
        threshold = max(similarities) * 0.2 # keep top 80% of relevance
        #threshold = 0.3
        filtered_docs = []

        for doc, distance in raw_results:
            similarity = 1 - distance  # Convert distance to similarity
            if similarity >= threshold:
                filtered_docs.append(doc)

        #filtered_docs = [doc for doc, _ in raw_results]

        #Handle no results
        if not filtered_docs:
            print(f"\nNo documents found above similarity threshold {threshold}.")
            continue

        #6. Build context from retrieved docs
        context = build_context(filtered_docs)

        #7. Build prompt from Llama
        prompt = f"""You are a helpful assistant answering questions based only on the provided context.

        Context:
        {context}

        Question:
        {query}

        Answer clearly and concisely. If the answer is not in the context, say you don't know.
        """

        #8. Get answer from Llama
        print("\n--- Retrieved Context ---\n")
        print(context)
        print("\n--- Answer ---\n")
        answer = llm.invoke(prompt)
        print(answer)

if __name__ == "__main__":
    main()



    

