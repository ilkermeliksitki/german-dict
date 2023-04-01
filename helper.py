import webbrowser
import pandas as pd
import sys

def left_align_df(df):
    # allign to the left
    try:
        max_length = df.applymap(len).max().max()
    except:
        max_length = 12
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

    tenses = [
        "präsens", "präteritum", "imperativ",
        "konjunktiv i", "konjunktiv ii"
    ]

    conjugations_dict = dict()
    conj_ls_div = soup.select('div.rAufZu > div.vTbl')
    for div in conj_ls_div:
        h2 = div.select_one("h2")
        if h2:
            tense_name = h2.text.lower()
            if tense_name in tenses:
                table = str(div.select_one("table"))
                df = pd.read_html(table)[0]
                df.columns = ["pronoun", "conjugation"]
                df = left_align_df(df)
                conjugations_dict[tense_name] = df.to_string(index=False)
            else:
                continue
        else:
            continue
    return conjugations_dict

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

def get_declension_definition(soup):
    div_element = soup.select_one("div.rAbschnitt > div > section > div.rAufZu")
    span_tag = div_element.select_one("div.rCntr > div > p > span")
    definitions = span_tag.text.split()
    definition = " ".join(definitions)
    return definition

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
