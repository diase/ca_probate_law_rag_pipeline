from pydoc import text
from bs4 import BeautifulSoup

def scrape_local_file(filepath):
    try:
        # We strip 'file:///' if it's still in the string
        clean_path = filepath.replace('file:///', '')
        
        with open(clean_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        return BeautifulSoup(html_content, "html.parser")
    except Exception as e:
        print(f"Error opening file: {e}")
        return None

def main():
    url = 'file:///C:/Users/ericl/OneDrive/Documents/probate_sites/self_help_small_estate.htm'
    soup = scrape_local_file(url)

    # 1. Find the main content area
    content_area = soup.find("div", class_="page__content") or soup.find("main")

    if not content_area:
        print("Failed to find main content area.")
        return

    extracted = []

    # 2. Find all relevant tags anywhere inside the content area
    # But we will use a set to keep track of what we've already processed
    processed_texts = set()

    for tag in content_area.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        # Skip if this tag is inside another tag we are already processing 
        # (e.g., skip a <p> if it's inside an <li>)
        if tag.find_parent(["p", "li"]):
            continue

        text = tag.get_text(strip=True)
        if not text:
            continue

        if tag.name.startswith("h"):
            level = int(tag.name[1])
            extracted.append(f"{'#' * level} {text}")
        elif tag.name == "li":
            extracted.append(f"* {text}")
        else:
            extracted.append(text)

    # Join and save
    final_output = "\n\n".join(extracted)
    
    with open("docs/self_help_small_estate3.txt", "w", encoding="utf-8") as f:
        f.write(final_output)
    
    print("Done! Check docs/self_help_small_estate3.txt") 

if __name__ == "__main__":
    main()
