import sys
import os
import retrieval_pipeline_baseline
from io import StringIO
from unittest.mock import patch

#Helper function to read in questions from the questions document
def retrieve_questions_doc():
    with open("test_questions.txt", 'r') as f:
        return f.readlines()

#Helper function for changing the title when necessary
def change_title(title, line):
    current_title = title
    if line.startswith("@@@"):
        current_title = "Form-related"
    elif line.startswith("$$$"):
        current_title = "Rule-related" 
    elif line.startswith('###'):
        current_title = "Self Help"
    elif line.startswith("&&&"):
        current_title = "Statute-related"
    return current_title

#Helper function to parse the questions document into a list of questions
def parse_questions_doc(questions_doc):
    questions_list = []
    section = []
    old_title = ""
    title = ""
    for line in questions_doc:
        #changes title at the start of each new section
        old_title = title
        title = change_title(title, line)
        #print(f"Current title: {title}, Old title: {old_title}, Line: {line.strip()}")
        if title == old_title:
            section.append(line.strip())
        elif old_title == "":
            continue
        else:
            questions_list.append(section)
            section = []
    questions_list.append(section) #appends the last section
    return questions_list

def main():
    questions_doc = retrieve_questions_doc()
    questions_list = parse_questions_doc(questions_doc)
    #print(questions_list)

    with patch('builtins.input', side_effect=[item for sublist in questions_list for item in sublist]):
        with patch('sys.stdout', new=StringIO()) as output:
            retrieval_pipeline_baseline.main()
            with open('test_results.txt', 'w') as f:
                f.write(output.getvalue())

if __name__ == "__main__":
    main()