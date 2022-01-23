import requests
from bs4 import BeautifulSoup
import pandas as pd

# word = input().strip()
word = "spülbecken"
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

declension = soup.select_one("div.vTxtTbl > table")
declension_df = pd.read_html(str(declension))[0]
declension_df.columns = ["Fälle", "Singular", "Plural"]
declension_df["Fälle"] = ["nominativ", "genitiv", "dativ", "akkusativ"]
declension_df.set_index("Fälle", inplace=True)
# print(declension_df)

