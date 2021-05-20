#!/usr/bin/env python
import logging
import subprocess
from pathlib import Path

from lhotse import load_manifest
from snowfall.common import setup_logger
import re

WORDLIST = dict()
UNK = '<UNK>'
REPLACE_UNKS = True

setup_logger('exp/log/prepare_lm')
def read_lexicon_words(lexicon):
    with open(lexicon, 'r', encoding='utf-8') as f:
        for line in f:
            line = re.sub(r'(?s)\s.*', '', line)
            WORDLIST[line] = 1


def case_normalize(w):
    # this is for POI
    # but we should add it into the lexicon
    if w.startswith('~'):
        return w.upper()
    else:
        return w.lower()


def process_transcript(transcript):
    global WORDLIST
    # https://www.programiz.com/python-programming/regex
    # [] for set of characters you with to match
    # eg. [abc] --> will search for a or b or c
    # "." matches any single character
    # "$" to check if string ends with a certain character 
    # eg. "a$" should end with "a"
    # replace <extreme background> with <extreme_background>
    # replace <foreign lang="Spanish">fuego</foreign> with foreign_lang=
    # remove "[.,!?]"
    # remove " -- "
    # remove " --" --> strings that ends with "-" and starts with " "
    # \s+ markers are – that means “any white space character, one or more times”
    tmp = re.sub(r'<extreme background>', '', transcript)
    tmp = re.sub(r'<background>', '', transcript)
    tmp = re.sub(r'foreign\s+lang=', 'foreign_lang=', tmp)
    tmp = re.sub(r'\(\(', '', tmp)
    tmp = re.sub(r'\)\)', '', tmp)
    tmp = re.sub(r'[.,!?]', ' ', tmp)
    tmp = re.sub(r' -- ', ' ', tmp)
    tmp = re.sub(r' --$', '', tmp)
    x = re.split(r'\s+', tmp)

    out_x = list()
    for w in x:
        w = w.strip()
        w = case_normalize(w)
        if w == "":
            continue
        elif w in WORDLIST:
            out_x.append(w)
        else:
            out_x.append(UNK)

    return ' '.join(out_x)


def main():
    # Read Lhotse supervisions, remove special non-lexical tokens,
    # and write the sentences to a text file for LM training.
    logging.info(f'Preparing LM training text.')
    lexicon =  'data/local/dict_nosp/lexicon/lexicon_raw_nosil.txt'
    read_lexicon_words(lexicon)
    sups = load_manifest('exp/data/supervisions_train.json')
    f = open('exp/data/lm_train_text', 'w')
    for s in sups:
        print(s.text, file=f)

    sups = load_manifest('exp/data/supervisions_dev_clean.json')
    f = open('exp/data/lm_dev_text', 'w')
    for s in sups:
        print(s.text, file=f)

if __name__ == '__main__':
    main()
