import webbrowser
import pandas as pd
import sys

def left_align_df(df):
    # allign to the left
    max_length = df.applymap(len).max().max()
    df.columns = [col.ljust(max_length) for col in df.columns]
    df = df.apply(lambda x: x.str.ljust(max_length))
    return df

def is_conjugation_found(soup):
    # return the error not found error message or none.
    oops = soup.select_one("h2.rCntr")
    return oops

def get_conjugation(soup):
    oops = is_conjugation_found(soup)
    if oops:
        sys.stderr.write(opps.text)
        return None
    d = dict()
    conj_ls_div = soup.select('div.rAufZu > div.vTbl')
    for div in conj_ls_div:
        h2 = div.select_one("h2")
        if h2:
            if h2.text.lower() == "präsens": 
                table = str(div.select_one("table"))
                df = pd.read_html(table)[0]
                df.columns = ["pronoun", "conjugation"]
                df.set_index("pronoun", inplace=True)
                df = left_align_df(df)
                d["präsens"] = df
            elif h2.text.lower() == "präteritum":
        else:
            continue

def get_name_and_meanaing_of_verb_conj(soup):
    oops = is_conjugation_found(soup)
    if oops:
        print(oops.text)
        return None, None
    name_p = soup.select_one("p#grundform > b")
    name = name_p.text
    meaning_div = soup.select_one("div#vStckKrz > div > p > span")
    meaning_ls = meaning_div.text.split()
    meaning = " ".join(meaning_ls)
    return name, meaning

def get_name_with_article_dec(soup):
    main_element = soup.select_one("p.vGrnd.rCntr")
    return main_element.text.strip()

def get_pronunciation_link_dec(soup):
    main_element = soup.select_one("p.vGrnd.rCntr")
    pronunciation = main_element.select_one("a").get("href")
    return pronunciation

def get_pronunciation_link_conj(soup):
    pass

def get_declension(soup):
    # create the related dataframe
    main_element = soup.select_one("p.vGrnd.rCntr")
    en_translation = soup.select("dl.vNrn > dd > span")[3].text
    declension = soup.select_one("div.vTxtTbl > table")
    declension_df = pd.read_html(str(declension))[0]
    declension_df.columns = ["Fälle", "Singular", "Plural"]
    declension_df["Fälle"] = ["nominativ", "genitiv", "dativ", "akkusativ"]

    # arrange index and sort
    declension_df.set_index("Fälle", inplace=True)
    declension_df.sort_index(inplace=True)

    declension_df = left_align_df(declension_df)

    return declension_df
