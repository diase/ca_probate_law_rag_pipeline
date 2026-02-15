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
    url = 'https://courts.ca.gov/cms/rules/index/seven'

    soup = scrape_page(url)

    content_area = soup.find("ul", class_="list__container rule-section")

    if content_area:
        links = [a['href'] for a in content_area.find_all('a', href=True)]
        filtered = [x for x in links if not x.endswith(".pdf")]
        filtered_set = set(filtered)
        print("got links: \n\n")
        for link in filtered_set:
            print(f"{link}\n\n")

        return filtered_set
    else:
        print("couldn't get links")
        return
if __name__ == "__main__":
    main()

    