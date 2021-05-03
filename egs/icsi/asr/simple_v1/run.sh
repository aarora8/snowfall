#!/usr/bin/env bash

# Copyright 2020 Xiaomi Corporation (Author: Junbo Zhang)
# Apache 2.0

# Example of how to build L and G FST for K2. Most scripts of this example are copied from Kaldi.

set -eou pipefail
[ -f path.sh ] && . ./path.sh

stage=5
if [ $stage -le 0 ]; then
  local2/prepare_dict.sh data/local/lm data/local/dict_nosp
fi

if [ $stage -le 1 ]; then
  local/prepare_lang.sh \
    --position-dependent-phones false \
    data/local/dict_nosp \
    "<UNK>" \
    data/local/lang_tmp_nosp \
    data/lang_nosp
fi

if [ $stage -le 2 ]; then
  echo "LM preparation"
  local2/safet_train_lms.sh
  gunzip -c data/local/lm/3gram-mincount/lm_unpruned.gz >data/local/lm/lm_tgmed.arpa

  # Build G
  python3 -m kaldilm \
    --read-symbol-table="data/lang_nosp/words.txt" \
    --disambig-symbol='#0' \
    --max-order=3 \
    data/local/lm/lm_tgmed.arpa >data/lang_nosp/G.fst.txt
fi

if [ $stage -le 4 ]; then
  python3 ./prepare.py
fi

if [ $stage -le 5 ]; then
  ngpus=1
  python3 -m torch.distributed.launch --nproc_per_node=$ngpus ./mmi_bigram_train.py --world_size $ngpus
fi

if [ $stage -le 6 ]; then
  python3 ./mmi_bigram_decode.py --epoch 9
fi