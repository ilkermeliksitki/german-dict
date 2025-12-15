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
    curr.execute('SELECT * FROM words WHERE word LIKE ?', ("%" + word + "%",))
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
    conn.commit()
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
    curr.execute('SELECT id FROM words WHERE word LIKE ?', ("%" + word + "%",))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0]

def get_word_type(word):
    curr, conn = _open_database()
    query = '''
        SELECT type FROM types
        JOIN words ON type_id = types.id
        WHERE word LIKE ?
    '''
    curr.execute(query, ("%" + word + "%",))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0] if result else None

def get_word(word_id):
    curr, conn = _open_database()
    curr.execute('SELECT word FROM words WHERE id = ?', (word_id,))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0]

def get_definition_id(word):
    curr, conn = _open_database()
    curr.execute('SELECT definition_id FROM words WHERE word LIKE ?', ("%" + word + "%",))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0]

def get_definition(definition_id):
    curr, conn = _open_database()
    curr.execute('SELECT definition FROM definitions WHERE id = ?', (definition_id,))
    result = curr.fetchone()
    _close_database(curr, conn)
    return result[0]

def get_mood_id(mood: str, curr=None) -> int:
    should_close = False
    if curr is None:
        curr, conn = _open_database()
        should_close = True

    curr.execute('SELECT id FROM moods WHERE mood LIKE ?', (mood,))
    result = curr.fetchone()

    if should_close:
        _close_database(curr, conn)

    if result is not None:
        return result[0]
    return -1

def add_conjugation_to_db(conjugation_dict, word_id):
    curr, conn = _open_database()

    for mood_name, tenses in conjugation_dict.items():
        mood_id = get_mood_id(mood_name, curr)
        if mood_id == -1:
            continue

        for tense, pronouns in tenses.items():
            for pronoun, conjugation in pronouns.items():
                curr.execute("""
                    INSERT OR IGNORE INTO conjugations
                    (tense, pronoun, conjugation, word_id, mood_id)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (tense, pronoun, conjugation, word_id, mood_id)
                )

    _close_database(curr, conn)

def _pronoun_sort_key(item):
    pronoun = item[1]
    pronoun_order = ['ich', 'du', 'er', 'wir', 'ihr', 'sie', '0', '1']
    return pronoun_order.index(pronoun)

def get_available_moods(word_id: int):
    curr, conn = _open_database()
    curr.execute("""
        SELECT DISTINCT moods.id, moods.mood
        FROM conjugations
        JOIN moods ON conjugations.mood_id = moods.id
        WHERE conjugations.word_id = ?
        ORDER BY moods.id
    """, (word_id,))
    moods = curr.fetchall()
    _close_database(curr, conn)
    return moods

def get_available_tenses(word_id: int, mood_id: int):
    curr, conn = _open_database()
    curr.execute("""
        SELECT DISTINCT tense
        FROM conjugations
        WHERE word_id = ? AND mood_id = ?
    """, (word_id, mood_id))
    tenses = curr.fetchall()
    _close_database(curr, conn)
    return [t[0] for t in tenses]

def print_conjugation_of_verb(word, mood_id, tense):
    curr, conn = _open_database()
    word_id = get_word_id(word)

    curr.execute("""
        SELECT tense, pronoun, conjugation
        FROM conjugations
        WHERE word_id = ? and mood_id = ? and tense = ?
    """,
        (word_id, mood_id, tense)
    )
    conjugation_ls = curr.fetchall()

    if not conjugation_ls:
        print(f"{RED}No conjugation found for {tense} in this mood.{RESET}")
        _close_database(curr, conn)
        return

    # sort the list according to german pronouns
    conjugation_ls = sorted(conjugation_ls, key=_pronoun_sort_key)

    print(f"\n{RED}Mood: {mood_id} | Tense: {tense}{RESET}")
    for index, conjugation_tuple in enumerate(conjugation_ls):
        # if pronoun appears numeric, do not write down
        if not conjugation_tuple[1].isnumeric():
             # Special padding for "ich", "du" vs "wir" etc?
             # Just keep it consistent
            print(f"{BLUE + conjugation_tuple[1] + RESET:20} ", end='')
        print(f"{GREEN + conjugation_tuple[2] + RESET}")
    _close_database(curr, conn)

def print_declension_of_noun(word):
    curr, conn = _open_database()
    word_id = get_word_id(word)
    curr.execute('SELECT singular_nominative, plural_nominative, singular_genitive, plural_genitive, '
                 'singular_dative, plural_dative, singular_accusative, plural_accusative '
                 'FROM declensions WHERE word_id = ?', (word_id,))
    result = curr.fetchone()
    if result:
        print(RED + "Singular" + RESET)
        print(f"{BLUE}nom: {result[0]} {RESET}")
        print(f"{BLUE}acc: {result[6]} {RESET}")
        print(f"{BLUE}dat: {result[4]} {RESET}")
        print(f"{BLUE}gen: {result[2]} {RESET}")
        print()
        print(RED + "Plural" + RESET)
        print(f"{BLUE}nom: {result[1]} {RESET}")
        print(f"{BLUE}acc: {result[7]} {RESET}")
        print(f"{BLUE}dat: {result[5]} {RESET}")
        print(f"{BLUE}gen: {result[3]} {RESET}")
    else:
        print(f"{RED}No declension found for the word '{word}'.{RESET}")

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


def add_declension_to_db(declension_dict, word_id):
    curr, conn = _open_database()

    query = """
        INSERT INTO declensions (
            singular_nominative, plural_nominative,
            singular_genitive, plural_genitive,
            singular_dative, plural_dative,
            singular_accusative, plural_accusative,
            word_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    values = (
        declension_dict['singular']['nominative'],
        declension_dict['plural']['nominative'],
        declension_dict['singular']['genitive'],
        declension_dict['plural']['genitive'],
        declension_dict['singular']['dative'],
        declension_dict['plural']['dative'],
        declension_dict['singular']['accusative'],
        declension_dict['plural']['accusative'],
        word_id
    )
    conn.execute(query, values)

    _close_database(curr, conn)
