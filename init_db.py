import sqlite3

with open('schema.sql', 'r') as f:
    schema = f.read()

conn = sqlite3.connect('dictionary.db')
curr = conn.cursor()

curr.executescript(schema)
conn.commit()

pos_ls = ['Nomen', 'Pronomen', 'Verb', 'Adjektiv', 'Adverb',
          'Präposition', 'Konjunktion', 'Interjections']

for pos in pos_ls:
    curr.execute("INSERT INTO types (type) VALUES (?)", (pos,))

moods = ['simple', 'indicative', 'subjunctive', 'contidional',
         'imperative', 'infinitive/participle']

for mood in moods:
    curr.execute("INSERT INTO moods (mood) VALUES (?)", (mood,))
conn.commit()

curr.close()
conn.close()
