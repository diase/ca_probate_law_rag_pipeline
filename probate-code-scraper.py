import requests 
import re
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

if __name__ == "__main__":

    code = "1"
    url = f'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum={code}.'

    soup = scrape_page(url)

    while int(code) < 27100:
        match = re.search(fr'(?:.*){code}\. \s*(.*)', soup.text, re.DOTALL)
        if match:
            code_text = match.group(1).strip()
            #print("Section number:", code)
            #print("Text:", code_text)

            with open("output.txt", "a", encoding="utf-8") as f:
                print(code + ": " + code_text, file=f)

        code = str(int(code) + 1)
        url = f'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum={code}.'
        soup = scrape_page(url)