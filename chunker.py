import os
from dotenv import load_dotenv
load_dotenv()
import subprocess
import tempfile
import pdf_extractor
import pytesseract
from pdf2image import convert_from_path
from docx import Document
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import re

class ChunkFiles():

    def __init__(self, folder_name):
        self.folder = folder_name

    def main(self):
        print("Chunking files...")

    def chunk_files(self) -> list:
        #search for .doc files. say to convert to .docx
        for root, dirs, files in os.walk(self.folder):
            for name in files:
                if name.lower().endswith(self.folder):
                    print(f"Found .doc file: {os.path.join(root, name)}. Please convert this to .docx for processing.")

        #create lists to store file paths for pdfs, docx, and web files respectively
        pdf_paths = []
        docx_paths = []
        web_paths = []
        for root, dirs, files in os.walk(self.folder):
            for name in files:
                full_path = os.path.join(root, name)
                if name.lower().endswith(".pdf"):
                    pdf_paths.append(full_path)
                elif name.lower().endswith(".docx"):
                    docx_paths.append(full_path)
                elif name.lower().endswith(".html") or name.lower().endswith(".htm"):
                    web_paths.append(full_path)

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
    
    def extract_pdf(self, path):
        text = pdf_extractor.main(path)
        if text and len(text.strip()) < 50:
            text = self.extract_with_pdftotext(path)
            if not text or not text.strip():
                text = self.extract_with_ocr(path)
                if text == "":
                    print(f"Could not extract text from PDF: {path}")
                    return []
        
        #call to Gemini
        results = self.create_results_from_gemini(path, text)
        return results

    def create_results_from_gemini(self, path, text):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        print("Gemini API Key Configured")
        contents = [ { "role": "user", 
                      "parts": [ { "text": ( "You are a document chunker. Extract headings and the text under each heading. " "Return ONLY valid JSON. Format:\n\n" "[\n" " {\"heading\": \"...\", \"text\": \"...\"},\n" " ...\n" "]\n\n" "Do NOT include markdown fences or explanations." ) },
                               {"text": f"Document text: {text}"} ] } ]
        model = genai.GenerativeModel(model_name="gemini-2.5-flash") 
        response = model.generate_content(contents)
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        try: data = json.loads(raw) 
        except Exception: 
            print("Gemini returned invalid JSON, attempting repair") 
            raw = self.repair_json(raw) 
            data = json.loads(raw)

        results = [] 
        for item in data: 
            results.append({ "path": path, "heading": item.get("heading"), "text": item.get("text") }) 
        return results

    def repair_json(self, text):  
        text = re.sub(r"```json|```", "", text) 
        text = text.replace("\n", " ") 
        return text

    def extract_with_pdftotext(self, path):
        """
        Uses the system pdftotext command.
        Returns plain text.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp_path = tmp.name

        try:
            subprocess.run(
                ["pdftotext", "-layout", path, tmp_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def extract_with_ocr(self, path):
       
        try:
            pages = convert_from_path(path, dpi=300)
        except Exception as e:
            print(f"[ERROR] Failed to convert PDF to images for OCR: {e}")
            return ""

        ocr_texts = []

        for i, page in enumerate(pages):
            try:
                text = pytesseract.image_to_string(page)
                if text.strip():
                    ocr_texts.append(text)
            except Exception as e:
                print(f"[WARN] OCR failed on page {i}: {e}")
                return ""

        return "\n\n=== OCR PAGE BREAK ===\n\n".join(ocr_texts)


    def extract_docx(self, path): 
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
        for table in doc.tables: 
            for row in table.rows: 
                # Extract each cell's text 
                cells = [cell.text.strip() for cell in row.cells if cell.text.strip()] 
                if not cells: 
                    continue 
                # Join cells with a separator 
                row_text = " | ".join(cells) 
                results.append({ "path": path, "heading": current_heading, "text": row_text }) 

        return results
    #POSSIBLY KEEP IMAGES
    def extract_web(self, path): 
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


