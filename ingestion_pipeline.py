import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
import re
#from langchain.schema import Document
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

import shutil
if os.path.exists("chroma_db"):
    shutil.rmtree("chroma_db")

load_dotenv()

def main():

    #1 Load File
    print("Loading File")
    from functools import partial 
    loader = DirectoryLoader( "docs/", glob="*.txt", loader_cls=partial(TextLoader, encoding="utf-8") )
    document = loader.load()
    print(f"Loaded {len(document)} document.")

    #2 Chunk Files
    print("Chunking File")
    with open("docs/output.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # Split on "Provision X:" but keep the header
    parts = re.split(r"(Provision\s+\d+:)", text)

    documents = []

    for i in range(1, len(parts), 2):
        header = parts[i]
        body = parts[i+1].strip()
        full_text = f"{header}\n{body}"
        documents.append(Document(page_content=full_text))
    
    print("Chunking complete")

    #3 Embed and Store in DB
    print("Embedding and Storing in DB")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma.from_documents(documents, embeddings, persist_directory="chroma_db")
    

    print("Ingestion complete")

if __name__ == "__main__":
    main()