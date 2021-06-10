#!/usr/bin/env bash

# Copyright 2020 Xiaomi Corporation (Author: Junbo Zhang)
# Apache 2.0

# Example of how to build L and G FST for K2. Most scripts of this example are copied from Kaldi.

set -eou pipefail
. ./path.sh
# ./run.sh | tee local2/logfile/run_logfile.txt
#prepare.py is independent
#prepare_dict will run after prepare.py
#prepare_lang will run after prepare dict
#train_lm_srilm will run after prepare.py
stage=1
if [ $stage -le 0 ]; then
  echo "Stage 0: Create train, dev and dev clean data directories"
  utils/queue.pl --mem 32G --config local/coe.conf exp/prepare.log ~/miniconda3/envs/k2/bin/python3 prepare.py
fi

if [ $stage -le 1 ]; then
  echo "Stage 1: Create lexicon similar to librispeech"
  local/prepare_dict.sh
fi

if [ $stage -le 2 ]; then
  echo "Stage 2: Create the data/lang_nosp directory that has a specific HMM topolopy"
  local/prepare_lang.sh \
    --position-dependent-phones false \
    data/local/dict_nosp \
    "<UNK>" \
    data/local/lang_tmp_nosp \
    data/lang_nosp
fi

if [ $stage -le 3 ]; then
  echo "Stage 3: Create lm from train and dev clean text"
  local/train_lm_srilm.sh
  gunzip -c data/local/lm/lm.gz >data/local/lm/lm_tgmed.arpa

  # Build G
  python3 -m kaldilm \
    --read-symbol-table="data/lang_nosp/words.txt" \
    --disambig-symbol='#0' \
    --max-order=3 \
    data/local/lm/lm_tgmed.arpa >data/lang_nosp/G.fst.txt
fi

if [ $stage -le 4 ]; then
  echo "Stage 4: train lstm model with train and dev clean data directories"
  utils/queue.pl --mem 32G --gpu 1 --config local/coe.conf exp/train_tdnn.log ~/miniconda3/envs/k2/bin/python3 mmi_bigram_train.py
fi
if [ $stage -le 5 ]; then
  echo "Stage 5: decode dev data directory with trained lstm model"
  utils/queue.pl --mem 10G --gpu 1 --config local/coe.conf exp/decode_lstm.log ~/miniconda3/envs/k2/bin/python3 mmi_bigram_decode.py --epoch 9
fi
exit
if [ $stage -le 6 ]; then
  echo "Stage 6: train conformer model with train and dev clean data directories"
  utils/queue.pl --mem 32G --gpu 1 --config local/coe.conf exp/train_conformer_25.log ~/miniconda3/envs/k2/bin/python3 mmi_att_transformer_train.py
fi
if [ $stage -le 7 ]; then
  echo "Stage 7: decode dev data directory with trained conformer model"
  utils/queue.pl --mem 10G --gpu 1 --config local/coe.conf exp/decode_conformer_25.log ~/miniconda3/envs/k2/bin/python3 mmi_att_transformer_decode.py --epoch 30
fi
