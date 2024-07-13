import sqlite3
from typing import Tuple
from sqlite3 import Cursor
from sqlite3 import Connection

from escape_sequences import *

def _open_database(path='dictionary.db') -> Tuple[Cursor, Connection]:
    conn = sqlite3.connect(path)
    curr = conn.cursor()
    return curr, conn

def _close_database(curr: Cursor, conn: Connection):
    conn.commit()
    curr.close()

def check_word_exists(word: str):
    curr, conn = _open_database()
    curr.execute('SELECT * FROM words WHERE word = ?', (word,))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result is not None 

def add_word_to_database(values: Tuple[str, str, str, str, str, str, str,]):
    #word, gender_id, auxiliary, regular, separable, definition_id, type_id = values
    # double check
    curr, conn = _open_database()
    curr.execute('''INSERT OR IGNORE INTO words
                 (word, gender_id, auxiliary, regular, separable, definition_id, type_id, have_declension, have_conjugaison) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', values)
    _close_database(curr, conn)

def add_definition_to_database(definition: str) -> int:
    # add definition to database, and return id of the definition
    curr, conn = _open_database()
    curr.execute('INSERT OR IGNORE INTO definitions (definition) VALUES (?)', (definition,))
    conn.commit()
    curr.execute('SELECT id FROM definitions WHERE definition = ?', (definition,))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0]

def get_type_id(type_: str) -> int:
    curr, conn = _open_database()
    curr.execute('SELECT id FROM types WHERE type = ?', (type_,))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0]

def get_gender_id(gender: str) -> int:
    curr, conn = _open_database()
    curr.execute('SELECT id FROM genders WHERE gender = ?', (gender,))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0]

def get_word_id(word):
    curr, conn = _open_database()
    curr.execute('SELECT id FROM words WHERE word = ?', (word,))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0]

def get_definition_id(word):
    curr, conn = _open_database()
    curr.execute('SELECT definition_id FROM words WHERE word = ?', (word,))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0]

def get_definition(definition_id):
    curr, conn = _open_database()
    curr.execute('SELECT definition FROM definitions WHERE id = ?', (definition_id,))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0]

# for now, only simple tense is being added.
def add_conjugation_to_db(conjugation_dict, word_id):
    curr, conn = _open_database()
    simple_tense_dict = conjugation_dict['simple']
    for tense in simple_tense_dict.keys():
        for pronoun in simple_tense_dict[tense].keys():
            conjugation = simple_tense_dict[tense][pronoun]
            #print(tense, pronoun, conjugation, 'is added')
            curr.execute(
                "INSERT OR IGNORE INTO conjugations (tense, pronoun, conjugation, word_id, mood_id) VALUES (?, ?, ?, ?, ?)",
                (tense, pronoun, conjugation, word_id, 1)
            )
    _close_database(curr, conn)

def _pronoun_sort_key(item):
    pronoun = item[1]
    pronoun_order = ['ich', 'du', 'er', 'wir', 'ihr', 'sie', '0', '1']
    return pronoun_order.index(pronoun)

def print_conjugation_of_verb(word, tense_id):
    curr, conn = _open_database()
    word_id = get_word_id(word)
    tense_dict = {
        1: 'present', 2: 'imperfect', 3: 'imperative', 4: 'present subj.',
        5: 'imperf. subj.', 6: 'infinitive', 7: 'participle'
    }
    curr.execute('SELECT tense, pronoun, conjugation FROM conjugations WHERE word_id = ? and tense = ?',
        (word_id, tense_dict[tense_id])
    )
    conjugation_ls = curr.fetchall()
    # sort the list according to german pronouns
    conjugation_ls = sorted(conjugation_ls, key=_pronoun_sort_key)
    for index, conjugation_tuple in enumerate(conjugation_ls):
        if index == 0:
            print(RED + conjugation_tuple[0] + RESET)
        # if pronoun appears numeric, do not write down
        if not conjugation_tuple[1].isnumeric():
            print(f"{BLUE + conjugation_tuple[1] + RESET:20} ", end='')
        print(f"{GREEN + conjugation_tuple[2] + RESET}")
    _close_database(curr, conn)

def add_sentences_to_db(sentences_ls, word_id, replace=False):
    curr, conn = _open_database()
    if replace:
        curr.execute('DELETE FROM sentences WHERE word_id = ?', (word_id,))
    for _, de_sentence, en_sentence in sentences_ls:
        curr.execute('INSERT OR IGNORE INTO sentences (sentence, word_id) VALUES (?, ?)', (de_sentence + '--' + en_sentence, word_id))
    _close_database(curr, conn)

def print_sentences_from_db(word_id):
    curr, conn = _open_database()
    curr.execute('SELECT sentence FROM sentences WHERE word_id = ?', (word_id,))
    result = curr.fetchall()
    print()
    for sentence in result:
        de, en = sentence[0].split('--')
        align_num = len(de)
        print(f"{BLUE_LIGHT + de + RESET:45}", end=' ')
        print(BROWN_LIGHT + ITALIC + en + RESET, end='\n\n')
    _close_database(curr, conn)

