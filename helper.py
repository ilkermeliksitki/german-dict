import re
from bs4 import BeautifulSoup, element
import pandas as pd
from io import StringIO
import re

from escape_sequences import BLUE, RED, GREEN, RESET


def print_aligned_conjugation_table(conjugation_list: list, col_padding: int = 4):
    """
    prints the conjugation table with aligned columns.
    conjugation_list: list of tuples (tense, pronoun, conjugation)
    """
    if not conjugation_list:
        return

    # prepare rows 2D array, where each rows are:
    # [ich, würde, gewesen, sein], [du, würdest, gewesen, sein], ...
    rows = []
    for _, pronoun, conjugation in conjugation_list:
        if pronoun.isnumeric():
            continue
        parts = conjugation.split()
        rows.append([pronoun] + parts)
    if not rows:
        return

    # find the longest row length
    num_columns = max(len(row) for row in rows)
    col_widths = [0] * num_columns
    for row in rows:
        for i, item in enumerate(row):
            if len(item) > col_widths[i]:
                col_widths[i] = len(item)

    # add padding buffer (the space between columns)
    col_widths = [w + col_padding for w in col_widths]
    for row in rows:
        # pronoun (first column) is blue
        pronoun = row[0]
        cell_padding = col_widths[0] - len(pronoun)
        if cell_padding < 0: cell_padding = 0
        print(f"{BLUE}{pronoun}{RESET}{' ' * cell_padding}", end='')
        
        # conjugation parts (rest) are green
        for i in range(1, len(row)):
            item = row[i]
            cell_padding = col_widths[i] - len(item)
            if cell_padding < 0: cell_padding = 0
            
            print(f"{GREEN}{item}{RESET}{' ' * cell_padding}", end='')
        print()
    
def get_possible_matches(word: str) -> list:
    """Generates possible umlaut variations for a given word."""
    candidates = [word]

    # Common mappings
    mappings = {
        'ae': 'ä',
        'oe': 'ö',
        'ue': 'ü',
        'ss': 'ß'
    }

    # Simple replacement for typical patterns
    temp_word = word
    for k, v in mappings.items():
        if k in temp_word:
            candidates.append(temp_word.replace(k, v))

    # also try replacing single vowels if they mapped to umlauts (heuristic)
    # this is broader, e.g. "wahlen" -> "wählen"
    vowel_map = {
        'a': 'ä',
        'o': 'ö',
        'u': 'ü'
    }

    # generate variations for each vowel occurrence
    # for now, add the specific 'a' -> 'ä' etc logic if the simple mapping didn't cover it.

    if 'a' in word: candidates.append(word.replace('a', 'ä'))
    if 'o' in word: candidates.append(word.replace('o', 'ö'))
    if 'u' in word: candidates.append(word.replace('u', 'ü'))

    return list(set(candidates))

def parse_word_descriptors(soup: BeautifulSoup):
    """ parses word descriptors for identifying its name, type,
        gender (if it exists), regularity, and auxiliary (if it
        exists)
    """
    TYPES = ['noun', 'adjective', 'pronoun']
    GENDERS = ['masculine', 'feminine', 'neutral']
    REGULAR = ['regular', 'irregular']
    AUXILIARY = ['haben', 'sein']

    r_cntr = soup.select_one("div.rCntr.rClear")
    if not r_cntr:
        return None, None, None, None, None, None

    word = r_cntr.text.strip()
    # an·zeigen => anzeigen
    word = re.sub(r'\·', '', word)

    descriptors_tag = soup.select_one("p.rInf")
    if not descriptors_tag:
        return word, 'unknown', None, None, None, None

    descriptors = descriptors_tag.text.strip()
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
        'conditional': {
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
            if 'conditional' in mood:
                mood = 'conditional'
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


def parse_declension(soup: BeautifulSoup):

    def clean_form(cell):
        """Removes spaces, slashes, and superscripts. Keeps first clear form."""
        if pd.isna(cell):
            return ''
        text = re.sub(r"\s+", "", str(cell))          # remove all whitespace
        text = re.split(r"/", text)[0]                # take the first variant before slash
        text = re.sub(r"\d+", "", text)               # remove superscript numbers
        text = re.sub(r'[\u2070-\u2079]+$', '', text) # remove unicode superscripts
        return text

    def split_article_words(compound):
        """Splits compound articles into separate words. derTisch => der Tisch."""
        match = re.match(r'^([a-zäöüß]+)([A-ZÄÖÜ].*)$', compound)
        if match:
            return match.group(1) + ' ' + match.group(2)
        else:
            # fallback if no match
            return compound


    declension_dict = {
        'singular': {'nominative': '', 'genitive': '', 'dative': '', 'accusative': ''},
        'plural': {'nominative': '', 'genitive': '', 'dative': '', 'accusative': ''}
    }

    cases = ['nominative', 'genitive', 'dative', 'accusative']

    # Extract tables
    table1_html = soup.select_one("div.vDkl > div.vTbl:nth-of-type(1) > table").prettify()
    table2_html = soup.select_one("div.vDkl > div.vTbl:nth-of-type(2) > table").prettify()

    sgl = pd.read_html(StringIO(table1_html))[0]
    # concatenate the first and second columns
    sgl.iloc[:, 1] = sgl.iloc[:, 1] + '  ' + sgl.iloc[:, 2]

    plr = pd.read_html(StringIO(table2_html))[0]

    # concatenate the first and second columns
    plr.iloc[:, 1] = plr.iloc[:, 1] + '  ' + plr.iloc[:, 2]

    for i, case in enumerate(cases):
        declension_dict['singular'][case] = split_article_words(clean_form(sgl.iloc[i, 1]))
        declension_dict['plural'][case] = split_article_words(clean_form(plr.iloc[i, 1]))

    return declension_dict
