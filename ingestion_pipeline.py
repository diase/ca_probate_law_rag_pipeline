import os
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import statute_docs_chunker
import self_help_docs_chunker
#import rule_docs_chunker
import json
import shutil

if os.path.exists("statute_db"):
    shutil.rmtree("statute_db")
if os.path.exists("self_help_db"):
    shutil.rmtree("self_help_db")
if os.path.exists("rule_db"):
    shutil.rmtree("rule_db")
if os.path.exists("form_db"):
    shutil.rmtree("form_db")

def main():

    #1 Chunk Files
    print("Chunking Statute Files")
    statute_parts = statute_docs_chunker.main()

    statute_documents = []

    for i in range(1, len(statute_parts) - 1, 2):
        header = statute_parts[i]
        body = statute_parts[i+1].strip()
        full_text = f"{header}\n{body}"
        statute_documents.append(Document(page_content=full_text, metadata={"source":"https://leginfo.legislature.ca.gov/faces/codesTOCSelected.xhtml?tocCode=PROB&tocTitle=+Probate+Code+-+PROB{i}"}))
    print(f"Created {len(statute_documents)} statute documents\n\n")
    #print(f"Last Document: {statute_documents[len(statute_documents) - 1].page_content}")
    
    print("Chunking Self_Help Files")

    self_help_dicts = self_help_docs_chunker.main()

    self_help_documents = []

    for i in range(len(self_help_dicts)):
        source = self_help_dicts[i]["source"]
        parts = self_help_dicts[i]["parts"]

        for i in range(1, len(parts) - 1, 2):
            #if i + 1 < len(parts):
            header = parts[i].strip()
            body = parts[i+1].strip()
        
            if not body: continue # Skip headers with no text
            
            full_text = f"{header}\n{body}"
        
            self_help_documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "source": source
                    }
                )
            )
    print(f"Created {len(self_help_documents)} self_help_documents\n\n")
    #print(f"Last Document: {self_help_documents[len(self_help_documents) - 1].page_content}")

    print("Chunking Form Files")

    form_documents = []

    #form_scraper.main()

    with open("form_docs/dicts", "r") as f:
        form_dicts = json.load(f)

    for i in range(len(form_dicts)):
        header = form_dicts[i]["header"]
        body = form_dicts[i]["body"]
        source = form_dicts[i]["source"]

        full_text = f"{header}\n{body}"

        form_documents.append(
            Document(
                page_content=full_text,
                metadata={
                    "source":source
                    }
                )
            )

    print(f"Created {len(form_documents)} form_documents\n\n")
    print(f"Last Form doc: {form_documents[len(form_documents) - 1].page_content}")

    return

    print("Chunking Rule Files")
    
    print("Chunking complete")

    #2 Embed and Store in DB
    """
    statute_db: corresponds to CA Probate Code
    self_help_db: corresponds to CA Courts Self Help Website Probate Section
    rule_db: corresponds to CA Rules of Court
    form_db: corresponds to CA Judicial Council Forms
    """
    print("Embedding and Storing in DB")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    statute_db = Chroma.from_documents(statute_documents, embeddings, persist_directory="statute_db")
    self_help_db = Chroma.from_documents(self_help_documents, embeddings, persist_directory="self_help_db")
    rule_db = Chroma.from_documents(rule_documents, embeddings, persist_directory="rule_db")
    form_db = Chroma.from_documents(form_documents, embeddings, persist_directory="form_db")
    
    #print(f"Verified metadata for first chunk: {documents[0].metadata}")
    print("Ingestion complete")

if __name__ == "__main__":
    main()