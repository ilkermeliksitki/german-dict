import os
import re
import sys
from openai import OpenAI

from typing import List, Tuple

from escape_sequences import *

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL_ENGINE = "gpt-4o-mini"

def get_openai_response(word) -> str:
    print(ITALIC + 'waiting for open ai to get example sentences\n' + RESET)
    model_engine = MODEL_ENGINE
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"prompt 5 numbered list example sentences that is used in daily life consisting \
of at least 5 words for the word {word} in German and translate those sentences \
in English, here is the example: \n<german sentence> - <english sentence>"

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
    except Exception as e:
        sys.stderr.write(f'Response error: {e}\n')
        response = None

    return response

def parse_openai_response(response: str) -> List[Tuple[str, str]]:
    """
        Define a function that takes a string `r` and returns
        a list of example sentence tuples
    """
    if response is None:
        sys.stderr.write('open ai response is None, please repeat the action.\n')
        sys.exit(3)

    parsed_examples = []
    text = response.choices[0].message.content.strip()
    text_ls = text.split('\n')
    for example in text_ls:
        # Extract the example number, German sentence, and English 
        # translation from the match object.
        try:
            parsed_example_tp = re.findall(r'(\d)\W+(.*)\s-\s(.*)', example.strip())[0]
        except:
            sys.stderr.write('open ai response error, please repeat the action.\n')
            sys.exit(4)
        # if lenght of the tuple is not 3, consider it is not parsed 
        # correctly, and skip.
        if len(parsed_example_tp) != 3:
            continue
        parsed_examples.append(parsed_example_tp)
    return parsed_examples

