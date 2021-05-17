#!/usr/bin/env python
import logging
import subprocess
from pathlib import Path

from lhotse import load_manifest
from snowfall.common import setup_logger
import re
WORDLIST = dict()

def read_lexicon_words(lexicon):
    with open(lexicon, 'r', encoding='utf-8') as f:
        for line in f:
            line = re.sub(r'(?s)\s.*', '', line)
            WORDLIST[line] = 1

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

    sups = load_manifest('exp/data/supervisions_dev.json')
    f = open('exp/data/lm_dev_text', 'w')
    for s in sups:
        print(s.text, file=f)

if __name__ == '__main__':
    main()
