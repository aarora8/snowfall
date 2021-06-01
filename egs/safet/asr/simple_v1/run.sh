#!/usr/bin/env bash

# Copyright 2020 Xiaomi Corporation (Author: Junbo Zhang)
# Apache 2.0

# Example of how to build L and G FST for K2. Most scripts of this example are copied from Kaldi.

set -eou pipefail
. ./path.sh
# ./run.sh | tee local2/logfile/run_logfile.txt
# utils/queue.pl --mem 10G --gpu 1 --config conf/coe.conf decode.log /home/hltcoe/aarora/miniconda3/envs/k2/bin/python3 mmi_bigram_decode.py
stage=2
if [ $stage -le 0 ]; then
  mkdir -p exp/data/
  local2/prepare_dict.sh
fi

if [ $stage -le 1 ]; then
  local/prepare_lang.sh \
    data/local/dict_nosp \
    "<UNK>" \
    data/local/lang_tmp_nosp \
    data/lang_nosp
fi

if [ $stage -le 2 ]; then
  #python3 ./prepare.py
  utils/queue.pl --mem 32G --config conf/coe.conf exp/prepare.log ~/miniconda3/envs/k2/bin/python3 prepare.py
fi

#if [ $stage -le 3 ]; then
#  echo "LM preparation"
#  local2/prepare_lm.py
#  local2/train_lm_srilm.sh
#  gunzip -c data/local/lm/lm.gz >data/local/lm/lm_tgmed.arpa
#
#  # Build G
#  python3 -m kaldilm \
#    --read-symbol-table="data/lang_nosp/words.txt" \
#    --disambig-symbol='#0' \
#    --max-order=3 \
#    data/local/lm/lm_tgmed.arpa >data/lang_nosp/G.fst.txt
#fi

if [ $stage -le 4 ]; then
  ngpus=1
  #python3 -m torch.distributed.launch --nproc_per_node=$ngpus ./mmi_bigram_train_1b.py --world_size $ngpus
  utils/queue.pl --mem 32G --gpu 1 --config conf/coe.conf exp/train1b.log ~/miniconda3/envs/k2/bin/python3 mmi_bigram_train.py
fi
if [ $stage -le 5 ]; then
  #python3 ./mmi_bigram_decode.py --epoch 9
  utils/queue.pl --mem 10G --gpu 1 --config conf/coe.conf exp/decode.log ~/miniconda3/envs/k2/bin/python3 mmi_bigram_decode.py --epoch 9
fi
