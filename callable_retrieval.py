import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import google.generativeai as genai
from dotenv import load_dotenv 

load_dotenv()

class RetrievalPipeline:
    def __init__(self):
        pass

    def main(self):
        #1. Embeddings: same as ingestion
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        #2. Load existing Chroma DBs
        self.statute_db = Chroma(persist_directory="statute_db", embedding_function = embeddings)
        self.self_help_db = Chroma(persist_directory="self_help_db", embedding_function = embeddings)
        self.rule_db = Chroma(persist_directory="rule_db", embedding_function = embeddings)
        self.form_db = Chroma(persist_directory="form_db", embedding_function = embeddings)
        print("Chroma DBs loaded")

    def ask_questions(self, question):
        #1. Initialize Gemini LLM
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        print("Gemini LLM initialized")

        print(f"Your Question: {question}")
        
        query = question
        if query.lower() in {"q", "quit", "exit"}:
            return
        
        #2. Route to correct db
        form_keywords = ["form", "file", "submit", "attach", "de-", "de -", "ge-", "ge -", "app-", "app -", "jv-", "jv -"]
        rule_keywords = ["notice", "deadline", "hearing", "inventory", "petition", "time limit"]
        statute_keywords = ["inherit", "liable", "duty", "power"]
        self_help_keywords = ["what is", "when is", "explain", "overview", "basics", "summary", "summarize"]

        if any(w in query.lower() for w in form_keywords):
            self.db = self.form_db
        elif any(w in query.lower() for w in rule_keywords):
            self.db = self.rule_db
        elif any(w in query.lower() for w in statute_keywords):
            self.db = self.statute_db
        elif any(w in query.lower() for w in self_help_keywords):
            self.db = self.self_help_db
        else:
            self.db = self.statute_db

        #3. Retrieve top k results with scores(Cosine Distance)
        raw_results = self.db.similarity_search_with_score(query, k=10)
        print("\n--- Similarities ---")
        for doc, dist in raw_results:
            similarity = 1 - dist  # Convert distance to similarity
            print(f"distance={dist:.4f}, similarity={similarity:.4f}")

        
        #4 Set cosine similarity threshold
        similarities = [1 - dist for _, dist in raw_results]
        #threshold = max(similarities) * 0.2 # keep any document that is at least 20% of the top similarity
        filtered_docs = []
        # Sort similarities descending
        sorted_sims = sorted(similarities, reverse=True)
        # Compute index for top 80%
        cutoff_index = int(len(sorted_sims) * 0.5) #keep top 50%
        # The similarity at that position becomes the threshold
        threshold = sorted_sims[cutoff_index]


        for doc, distance in raw_results:
            similarity = 1 - distance  # Convert distance to similarity
            if similarity >= threshold:
                filtered_docs.append((doc, distance))

        #Handle no results(Currently useless as we keep 50%)
        
        if not filtered_docs:
            print(f"\nNo documents found above similarity threshold {threshold}.")
            return
        

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
             "parts": [{"text": "You are a helpful assistant answering questions based only on the provided context. Answer clearly and concisely. If the answer is not in the context, say you don't know."},
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





    

