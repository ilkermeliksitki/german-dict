#!/usr/bin/env python3

import sys
import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup

from db import *
from helper import *
from config import *
from init_db import initialize_database

BLUE   = "\033[1;34m"
RED    = "\033[1;31m"
GREEN  = "\033[1;32m"
ITALIC = "\033[3m"
RESET  = "\033[0m"

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
    print(definition_id, type_id)
    # add word to the database
    gender_id = None
    if word_type == 'verb':
        print('conjugations is adding...')
        print(parse_conjugation(soup))
    elif word_type == 'noun':
        gender_id = get_gender_id(gender)
        print('declension is adding...')
        print(parse_declension(soup))
    elif word_type == 'adjective':
        pass

    add_word_to_database((word, gender_id, auxiliary, regular, separable, definition_id, type_id))
    print(parse_word_descriptors(soup))
    pass
else:
    print('print word from database')

if args.declension:
    pass
elif args.conjugation:
    pass
elif args.word:
    pass
else:
    sys.exit(2)





