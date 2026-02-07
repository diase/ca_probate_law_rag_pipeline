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

    number = "1"
    url = f'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum={number}.'

    soup = scrape_page(url)

    while int(number) < 27100:
        provision_text = "\n".join(p.get_text(strip=True) for p in soup.select("font > p"))

        with open("output.txt", "a", encoding="utf-8") as f:
            if provision_text:
                print("Provision " + number + ":\n" + provision_text, file=f)

        number = str(int(number) + 1)
        url = f'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum={number}.'
        soup = scrape_page(url)