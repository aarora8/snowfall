#!/usr/bin/env bash

# Copyright 2020 Xiaomi Corporation (Author: Junbo Zhang)
# Apache 2.0
# Example of how to build L and G FST for K2. Most scripts of this example are copied from Kaldi.

set -eou pipefail

stage=5
if [ $stage -le 1 ]; then
  local/download_lm.sh "openslr.org/resources/11" data/local/lm
fi

if [ $stage -le 2 ]; then
  local/prepare_dict.sh data/local/lm data/local/dict_nosp
fi

if [ $stage -le 3 ]; then
  local/prepare_lang.sh \
    --position-dependent-phones false \
    data/local/dict_nosp \
    "<UNK>" \
    data/local/lang_tmp_nosp \
    data/lang_nosp

  echo "To load L:"
  echo "    Lfst = k2.Fsa.from_openfst(<string of data/lang_nosp/L.fst.txt>, acceptor=False)"
fi

if [ $stage -le 4 ]; then
  # Build G
  python3 -m kaldilm \
    --read-symbol-table="data/lang_nosp/words.txt" \
    --disambig-symbol='#0' \
    --max-order=1 \
    data/local/lm/lm_tgmed.arpa >data/lang_nosp/G_uni.fst.txt

  python3 -m kaldilm \
    --read-symbol-table="data/lang_nosp/words.txt" \
    --disambig-symbol='#0' \
    --max-order=3 \
    data/local/lm/lm_tgmed.arpa >data/lang_nosp/G.fst.txt

  python3 -m kaldilm \
    --read-symbol-table="data/lang_nosp/words.txt" \
    --disambig-symbol='#0' \
    --max-order=4 \
    data/local/lm/lm_fglarge.arpa >data/lang_nosp/G_4_gram.fst.txt

  echo ""
  echo "To load G:"
  echo "Use::"
  echo "  with open('data/lang_nosp/G.fst.txt') as f:"
  echo "    G = k2.Fsa.from_openfst(f.read(), acceptor=False)"
  echo ""
fi

if [ $stage -le 5 ]; then
  #python3 ./prepare.py
  utils/queue.pl --mem 30G --config conf/coe.conf exp/prepare.log ~/miniconda3/envs/k2/bin/python3 prepare.py
fi

if [ $stage -le 6 ]; then
  #ngpus=1
  #python3 -m torch.distributed.launch --nproc_per_node=$ngpus ./mmi_bigram_train.py --world_size $ngpus
  utils/queue.pl --mem 20G --gpu 1 --config conf/coe.conf exp/train.log ~/miniconda3/envs/k2/bin/python3 mmi_bigram_train.py
fi

if [ $stage -le 7 ]; then
  # python3 ./mmi_bigram_decode.py --epoch 9
  utils/queue.pl --mem 10G --gpu 1 --config conf/coe.conf exp/decode.log ~/miniconda3/envs/k2/bin/python3 mmi_bigram_decode.py --epoch 9
fi
