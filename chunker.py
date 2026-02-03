import os
from dotenv import load_dotenv
load_dotenv()
from pypdf import PdfReader
from docx import Document
from bs4 import BeautifulSoup

class ChunkFiles():

    def __init__(self):
        pass

    def main(self):
        print("Chunking files...")

    def chunk_files(self) -> list:
        #search for .doc files. say to convert to .docx
        for f in os.listdir("raw_docs"):
            count = 0;
            if f.lower().endswith(".doc"):
                count += 1
                print(f"Found {count} files of type .doc. Please convert these to .docx for processing.")

        #create separate lists for different file types
        pdf_paths = [os.path.join("raw_docs", f) for f in os.listdir("raw_docs") if f.lower().endswith(".pdf")]
        docx_paths = [os.path.join("raw_docs", f) for f in os.listdir("raw_docs") if f.lower().endswith(".docx")]
        web_paths = [os.path.join("raw_docs", f) for f in os.listdir("raw_docs") if f.lower().endswith(".html") or f.lower().endswith(".htm")]

        #each item is dict with keys: path, heading, text 
        files = []

        for path in pdf_paths:
            files.extend(self.extract_pdf(path))
        for path in docx_paths:
            files.extend(self.extract_docx(path))
        for path in web_paths:
            files.extend(self.extract_web(path))
        print(f"Extracted {len(files)} files.")

        return files

    def extract_pdf(path):
        reader = PdfReader(path)
        results = []

        current_heading = None

        for page_num, page in enumerate(reader.pages):
            raw = page.extract_text()
            if not raw:
                continue

            # Split into paragraphs (double newline is the most reliable)
            paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]

            for para in paragraphs:
                # Simple heuristic: treat short, all‑caps, or colon‑ending lines as headings
                if (
                    para.isupper() or
                    len(para) < 60 or
                    para.endswith(":")
                ):
                    current_heading = para
                    continue

                results.append({
                    "path": path,
                    "heading": current_heading,
                    "text": para
            })

        return results

    def extract_docx(path): 
        doc = Document(path) 
        results = [] 
        current_heading = None 
        for para in doc.paragraphs: 
            text = para.text.strip() 
            if not text: continue 
            # Detect headings using Word's built‑in style info 
            if para.style.name.startswith("Heading"): 
                current_heading = text 
                continue 
            # Fallback heuristic for documents without proper heading styles 
            if ( text.isupper() or len(text) < 60 or text.endswith(":") ): 
                current_heading = text 
                continue 
            results.append({ 
                "path": path,  
                "heading": current_heading, 
                "text": text }) 
        return results

    def extract_web(path): 
        with open(path, "r", encoding="utf-8") as f: 
            html = f.read() 
        soup = BeautifulSoup(html, "html.parser") 
        results = [] 
        current_heading = None 
        # Tags that should never be treated as content 
        skip_tags = { "script", "style", "nav", "footer", "header", "noscript", "svg", "img" } 
        # Choose a main content area if present 
        container = ( soup.find("main") or soup.find("article") or soup.find("body") or soup ) 
        for tag in container.descendants: 
            if tag.name is None: 
                continue 
            if tag.name in skip_tags: 
                continue 
            # Headings 
            if tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]: 
                text = tag.get_text(strip=True) 
                if text: 
                    current_heading = text 
                continue 
            # Any tag with visible text 
            text = tag.get_text(strip=True) 
            if not text: 
                continue 
            # Avoid capturing headings twice 
            if text == current_heading: 
                continue 
            # Avoid capturing parent text repeatedly 
            if len(tag.find_all(recursive=False)) > 0: 
                # If the tag has children, skip unless it's a known content tag 
                if tag.name not in ["p", "li", "div", "section", "article", "td", "blockquote"]: 
                    continue 
            results.append({ "path": path, "heading": current_heading, "text": text }) 
        return results


