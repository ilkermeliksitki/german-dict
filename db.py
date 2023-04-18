import sqlite3
from typing import Tuple
from sqlite3 import Cursor
from sqlite3 import Connection

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
    curr, conn = _open_database()
    word, gender_id, auxiliary, regular, separable, definition_id, type_id = values
    curr.execute('''INSERT INTO words 
                 (word, gender_id, auxiliary, regular, separable, definition_id, type_id) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', values)
    _close_database(curr, conn)

def add_definition_to_database(definition: str) -> int:
    # add definition to database, and return id of the definition
    curr, conn = _open_database()
    curr.execute('INSERT INTO definitions (definition) VALUES (?)', (definition,))
    conn.commit()
    curr.execute('SELECT id FROM definitions WHERE definition = ?', (definition,))
    result = curr.fetchone()
    _close_database(curr, conn)
    print('def add successful')
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
    print(result)
    _close_database(curr, conn)
    return result[0]

