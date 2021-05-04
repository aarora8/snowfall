#!/usr/bin/env bash

# Copyright 2020 Xiaomi Corporation (Author: Junbo Zhang)
# Apache 2.0

# Example of how to build L and G FST for K2. Most scripts of this example are copied from Kaldi.

set -eou pipefail
[ -f path.sh ] && . ./path.sh
# ./run.sh | tee exp/logfile.txt
stage=4
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
  python3 ./prepare.py
  #utils/queue.pl --mem 30G train.log /home/aaror/miniconda3/envs/k2/bin/python3 prepare.py
fi

if [ $stage -le 3 ]; then
  echo "LM preparation"
  local2/prepare_lm.py
  local2/train_lm_srilm.sh
  gunzip -c data/local/lm/lm.gz >data/local/lm/lm_tgmed.arpa

  # Build G
  python3 -m kaldilm \
    --read-symbol-table="data/lang_nosp/words.txt" \
    --disambig-symbol='#0' \
    --max-order=3 \
    data/local/lm/lm_tgmed.arpa >data/lang_nosp/G.fst.txt
fi

if [ $stage -le 4 ]; then
  ngpus=1
  python3 -m torch.distributed.launch --nproc_per_node=$ngpus ./mmi_bigram_train_1b.py --world_size $ngpus
fi

if [ $stage -le 5 ]; then
  python3 ./mmi_bigram_decode.py --epoch 9
fi
