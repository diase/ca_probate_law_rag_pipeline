import requests
from bs4 import BeautifulSoup

def scrape_page(url):
    try: 
        # Send HTTP request
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises error for 4xx/5xx

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        return soup

    except requests.exceptions.RequestException:
        # Handles all network-related errors, including 404, timeout, connection errors
        return False 

def main():
    url = 'https://selfhelp.courts.ca.gov/probate'

    soup = scrape_page(url)

    #only extract headings and paragraphs
    allowed_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p"]

    #create variable to store text
    extracted = []

    for tag in soup.find_all(allowed_tags):

        text = tag.get_text(strip=True)

        if not text:
            continue

        if tag.name.startswith("h"):
            level = int(tag.name[1])#get heading level
            extracted.append(f"{'#' * level} {text}")
        else:
            extracted.append(text)

    #create space between text
    extracted = "\n\n".join(extracted)

    #write to file
    with open("docs/self_help_probate.txt", "a", encoding="utf-8") as f:
        f.write(extracted)  

if __name__ == "__main__":
    main()
