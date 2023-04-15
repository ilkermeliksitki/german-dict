import os
import re
import openai
from typing import List, Tuple

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL_ENGINE = "text-davinci-003"
TEMPERATURE = 1.150

def get_response() -> str:
    openai.api_key = OPENAI_API_KEY
    model_engine = MODEL_ENGINE

    word = input("Enter a german word: ")
    prompt = f"prompt 5 numbered list example sentences that is used in daily life consisting \
of at least 5 words for the word {word} in German and translate those sentences \
in English, here is the example: \n<german sentence> - <english sentence>"

    # generate text from the prompt using the GPT-3 model
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=256,
        n=1,
        temperature=TEMPERATURE
    )

    #generated_text = response.choices[0].text.strip()
    return response

def parse_response(response: str) -> List[Tuple[str, str]]:
    """
        Define a function that takes a string `r` and returns
        a list of example sentence tuples
    """
    parsed_examples = []
    text = response["choices"][0]["text"].strip()
    text_ls = text.split('\n')
    for example in text_ls:
        # Extract the example number, German sentence, and English 
        # translation from the match object.
        parsed_example_tp = re.findall(r'(\d)\W+(.*)\s-\s(.*)', example.strip())[0]
        # if lenght of the tuple is not 3, consider it is not parsed 
        # correctly, and skip.
        if len(parsed_example_tp) != 3:
            continue
        parsed_examples.append(parsed_example_tp)
    return parsed_examples

r = get_response()
ls = parse_response(r)
print(ls)
