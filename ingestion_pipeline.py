import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
#from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from webscraper import download_site

#remove this
import shutil
if os.path.exists("chroma_db"):
    shutil.rmtree("chroma_db")

load_dotenv()

def main():
    #Download Wikipedia Pages
    print("Downloading file")
    download_site()#

    #1 Load Files
    print("Loading Files")
    from functools import partial 
    loader = DirectoryLoader( "docs/", glob="*.txt", loader_cls=partial(TextLoader, encoding="utf-8") )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents.")

    #2 Chunk Files
    print("Chunking Files")
    #splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200,
                                             separators=["\n\n", "\n", ".", " ", ""])
    chunks = splitter.split_documents(documents)
    print("Chunking complete")

    #3 Embed and Store in DB
    print("Embedding and Storing in DB")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma.from_documents(chunks, embeddings, persist_directory="chroma_db")
    

    print("Ingestion complete")

if __name__ == "__main__":
    main()