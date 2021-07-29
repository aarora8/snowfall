import torch
import lhotse
from lhotse import load_manifest, fix_manifests

train_text=exp/data/lm_train_text
dev_text=exp/data/lm_dev_text
sups = load_manifest('exp/data/supervisions_safet_train.json')
f = open('exp/data/lm_train_text', 'w')
for s in sups:
    print(s.text, file=f)

sups = load_manifest('exp/data/supervisions_safet_dev_clean.json')
f = open('exp/data/lm_dev_text', 'w')
for s in sups:
    print(s.text, file=f)
