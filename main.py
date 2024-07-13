#!/home/melik/Documents/projects/german-dict/venv/bin/python
import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup

from db import *
from helper import *
from config import *
from init_db import initialize_database
from escape_sequences import *
from ai import *

GERMAN_DICT_DIR = os.environ.get("GERMAN_DICT_DIR")
os.chdir(GERMAN_DICT_DIR)

# configuration
if not is_database_initialized():
    initialize_database()
    set_database_initialized()

# argument parser - cli tool
parser = argparse.ArgumentParser()
parser.add_argument("word", help="the word that you want to look for.")
parser.add_argument("-p", "--pronunciation", help="gives the link for the pronunciation of the word.", action="store_true")
group = parser.add_mutually_exclusive_group()
group.add_argument("-d", "--declension", help="prints the declension of the word.", action="store_true")
group.add_argument("-c", "--conjugation", help="prints the conjugation of the word.", action="store_true")
group.add_argument("-s", "--sentence", help="prints example sentences.", action="store_true")
parser.add_argument("-r", "--replace", help="replaces the example sentences.", action="store_true")
args = parser.parse_args()

word = args.word.strip()

if not check_word_exists(word):
    r = requests.get(f"https://www.verbformen.com/?w={word}")
    if r.status_code == 429:
        sys.stderr.write("Too many requests, slow  down\n")
        sys.exit(3)

    # cook the soup
    soup = BeautifulSoup(r.text, "html.parser")

    # parse word descriptors
    word, word_type, gender, regular, auxiliary, separable = parse_word_descriptors(soup)

    # get definition, definition_id and type_id based on parsed descriptors
    definition = parse_definition(soup)
    definition_id = add_definition_to_database(definition)
    type_id = get_type_id(word_type)

    # add word to the database
    gender_id = None
    if word_type == 'verb':
        add_word_to_database((word, gender_id, auxiliary, regular, separable, definition_id, type_id, 0, 1))
        word_id = get_word_id(word)

        # conjugation part
        conjugation_dict = parse_conjugation(soup)
        add_conjugation_to_db(conjugation_dict, word_id)

        # initial sentences part
        openai_response = get_openai_response(word)
        parsed_sentences = parse_openai_response(openai_response)
        add_sentences_to_db(parsed_sentences, word_id)
    elif word_type == 'noun':
        gender_id = get_gender_id(gender)
        add_word_to_database((word, gender_id, auxiliary, regular, separable, definition_id, type_id, 1, 0))
    elif word_type == 'adjective':
        add_word_to_database((word, gender_id, auxiliary, regular, separable, definition_id, type_id, 1, 0))
    else:
        print('unknown word type')

    #print(parse_word_descriptors(soup))

if args.declension:
    print('declension have not been implemented yet.')
    sys.exit(3)
elif args.conjugation:
    tense_id_str =  '1 = present\n2 = imperfect\n3 = imperative\n4 = present subj.\n'
    tense_id_str += '5 = imperf. subj.\n6 = infinitive\n7 = participle\n'
    tense_id_str += 'Enter the desired id: '
    tense_id = int(input(tense_id_str))
    # print the conjugation
    print_conjugation_of_verb(args.word, tense_id)
elif args.sentence:
    word_id = get_word_id(word)
    if args.replace:
        # initial sentences part
        openai_response = get_openai_response(word)
        parsed_sentences = parse_openai_response(openai_response)
        add_sentences_to_db(parsed_sentences, word_id, replace=True)
    print_sentences_from_db(word_id)
elif args.word:
    word_id = get_word_id(word)
    definition_id = get_definition_id(word)
    definition = get_definition(definition_id)
    print(BLUE + word + RESET)
    print(RED + definition + RESET)
else:
    sys.exit(2)

  



