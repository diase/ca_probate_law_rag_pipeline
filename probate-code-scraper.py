import requests 
from bs4 import BeautifulSoup

def scrape_page(url):
    # Send HTTP request
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # raises error for 4xx/5xx

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    return soup


if __name__ == "__main__":
    url = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PROB&sectionNum=4."
    soup = scrape_page(url)

    # Example: print page title
    print(soup.title.text)