from importlib.metadata import files
import os
import re
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from chunker import ChunkFiles
import shutil
if os.path.exists("chroma_db"):
    shutil.rmtree("chroma_db")

load_dotenv()

def main():
    #1Chunk Files
    chunking_program = ChunkFiles()
    files = chunking_program.chunk_files()
    documents = [Document(page_content=file['text'], 
                          metadata={"source": file['path'], 
                                    "heading": file['heading']}) for file in files]
    #2 Embed and Store in DB
    print("Embedding and Storing in DB")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma.from_documents(documents, embeddings, persist_directory="chroma_db")
    
    print(f"Verified metadata for first chunk: {documents[0].metadata}")
    print("Ingestion complete")

if __name__ == "__main__":
    main()