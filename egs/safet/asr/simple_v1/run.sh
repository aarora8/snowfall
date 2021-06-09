#!/usr/bin/env bash

# Copyright 2020 Xiaomi Corporation (Author: Junbo Zhang)
# Apache 2.0

# Example of how to build L and G FST for K2. Most scripts of this example are copied from Kaldi.

set -eou pipefail
. ./path.sh
# ./run.sh | tee local2/logfile/run_logfile.txt
#Prepare.py is independent
#Prepare_dict is independent
#Prepare_lang will run after prepare dict
#Prepare_lm will run after prepare.py
#Train_lm_srilm will run after prepare_lm
stage=0
if [ $stage -le 0 ]; then
  echo "Stage 0: Create train, dev and dev clean data directories"
  utils/queue.pl --mem 32G --config conf/coe.conf exp/prepare.log ~/miniconda3/envs/k2/bin/python3 prepare.py
  local/prepare_lm.py
fi

if [ $stage -le 1 ]; then
  echo "Stage 1: Create lexicon similar to librispeech"
  dst_dir=data/local/dict_nosp
  local/prepare_dict.sh
  local/text_to_phones.py $dst_dir/oov_text.txt $dst_dir/optional_silence.txt \
    $dst_dir/lexicon/lexicon_monophones_nosil.txt exp/data/lm_train_text \
    exp/data/lm_train_monotext exp/data/lm_train_bitext

  local/replace_biphone_with_monophone_from_lexicon.py exp/data/lm_train_bitext \
    $dst_dir/lexicon/lexicon_biphones_nosil.txt \
    $dst_dir/lexicon/lexicon_monobiphones_nosil.txt
fi
exit
if [ $stage -le 2 ]; then
  echo "Stage 2: Create the data/lang_nosp directory that has a specific HMM topolopy"
  local/prepare_lang.sh \
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
  utils/queue.pl --mem 32G --gpu 1 --config conf/coe.conf exp/train_lstm.log ~/miniconda3/envs/k2/bin/python3 mmi_bigram_train.py
fi
if [ $stage -le 5 ]; then
  echo "Stage 5: decode dev data directory with trained lstm model"
  utils/queue.pl --mem 10G --gpu 1 --config conf/coe.conf exp/decode_lstm.log ~/miniconda3/envs/k2/bin/python3 mmi_bigram_decode.py --epoch 9
fi

if [ $stage -le 6 ]; then
  echo "Stage 6: train conformer model with train and dev clean data directories"
  utils/queue.pl --mem 32G --gpu 1 --config conf/coe.conf exp/train_conformer_20.log ~/miniconda3/envs/k2/bin/python3 mmi_att_transformer_train.py
fi
if [ $stage -le 7 ]; then
  echo "Stage 7: decode dev data directory with trained conformer model"
  utils/queue.pl --mem 10G --gpu 1 --config conf/coe.conf exp/decode_conformer_20.log ~/miniconda3/envs/k2/bin/python3 mmi_att_transformer_decode.py --epoch 20
fi
