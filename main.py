#!/usr/bin/env python3

import sys
import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup

from helper import *

parser = argparse.ArgumentParser()
parser.add_argument("word", help="the word that you want to look for.")
parser.add_argument(
	"-p", "--pronunciation", help="gives the link for the pronunciation of the word.", 
	action="store_true"
)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-d", "--declension", help="prints the declension of the word.", action="store_true")
group.add_argument("-c", "--conjugation", help="prints the conjugation of the word.", action="store_true")
args = parser.parse_args()

word = args.word.strip()

if args.declension:
    r = requests.get(f"https://www.verbformen.com/declension/nouns/{word}.htm")
elif args.conjugation:
    r = requests.get(f"https://www.verbformen.de/konjugation/{word}.htm")
else:
    sys.exit(2)

if r.status_code == 429:
    sys.stderr.write("Too many requests, slow  down\n")
    sys.exit(3)

soup = BeautifulSoup(r.text, "html.parser")

if args.declension:
    print(get_name_with_article_dec(soup))
    print(get_declension(soup))
elif args.conjugation:
    name, meaning = get_name_and_meanaing_of_verb_conj(soup)
    if name and meaning:
        print(name)
        print(meaning)
    else:
        sys.exit(4)
    conj_df = get_conjugation(soup)
    if conj_df:
        print(conj_df)
else:
    sys.exit(5)
