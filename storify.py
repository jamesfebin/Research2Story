import os
import re
import sys
import random
import openai
import requests
from PyPDF2 import PdfReader
import string
import argparse

openai.api_key = os.getenv("OPENAI_API_KEY")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


parser = argparse.ArgumentParser(
                    prog='Research2Story',
                    description='Convert Research Papers into Hilarious Novels with ChatGPT',
                    epilog='')

parser.add_argument('-u', '--url', required=True, help='URL of the research paper')
parser.add_argument('-f', '--fiction', required=True, help='Name of the fiction character')

args = parser.parse_args()

url = args.url
fiction = args.fiction

if url is None or fiction is None:
    print("Please provide both url and fiction parameters")
    exit()

print("Downloading the paper ...")
response = requests.get(url)
filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
pdf_file = open('./papers/{}.pdf'.format(filename), 'wb')
pdf_file.write(response.content)
pdf_file.close()
pdf_reader = PdfReader('./papers/{}.pdf'.format(filename))
text = ''

clear()
print("Extracting content ...")
for page_num in range(len(pdf_reader.pages)):
    page = pdf_reader.pages[page_num]    
    page_content = page.extract_text()
    text += page_content

abstract_regex = re.compile(r'(?<=Abstract\n\n)(.*?)(?=\n\n)')
section_regex = re.compile(r'\n\d+\. (.+?)\n')
text = text.split('Acknowledgements')[0]
text = text.split('Abstract')[1]
heading_pattern = re.compile(r'^\d+\.?\s')

sections = []
current_section = ''
for line in text.split('\n'):
    if heading_pattern.match(line):
        sections.append(current_section.strip())
        current_section = line + '\n'
    else:
        current_section += line + '\n'
sections.append(current_section.strip())

def split_paragraphs(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    paragraphs = []
    current_paragraph = ""
    for sentence in sentences:
        if len(current_paragraph) + len(sentence) > 1000:
            paragraphs.append(current_paragraph.strip())
            current_paragraph = sentence
        else:
            current_paragraph += sentence + " "
    paragraphs.append(current_paragraph.strip())

    return paragraphs

narration_paragraphs = []
for index, section in enumerate(sections):
        clear()
        print("Processing section: {} of {}".format(index, len(sections)))
        paragraphs = split_paragraphs(section)
        story_response = ''
        for (para_index, paragraph) in enumerate(paragraphs):
            print("Processing paragraph: {} of {}".format(para_index, len(paragraphs)))
            response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": "Rewrite the following section in simple words and in conversational style with characters from {} \n\n {}".format(fiction, paragraph)},
                        ]
                    )
            story_response = story_response + response['choices'][0]['message']['content']
        narration_paragraphs.append(story_response)
    
        
with open('stories/{}_story.txt'.format(filename), 'w') as txt_file:
    for paragraph in narration_paragraphs:
        paragraph += '\n\n'
        txt_file.write(paragraph)
clear()
print("Done")
    
