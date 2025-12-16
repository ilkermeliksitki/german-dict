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
parser.add_argument("-a", "--openai", help="if openai call is wanted, this should be provided", action="store_true")
args = parser.parse_args()

word = args.word.strip()

# validates if word is already in database or if any fuzzy match exists
found_word = None
# use fuzzy matches to find all variants
matches = get_fuzzy_matches(word) # (id, word)

if matches:
    # check for single exact match to avoid friction
    if len(matches) == 1 and matches[0][1].lower() == word.lower():
        found_word = matches[0][1]
    else:
        # check for haben and sein variants, and show add option accordingly
        has_haben = any('(haben)' in m[1] for m in matches)
        has_sein = any('(sein)' in m[1] for m in matches)
        show_add = not (has_haben and has_sein)

        print(f"\n{BLUE}Found matches:{RESET}")
        for idx, (mid, mword) in enumerate(matches):
            print(f"{idx + 1}: {mword}")

        if show_add:
            print(f"{len(matches) + 1}: Search online / Add new")

        try:
            sel = input(f"\n{BLUE}Select option (default 1): {RESET}")
            if not sel.strip():
                sel_idx = 0
            else:
                sel_idx = int(sel) - 1

            if 0 <= sel_idx < len(matches):
                found_word = matches[sel_idx][1]
            elif show_add and sel_idx == len(matches):
                # user chose to search online
                found_word = None
            else:
                # invalid match choice
                found_word = matches[0][1]
        except ValueError:
            found_word = matches[0][1] # Default to first match on error
else:
    candidates = get_possible_matches(word)
    for cand in candidates:
        matches = get_fuzzy_matches(cand)
        if matches:
            found_word = matches[0][1]
            break


if not found_word:
    try:
        r = requests.get(f"https://www.verbformen.com/?w={word}")
        if r.status_code == 429:
            sys.stderr.write("Too many requests, slow down\n")
            sys.exit(3)

        # cook the soup
        soup = BeautifulSoup(r.text, "html.parser")

        # check for variants (e.g. haben vs sein)
        variants = get_verb_variants(soup)

        selected_label = None
        if len(variants) > 1:
            print(f"\n{BLUE}Multiple conjugation forms found:{RESET}")
            for idx, (label, url) in enumerate(variants):
                print(f"{idx + 1}: {label}")

            try:
                sel = input(f"\n{BLUE}Select form (default 1): {RESET}")
                if not sel.strip():
                    sel_idx = 0
                else:
                    sel_idx = int(sel) - 1

                if 0 <= sel_idx < len(variants):
                    # selected label: sein or haben
                    selected_label, selected_url = variants[sel_idx]
                    sys.stdout.write(f"Fetching {selected_label} form...\n")
                    r = requests.get(selected_url)
                    if r.status_code == 200:
                        soup = BeautifulSoup(r.text, "html.parser")
                    else:
                         sys.stderr.write(f"Failed to fetch variant, using default.\n")
            except ValueError:
                print(f"{RED}Invalid input, using default.{RESET}")

        # parse word descriptors
        scraped_word, word_type, gender, regular, auxiliary, separable = parse_word_descriptors(soup)

        # update word name if a specific variant was selected to distinguish it in db
        if selected_label:
            # e.g. "fliegen" -> "fliegen (sein)" or "fliegen (haben)"
            if '(' not in word: # prevent double tagging if user typed "fliegen (sein)"
                word = f"{scraped_word} ({selected_label})"
        else:
            word = scraped_word

        # get definition, definition_id based on parsed descriptors
        definition = parse_definition(soup)
        definition_id = add_definition_to_database(definition)
        gender_id = None

        # map string descriptors to integers
        aux_map = {'haben': 0, 'sein': 1}
        reg_map = {'regular': 1, 'irregular': 0}

        # map values with default values to prevent crashes
        aux_val = aux_map.get(auxiliary)
        reg_val = reg_map.get(regular, 1)

        if word_type == 'verb':
            # type_id is brought here to prevent crashes when word_type is None
            # same done for noun and adjective as well.
            type_id = get_type_id(word_type)
            add_word_to_database((word, gender_id, aux_val, reg_val, separable, definition_id, type_id, 0, 1))
            word_id = get_word_id(word)

            # conjugation part
            conjugation_dict = parse_conjugation(soup)
            add_conjugation_to_db(conjugation_dict, word_id)

            # initial sentences part
            if args.openai:
                openai_response = get_openai_response(word)
                parsed_sentences = parse_openai_response(openai_response)
                add_sentences_to_db(parsed_sentences, word_id)
        elif word_type == 'noun':
            type_id = get_type_id(word_type)
            gender_id = get_gender_id(gender)
            add_word_to_database((word, gender_id, aux_val, reg_val, separable, definition_id, type_id, 1, 0))

            word_id = get_word_id(word)

            if args.openai:
                openai_response = get_openai_response(word)
                parsed_sentences = parse_openai_response(openai_response)
                add_sentences_to_db(parsed_sentences, word_id)

            # add declension to the database
            declension_dict = parse_declension(soup)
            add_declension_to_db(declension_dict, word_id)

        elif word_type == 'adjective':
            type_id = get_type_id(word_type)
            add_word_to_database((word, gender_id, aux_val, reg_val, separable, definition_id, type_id, 1, 0))
        else:
            print('unknown word type')

    except Exception as e:
        sys.stderr.write(f"An error occurred while fetching information for '{word}': {e}\n")
        sys.exit(1)
