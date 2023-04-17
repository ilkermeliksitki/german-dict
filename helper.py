import re
from bs4 import BeautifulSoup

def parse_word_descriptors(soup: BeautifulSoup):
    """ parses word descriptors for identifying its name, type,
        gender (if it exists), regularity, and auxiliary (if it
        exists)
    """
    TYPES = ['noun', 'adjective', 'pronoun']
    GENDERS = ['masculine', 'feminine', 'neutral']
    REGULAR = ['regular', 'irregular']
    AUXILIARY = ['haben', 'sein']

    word = soup.select_one("p.vGrnd.rCntr").text.strip()
    descriptors = soup.select_one("p.rInf").text.strip()
    # create descriptos list by trimming unnecessary chars.
    ls = re.findall(r'\b\w+\b', descriptors)

    word_type = 'verb' 
    for tp in TYPES:
        if tp in ls:
            word_type = tp
            break

    gender = None
    for gd in GENDERS:
        if gd in ls:
            gender = gd
            break

    regular = None
    for rg in REGULAR:
        if rg in ls:
            regular = rg
            break

    auxiliary = None
    for ax in AUXILIARY:
        if ax in ls:
            auxiliary = ax
            break
    return word, word_type, gender, regular, auxiliary


def parse_declension(soup :BeautifulSoup):
    declension_dict = {'singular': {}, 'plural': {}}
    divs = soup.select("div.rAufZu > div.vDkl > div.vTbl") 
    for i in range(len(divs)):
        tb = divs[i].table
        nom_art = tb.find('th', {'title': 'Nominative'}).next_sibling.next_sibling.text
        nom     = tb.find('th', {'title': 'Nominative'}).next_sibling.next_sibling.next_sibling.text

        gen_art = tb.find('th', {'title': 'Genitive'  }).next_sibling.next_sibling.text
        gen     = tb.find('th', {'title': 'Genitive'  }).next_sibling.next_sibling.next_sibling.text

        dat_art = tb.find('th', {'title': 'Dative'    }).next_sibling.next_sibling.text
        dat     = tb.find('th', {'title': 'Dative'    }).next_sibling.next_sibling.next_sibling.text

        acc_art = tb.find('th', {'title': 'Accusative'}).next_sibling.next_sibling.text
        acc     = tb.find('th', {'title': 'Accusative'}).next_sibling.next_sibling.next_sibling.text
        # singular
        if i == 0:
            declension_dict['singular'] = {'nominative': nom_art + ' ' + nom,
                                           'genitive'  : gen_art + ' ' + gen,
                                           'dative'    : dat_art + ' ' + dat,
                                           'accusative': acc_art + ' ' + acc}
        # plural
        elif i == 1:
            declension_dict['plural'] = {'nominative'  : nom_art + ' ' + nom,
                                         'genitive'    : gen_art + ' ' + gen,
                                         'dative'      : dat_art + ' ' + dat,
                                         'accusative'  : acc_art + ' ' + acc}
    return declension_dict
