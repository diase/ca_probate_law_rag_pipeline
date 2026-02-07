import re
import os

def main():
    #create list of dictionaries to store source_url, and parts
    to_return = []
    for f in os.listdir("self_help_docs"):
        
        if f=="self_help_formal_probate.txt":
            source = "https://selfhelp.courts.ca.gov/probate/formal-probate"
        if f == "self_help_guardianship.txt":
            source = "https://selfhelp.courts.ca.gov/guardianship"
        if f == "self_help_impairment.txt":
            source = "https://selfhelp.courts.ca.gov/helping-person-impairment-or-disability"
        if f == "self_help_inventory.txt":
            source = "https://selfhelp.courts.ca.gov/probate/inventory-estimate-value"
        if f == "self_help_probate.txt":
            source = "https://selfhelp.courts.ca.gov/probate"
        if f == "self_help_simple_process.txt":
            source = "https://selfhelp.courts.ca.gov/probate/simple-transfer"
        if f == "self_help_small_estate3.txt":
            source = "https://selfhelp.courts.ca.gov/probate/small-estate"
        if f == "self_help_terms.txt":
            source = "https://selfhelp.courts.ca.gov/probate/terms"
        if f == "self_help_wills.txt":
            source = "https://selfhelp.courts.ca.gov/wills-estates-probate/legal-documents"

        #create dictionary
        dict = {"source": source, "parts": []}

        #read file, add parts to dictionary
        file_name = "self_help_docs/" + f
        with open(file_name, "r", encoding = "utf-8") as file:
            text = file.read()
        parts = re.split(r"(^#+\s+.*)", text, flags=re.MULTILINE)
        dict["parts"] = parts

        #append dict to to_return
        to_return.append(dict)


    #return list of dictionaries
    #print(f"Created {len(to_return)} dictionaries\n\nFirst Dictionary: {to_return[0]}")
    return to_return
    
if __name__ == "__main__":
    main()