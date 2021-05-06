#!/usr/bin/env python
import logging
import subprocess
from pathlib import Path

from lhotse import load_manifest
from snowfall.common import setup_logger
import re

setup_logger('exp/log/prepare_lm')
if Path(f'data/lang_nosp/G.fst.txt').is_file():
    logging.info(f'G.fst.txt already exists.')
logging.info(f'Processing language')


def case_normalize(w):
    if w.startswith('~'):
        return w.upper()
    else:
        return w.upper()


def process_transcript(transcript):
    global WORDLIST
    tmp = re.sub(r'extreme\s+background', 'extreme_background', transcript)
    tmp = re.sub(r'foreign\s+lang=', 'foreign_lang=', tmp)
    tmp = re.sub(r'\)\)([^\s])', ')) \1', tmp)
    tmp = re.sub(r'[.,!?]', ' ', tmp)
    tmp = re.sub(r' -- ', ' ', tmp)
    tmp = re.sub(r' --$', '', tmp)
    x = re.split(r'\s+', tmp)
    old_x = x
    x = list()

    w = old_x.pop(0)
    while old_x:
        if w.startswith(r'(('):
            while old_x and not w.endswith('))'):
                w2 = old_x.pop(0)
                w += ' ' + w2
            x.append(w)
            if old_x:
                w = old_x.pop(0)
        elif w.startswith(r'<'):
            #this is very simplified and assumes we will not get a starting tag
            #alone
            while old_x and not w.endswith('>'):
                w2 = old_x.pop(0)
                w += ' ' + w2
            x.append(w)
            if old_x:
                w = old_x.pop(0)
        elif w.endswith(r'))'):
            if old_x:
                w = old_x.pop(0)
        else:
            x.append(w)
            if old_x:
                w = old_x.pop(0)

    if not x:
        return None
    if len(x) == 1 and x[0] in ('<background>', '<extreme_background>'):
        return None

    out_x = list()
    for w in x:
        w = case_normalize(w)
        if w in WORDLIST:
            IV_WORDS[w] = 1 + IV_WORDS.get(w, 0)
            out_x.append(w)
        else:
            OOV_WORDS[w] = 1 + OOV_WORDS.get(w, 0)
            if REPLACE_UNKS:
                out_x.append(UNK)
            else:
                out_x.append(w)

    return ' '.join(out_x)


def main():
    # Read Lhotse supervisions, filter out silence regions, remove special non-lexical tokens,
    # and write the sentences to a text file for LM training.
    logging.info(f'Preparing LM training text.')
    sups = load_manifest('exp/data/supervisions_train.json').filter(lambda s: s.text != '<silence>')
    f = open('exp/data/lm_train_text', 'w')
    for s in sups:
        print(s.text, file=f)
    
    sups = load_manifest('exp/data/supervisions_dev.json').filter(lambda s: s.text != '<silence>')
    f = open('exp/data/lm_dev_text', 'w')
    for s in sups:
        cleaned_transcrition = process_transcript(s.text)
        print(cleaned_transcrition, file=f)


if __name__ == '__main__':
    main()
