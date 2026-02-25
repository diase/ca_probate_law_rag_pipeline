import requests
from bs4 import BeautifulSoup
import rules_links_scraper
import json

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

    links = rules_links_scraper.main()
    for link in links:
        rule_dict = {}

        url = f"https://courts.ca.gov/{link}"

        rule_dict["source"] = url

        soup = scrape_page(url)

        #Header:
        header_tag = soup.find("h1", class_="hangover__title stack__sm-space") 
        header_text = header_tag.get_text(strip=True) if header_tag else None 
        
        #Body:
        body_tag = soup.find("div", class_="box roc__rule__content")
        body_text = body_tag.get_text(strip=True) if body_tag else None
        
        if header_text != None and body_text != None:
            rule_dict["header"] = header_text
            rule_dict["body"] = body_text
            to_return.append(rule_dict)
    
    print(f"Created list of {len(to_return)} dictionaries\n\n")
    for i in to_return:
        print(f"\n\n{i}")
    #print(f"Final dict: {to_return[len(to_return) - 1]}")
    #return to_return
    with open("rule_docs/dicts", "w") as f:
        json.dump(to_return, f)

    
if __name__ == "__main__":
    main()
