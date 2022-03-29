import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import webbrowser


parser = argparse.ArgumentParser()
parser.add_argument("word", help="the word that you want to look for.")
parser.add_argument(
	"-p", "--pronunciation", help="gives the link for the pronunciation of the word.", 
	action="store_true"
)
parser.add_argument("-d", "--declension", help="prints the declension of the word.", action="store_true")
args = parser.parse_args()


# word = input().strip()
word = args.word.strip()
# word = "spülbecken"
r = requests.get(f"https://www.verbformen.com/declension/nouns/{word}.htm")
soup = BeautifulSoup(r.text, "html.parser")

if r.status_code == 429:
	print("Too many requests, slow  down")
	exit()

main_element = soup.select_one("p.vGrnd.rCntr")
the_word = main_element.text.strip()
pronunciation = main_element.select_one("a").get("href")
en_translation = soup.select("dl.vNrn > dd > span")[3].text
# print(the_word, en_translation, pronunciation, sep="\n")
print()
print(the_word, en_translation, sep="\n\n")

if args.pronunciation:
	webbrowser.open(pronunciation)

# das Spülbecken
# sink, rinsing tank, utility sink, settling pit
# https://www.verbformen.de/deklination/substantive/grundform/der_Spu3lbecken.mp3

declension = soup.select_one("div.vTxtTbl > table")
declension_df = pd.read_html(str(declension))[0]
declension_df.columns = ["Fälle", "Singular", "Plural"]
declension_df["Fälle"] = ["nominativ", "genitiv", "dativ", "akkusativ"]
declension_df.set_index("Fälle", inplace=True)

if args.declension:
	print(declension_df)

#                   Singular           Plural
# Fälle                                     
# nominativ   das Spülbecken   die Spülbecken
# genitiv     des Spülbeckens  der Spülbecken
# dativ       dem Spülbecken   den Spülbecken
# akkusativ   das Spülbecken   die Spülbecken
