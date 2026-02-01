from callable_retrieval import RetrievalPipeline

retrieval_pipeline = RetrievalPipeline()

retrieval_pipeline.main() #loads existing embeddings and chroma db

queries = []

for q in queries:
    retrieval_pipeline.ask_questions(q) #initalizes Gemini, retrieves chunks from chroma, 
                                        #filters and prints, prints gemini's response
