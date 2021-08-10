#!/usr/bin/env bash
set -eou pipefail
. ./path.sh
# ./run.sh | tee run.log
stage=0
if [ $stage -le 0 ]; then
  echo "Stage 0: Create train, dev and dev clean data directories"
  local/queue.pl --mem 32G --config local/coe.conf exp/prepare.log ~/miniconda3/envs/icef/bin/python3 prepare.py
fi

if [ $stage -le 1 ]; then
  echo "Stage 1: Create lexicon similar to librispeech"
  local/prepare_dict.sh
fi

if [ $stage -le 2 ]; then
  echo "Stage 2: Create the data/lang_nosp directory that has a specific HMM topolopy"
  local/prepare_lang.sh \
    --position-dependent-phones false \
    data/local/dict \
    "<UNK>" \
    data/local/lang_tmp \
    data/lang
fi

if [ $stage -le 3 ]; then
  echo "Stage 3: Create lm from train and dev clean text"
  local/prepare_lm.sh
  gunzip -c data/local/lm/lm.gz >data/local/lm/lm_tgmed.arpa

  # Build G
  python3 -m kaldilm \
    --read-symbol-table="data/lang/words.txt" \
    --disambig-symbol='#0' \
    --max-order=3 \
    data/local/lm/lm_tgmed.arpa >data/lang/G.fst.txt
fi

if [ $stage -le 4 ]; then
  # this stage takes about 3 minutes
  mkdir -p data/lm
  if [ ! -f data/lm/P.arpa ]; then
    echo "Generating data/lm/P.arpa"
    ./local/add_silence_to_transcript.py \
      --transcript exp/data/lm_train_text \
      --sil-word "!SIL" \
      --sil-prob 0.5 \
      --seed 20210629 \
      > data/lm/transcript_with_sil.txt

    ./local/convert_transcript_to_corpus.py \
      --transcript data/lm/transcript_with_sil.txt \
      --lexicon data/local/dict/lexicon.txt \
      --oov "<UNK>" \
      > data/lm/corpus.txt

    ./local/make_kn_lm.py \
      -ngram-order 2 \
      -text data/lm/corpus.txt \
      -lm data/lm/P.arpa
  fi
fi

if [ $stage -le 5 ]; then
  if [ ! -f data/lang/P.fst.txt ]; then
    python3 -m kaldilm \
      --read-symbol-table="data/lang/phones.txt" \
      --disambig-symbol='#0' \
      --max-order=2 \
      data/lm/P.arpa > data/lang/P.fst.txt
  fi
fi


if [ $stage -le 4 ]; then
  echo "Stage 4: train lstm model with train and dev clean data directories"
  local/queue.pl --mem 32G --gpu 1 --config local/coe.conf exp/train_lstm.log ~/miniconda3/envs/icef/bin/python3 mmi_bigram_train.py
fi
if [ $stage -le 5 ]; then
  echo "Stage 5: decode dev data directory with trained lstm model"
  local/queue.pl --mem 10G --gpu 1 --config local/coe.conf exp/decode_lstm.log ~/miniconda3/envs/icef/bin/python3 mmi_bigram_decode.py --epoch 9
fi

if [ $stage -le 6 ]; then
  echo "Stage 6: train conformer model with train and dev clean data directories"
  local/queue.pl --mem 32G --gpu 1 --config local/coe.conf exp/train_conformer_60.log ~/miniconda3/envs/icef/bin/python3 mmi_att_transformer_train.py
fi
if [ $stage -le 7 ]; then
  echo "Stage 7: decode dev data directory with trained conformer model"
  local/queue.pl --mem 10G --gpu 1 --config local/coe.conf exp/decode_conformer_60.log ~/miniconda3/envs/icef/bin/python3 mmi_att_transformer_decode.py --epoch 60
fi

