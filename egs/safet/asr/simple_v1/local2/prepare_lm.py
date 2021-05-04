#!/usr/bin/env python
import logging
import subprocess
from pathlib import Path

from lhotse import load_manifest
from snowfall.common import setup_logger

LM_CMD = """lmplz -o 3 --text exp/data/lm_train_text --arpa exp/data/arpa.3g.txt --skip_symbols"""
GFST_CMD = """python3 -m kaldilm \
    --read-symbol-table="data/lang_nosp/words.txt" \
    --disambig-symbol='#0' \
    --max-order=3 \
    exp/data/arpa.3g.txt > data/lang_nosp/G.fst.txt
"""

setup_logger('exp/log/prepare_lm')
if Path(f'data/lang_nosp/G.fst.txt').is_file():
    logging.info(f'G.fst.txt already exists.')
logging.info(f'Processing language')

# Read Lhotse supervisions, filter out silence regions, remove special non-lexical tokens,
# and write the sentences to a text file for LM training.
logging.info(f'Preparing LM training text.')
sups = load_manifest('exp/data/supervisions_train.json').filter(lambda s: s.text != '<silence>')
f = open('exp/data/lm_train_text', 'w')
for s in sups:
    text = ' '.join(w for w in s.text.split())
    if text:
        print(s.text, file=f)

sups = load_manifest('exp/data/supervisions_dev.json').filter(lambda s: s.text != '<silence>')
f = open('exp/data/lm_dev_text', 'w')
for s in sups:
    text = ' '.join(w for w in s.text.split())
    if text:
        print(s.text, file=f)
# Run KenLM n-gram training
#logging.info(f'Training KenLM n-gram model.')
#subprocess.run(LM_CMD, text=True, shell=True, check=True)
## Create G.fst.txt for K2 decoding
#logging.info(f'Compiling G.fst.txt with kaldilm.')
#subprocess.run(GFST_CMD.format(lang=lang), text=True, shell=True, check=True)
