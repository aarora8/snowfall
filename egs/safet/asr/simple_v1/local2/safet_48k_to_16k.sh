#!/usr/bin/env bash

for wav_path in ls /export/corpora5/opensat_corpora/LDC2020E10/LDC2020E10_SAFE-T_Corpus_Speech_Recording_Audio_Training_Data_R2/data/audio/*.flac; do
  wav_id=$(echo "$wav_path" | cut -d"/" -f 9)
  wav_name=$(echo "$wav_id" | cut -d"." -f 1)
  echo $wav_id
  echo $wav_name
  flac -s -c -d $wav_path | sox - -b 16 -t wav -r 16000 -c 1 /export/c03/aarora8/snowfall/egs/safet/asr/simple_v1/corpora_data/LDC2020E10/${wav_name}.wav
done
