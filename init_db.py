import sqlite3

def initialize_database():
    with open('schema.sql', 'r') as f:
        schema = f.read()

    conn = sqlite3.connect('dictionary.db')
    curr = conn.cursor()

    curr.executescript(schema)
    conn.commit()

    pos_ls = ['noun', 'pronoun', 'verb', 'adjective', 'adverb',
              'preposition', 'conjunction', 'interjections']

    for pos in pos_ls:
        curr.execute("INSERT INTO types (type) VALUES (?)", (pos,))

    moods = ['simple', 'indicative', 'subjunctive', 'conditional',
             'imperative', 'infinitive/participle']

    for mood in moods:
        curr.execute("INSERT INTO moods (mood) VALUES (?)", (mood,))
    conn.commit()

    for gn in ['masculine', 'feminine', 'neutral']:
        curr.execute("INSERT INTO genders (gender) VALUES (?)", (gn,))
    conn.commit()


    curr.close()
    conn.close()
    print('database is initialized')

if __name__ == '__main__':
    initialize_database()
