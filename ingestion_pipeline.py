from importlib import metadata
import os
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

    #1 Chunk Files
    print("Chunking Files")

    #chunking output.txt
    with open("docs/output.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # Split on "Provision X:" but keep the header
    parts = re.split(r"(Provision\s+\d+:)", text)

    documents = []

    for i in range(1, len(parts), 2):
        header = parts[i]
        body = parts[i+1].strip()
        full_text = f"{header}\n{body}"
        documents.append(Document(page_content=full_text, metadata={"source":"https://leginfo.legislature.ca.gov/faces/codesTOCSelected.xhtml?tocCode=PROB&tocTitle=+Probate+Code+-+PROB"}))
    
    #chunking self_help_formal_probate.txt
    with open("docs/self_help_formal_probate.txt", "r", encoding="utf-8") as f:
        text = f.read()

    #Split on #
    parts = re.split(r"(^#+\s+.*)", text, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip()
            body = parts[i+1].strip()
        
            if not body: continue # Skip headers with no text
            
            full_text = f"{header}\n{body}"
        
            documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "source": "https://selfhelp.courts.ca.gov/probate/formal-probate"
                    }
                )
            )

    #chunking self_help_guardianship.txt
    with open("docs/self_help_guardianship.txt", "r", encoding="utf-8") as f:
        text = f.read()

    #Split on #
    parts = re.split(r"(^#+\s+.*)", text, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip()
            body = parts[i+1].strip()
        
            if not body: continue # Skip headers with no text
            
            full_text = f"{header}\n{body}"
        
            documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "source": "https://selfhelp.courts.ca.gov/guardianship"
                    }
                )
            )

    #chunking self_help_impairment.txt
    with open("docs/self_help_impairment.txt", "r", encoding="utf-8") as f:
        text = f.read()

    #Split on #
    parts = re.split(r"(^#+\s+.*)", text, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip()
            body = parts[i+1].strip()
        
            if not body: continue # Skip headers with no text
            
            full_text = f"{header}\n{body}"
        
            documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "source": "https://selfhelp.courts.ca.gov/helping-person-impairment-or-disability"
                    }
                )
            )

    #chunking self_help_inventory.txt
    with open("docs/self_help_inventory.txt", "r", encoding="utf-8") as f:
        text = f.read()

    #Split on #
    parts = re.split(r"(^#+\s+.*)", text, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip()
            body = parts[i+1].strip()
        
            if not body: continue # Skip headers with no text
            
            full_text = f"{header}\n{body}"
        
            documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "source": "https://selfhelp.courts.ca.gov/probate/inventory-estimate-value"
                    }
                )
            )

    #chunking self_help_probate.txt
    with open("docs/self_help_probate.txt", "r", encoding="utf-8") as f:
        text = f.read()

    #Split on #
    parts = re.split(r"(^#+\s+.*)", text, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip()
            body = parts[i+1].strip()
        
            if not body: continue # Skip headers with no text
            
            full_text = f"{header}\n{body}"
        
            documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "source": "https://selfhelp.courts.ca.gov/probate"
                    }
                )
            )

    #chunking self_help_simple_process.txt
    with open("docs/self_help_simple_process.txt", "r", encoding="utf-8") as f:
        text = f.read()

    #Split on #
    parts = re.split(r"(^#+\s+.*)", text, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip()
            body = parts[i+1].strip()
        
            if not body: continue # Skip headers with no text
            
            full_text = f"{header}\n{body}"
        
            documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "source": "https://selfhelp.courts.ca.gov/probate/simple-transfer"
                    }
                )
            )

    #chunking self_help_small_estate3.txt
    with open("docs/self_help_small_estate3.txt", "r", encoding="utf-8") as f:
        text = f.read()

    #Split on #
    parts = re.split(r"(^#+\s+.*)", text, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip()
            body = parts[i+1].strip()
        
            if not body: continue # Skip headers with no text
            
            full_text = f"{header}\n{body}"
        
            documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "source": "https://selfhelp.courts.ca.gov/probate/small-estate"
                    }
                )
            )

    #chunking self_help_terms.txt
    with open("docs/self_help_terms.txt", "r", encoding="utf-8") as f:
        text = f.read()

    #Split on #
    parts = re.split(r"(^#+\s+.*)", text, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip()
            body = parts[i+1].strip()
        
            if not body: continue # Skip headers with no text
            
            full_text = f"{header}\n{body}"
        
            documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "source": "https://selfhelp.courts.ca.gov/probate/terms"
                    }
                )
            )

    #chunking self_help_wills.txt
    with open("docs/self_help_wills.txt", "r", encoding="utf-8") as f:
        text = f.read()

    #Split on #
    parts = re.split(r"(^#+\s+.*)", text, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip()
            body = parts[i+1].strip()
        
            if not body: continue # Skip headers with no text
            
            full_text = f"{header}\n{body}"
        
            documents.append(
                Document(
                    page_content=full_text,
                    metadata={
                        "source": "https://selfhelp.courts.ca.gov/wills-estates-probate/legal-documents"
                    }
                )
            )
    
    print("Chunking complete")

    #2 Embed and Store in DB
    print("Embedding and Storing in DB")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma.from_documents(documents, embeddings, persist_directory="chroma_db")
    

    print("Ingestion complete")

if __name__ == "__main__":
    main()