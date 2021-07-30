#!/usr/bin/env python3
import torch
import lhotse
from lhotse import load_manifest, fix_manifests

sups = load_manifest('exp/data/supervisions_safet_train.json')
f = open('exp/data/lm_train_text', 'w')
for s in sups:
    print(s.text, file=f)

sups = load_manifest('exp/data/supervisions_safet_dev_clean.json')
f = open('exp/data/lm_dev_text', 'w')
for s in sups:
    print(s.text, file=f)
