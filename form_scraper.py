import requests
from bs4 import BeautifulSoup
import forms_link_scraper

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
    #Make list of dicts with source, header, body
    to_return = []

    links = forms_link_scraper.main()
    for link in links:
        form_dict = {}

        url = f"https://selfhelp.courts.ca.gov/{link}"

        form_dict["source"] = url

        soup = scrape_page(url)

        #Header: jcc-hero__title h1 tag
        header_tag = soup.find("h1", class_="jcc-hero__title") 
        header_text = header_tag.get_text(strip=True) if header_tag else None 
        
        #Body: jcc-hero__lead under div tag
        body_tag = soup.find("div", class_="jcc-hero__lead")
        body_text = body_tag.get_text(strip=True) if body_tag else None
        
        if header_text != None and body_text != None:
            form_dict["header"] = header_text
            form_dict["body"] = body_text
            to_return.append(form_dict)
    
    print(f"Created list of {len(to_return)} dictionaries\n\n")
    for i in to_return:
        print(f"\n\n{i}")
    print(f"Final dict: {to_return[len(to_return) - 1]}")
    return to_return
    
if __name__ == "__main__":
    main()