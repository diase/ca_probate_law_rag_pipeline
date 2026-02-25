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
    url = 'https://selfhelp.courts.ca.gov/find-forms?query=probate'

    soup = scrape_page(url)

    content_area = soup.find("div", class_="jcc-find-forms__results")

    if content_area:
        links = [a['href'] for a in content_area.find_all('a', href=True)]
        filtered = [x for x in links if not x.endswith(".pdf")]
        filtered_set = set(filtered)
        print("got links")
        return filtered_set
    else:
        print("couldn't get links")
        return
if __name__ == "__main__":
    main()

    
