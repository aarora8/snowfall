#!/usr/bin/env python
import logging
import subprocess
from pathlib import Path

from lhotse import load_manifest
from snowfall.common import setup_logger
import re

setup_logger('exp/log/prepare_lm')
def main():
    # Read Lhotse supervisions, remove special non-lexical tokens,
    # and write the sentences to a text file for LM training.
    logging.info(f'Preparing LM training text.')
    sups = load_manifest('exp/data/supervisions_safet_train.json')
    f = open('exp/data/lm_train_text', 'w')
    for s in sups:
        print(s.text, file=f)

    sups = load_manifest('exp/data/supervisions_safet_dev_clean.json')
    f = open('exp/data/lm_dev_text', 'w')
    for s in sups:
        print(s.text, file=f)

if __name__ == '__main__':
    main()
