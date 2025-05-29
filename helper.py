import re
from bs4 import BeautifulSoup, element

def parse_word_descriptors(soup: BeautifulSoup):
    """ parses word descriptors for identifying its name, type,
        gender (if it exists), regularity, and auxiliary (if it
        exists)
    """
    TYPES = ['noun', 'adjective', 'pronoun']
    GENDERS = ['masculine', 'feminine', 'neutral']
    REGULAR = ['regular', 'irregular']
    AUXILIARY = ['haben', 'sein']

    word = soup.select_one("div.rCntr.rClear").text.strip()
    # an·zeigen => anzeigen
    word = re.sub(r'\·', '', word)
    descriptors = soup.select_one("p.rInf").text.strip()
    # create descriptos list by trimming unnecessary chars.
    ls = re.findall(r'\b\w+\b', descriptors)
    # clean up the list by superscripts and digits at the end of the words
    ls = [re.sub(r'[\d¹²³⁴⁵⁶⁷⁸⁹⁰]+$', '', word) for word in ls]

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

    separable = None
    if word_type == 'verb':
        separable = 0
        if 'separable' in ls:
            separable = 1
    return word, word_type, gender, regular, auxiliary, separable


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

def _delete_superscripts(s: str) -> str:
    # delete superscripts by using unicode superscript range.
    return re.sub(r'[\u2070-\u2079]', '', s)

def _create_numbered_key_dict(table_rows: element.ResultSet) -> dict:
    # this helper function is used for the tenses not having pronouns
    d = {}
    for i, tr in zip(range(len(table_rows)), table_rows):
        val = tr.text.lower().strip()
        d[str(i)] = _delete_superscripts(val)
    return d

def _parse_conjugation_table(table: element.Tag, mood: str, tense: str) -> dict:
    pronouns = ['ich', 'du', 'er', 'wir', 'ihr', 'sie']
    d = {}
    trs = table.select('tr')
    if mood == 'simple':
        if tense == 'infinitive' or tense == 'participle':
            d = _create_numbered_key_dict(trs)
        else:
            for pr, tr in zip(pronouns, trs):
                # delete pronoun, lower, and strip the conjugation
                conj = tr.text.lower().replace(pr, '').strip()
                if tense == 'imperative':
                    # there are extra paranthesis and white characters, delete them
                    conj = conj.replace('()', '')
                    conj = conj.strip()
                d[pr] = _delete_superscripts(conj)
    elif mood == 'imperative':
        d = _create_numbered_key_dict(trs)
    elif mood == 'infinitive/participle':
        d = _create_numbered_key_dict(trs)
    else:
        for pr, tr in zip(pronouns, trs):
            # delete pronoun, lower, and strip the conjugation
            conj = tr.text.lower().replace(pr, '').strip()
            d[pr] = _delete_superscripts(conj)
    return d

def parse_conjugation(soup: BeautifulSoup):
    """ parses the conjugations of verbs and return stored conjugations
        of that specific verb.
    """
    conjugation_dict = {
        'simple': {
            'present'          : {},
            'imperfect'        : {},
            'imperative'       : {},
            'present subj.'    : {},
            'imperf. subj.'    : {},
            'infinitive'       : {},
            'participle'       : {}
        },
        'indicative': {
            'present'          : {},
            'imperfect'        : {},
            'perfect'          : {},
            'pluperfect'       : {},
            'future'           : {},
            'future perfect'   : {}
        },
        'subjunctive': {
            'present subj.'    : {},
            'imperf. subj.'    : {},
            'perfect subj.'    : {},
            'pluperf. subj.'   : {},
            'future subj.'     : {},
            'fut. perf. subj.' : {}
        },
        'conditional (würde)': {
            'present cond.' : {},
            'past cond.'    : {}
        },
        'imperative': {
            'present' : {}
        },
        'infinitive/participle': {
            'infinitive i'  : {},
            'infinitive ii' : {},
            'participle i'  : {},
            'participle ii' : {}
        }
    }

    sections = soup.select("div.rAbschnitt > div > section.rBox.rBoxWht")
    first_section = True
    for sec in sections:
        # desc is only used to determine the relevant sections
        desc = sec.select_one("header > p")
        if desc is None:
            continue
        # divs include tenses in the relevant sections.
        divs = sec.select("div.rAufZu > div.vTbl")
        # tense name is not written for the case of simple tenses.
        if first_section:
            mood = 'simple'
        else:
            mood = sec.select_one("header > h2").text.lower()
        for div in divs:
            # tense name is under h2 tag in the first div, and h2 tag in others
            if first_section:
                tense = div.select_one("div > h2").text.lower()
            else:
                tense = div.select_one("div > h3").text.lower()
            table = div.select_one("table")
            if mood == 'imperative':
                # imperavite present == simple imperative, no need to parse
                conjugation_dict[mood][tense] = conjugation_dict['simple']['imperative']
                continue
            conjugation_dict[mood][tense] = _parse_conjugation_table(table, mood, tense)
        first_section = False
    return conjugation_dict

def parse_definition(soup: BeautifulSoup):
    p = soup.select_one("section.rBox.rBoxWht > div.rAufZu > div#vStckInf > div.rCntr > div > p.r1Zeile")
    p = p.text.strip()
    definition = ' '.join(p.split('\n'))
    return definition
