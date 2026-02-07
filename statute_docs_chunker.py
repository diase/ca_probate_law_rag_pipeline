import re

def main():
    #chunking output.txt
    with open("statute_docs/output.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # Split on "Provision X:" but keep the header
    parts = re.split(r"(Provision\s+\d+:)", text)
    
    #to_print = parts[0:10]
    #for part in to_print:
    #    print(f"PART: \n{part} \n\n")
    #print(f"Total parts: {len(parts)}\n\n")
    #print(f"Last part: {parts[-1]}")
    return parts

if __name__ == "__main__":
    main()