else:
    word = found_word

word_type = get_word_type(word)
if args.declension:
    if word_type != 'noun':
        sys.stderr.write("Declension is only available for nouns.\n")
        sys.exit(1)
    print_declension_of_noun(word)
    if args.openai:
        openai_response = get_openai_response(word)
        parsed_sentences = parse_openai_response(openai_response)
        add_sentences_to_db(parsed_sentences, word_id, replace=True)
elif args.conjugation:
    if word_type != 'verb':
        sys.stderr.write("Conjugation is only available for verbs.\n")
        sys.exit(1)

    word_id = get_word_id(word)
    moods = get_available_moods(word_id)

    if not moods:
        print(f"{RED}No conjugation data found.{RESET}")
        sys.exit(0)

    print(f"\n{RED}Available Moods:{RESET}")
    for idx, (mid, mname) in enumerate(moods):
        print(f"{idx + 1}: {mname.capitalize()}")

    try:
        mood_idx = int(input(f"\n{BLUE}Select Mood: {RESET}")) - 1
        if 0 <= mood_idx < len(moods):
            selected_mood_id = moods[mood_idx][0]
            selected_mood_name = moods[mood_idx][1]

            tenses = get_available_tenses(word_id, selected_mood_id)
            if not tenses:
                print(f"{RED}No tenses found for this mood.{RESET}")
                sys.exit(0)

            print(f"\n{RED}Available Tenses for {selected_mood_name.capitalize()}:{RESET}")
            for idx, tense in enumerate(tenses):
                print(f"{idx + 1}: {tense.capitalize()}")

            tense_idx = int(input(f"\n{BLUE}Select Tense: {RESET}")) - 1
            if 0 <= tense_idx < len(tenses):
                selected_tense = tenses[tense_idx]
                print_conjugation_of_verb(word, selected_mood_id, selected_tense)
            else:
                print(f"{RED}Invalid tense selection.{RESET}")
        else:
            print(f"{RED}Invalid mood selection.{RESET}")
    except ValueError:
        print(f"{RED}Invalid input.{RESET}")
elif args.sentence:
    word_id = get_word_id(word)
    if args.replace:
        # initial sentences part
        openai_response = get_openai_response(word)
        parsed_sentences = parse_openai_response(openai_response)
        add_sentences_to_db(parsed_sentences, word_id, replace=True)
    print_sentences_from_db(word_id)
elif args.word:
    # get saved word in database
    word_id = get_word_id(word)
    full_word = get_word(word_id) # print das Zimmer, not zimmer (search word)
    definition_id = get_definition_id(word)
    definition = get_definition(definition_id)
    print(BLUE + full_word + RESET)
    print(RED + definition + RESET)
else:
    sys.exit(2)

  



