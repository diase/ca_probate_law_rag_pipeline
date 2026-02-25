import re

def main():
    #chunking output.txt
    with open("statute_docs/output.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # Split on "Provision X:" but keep the header
    parts = re.split(r"(Provision\s+\d+:)", text)
    
    return parts

if __name__ == "__main__":
    main()
