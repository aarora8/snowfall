#!/usr/bin/env bash

dst_dir=data/local/dict_nosp
silence_phones=$dst_dir/silence_phones.txt
optional_silence=$dst_dir/optional_silence.txt
nonsil_phones=$dst_dir/nonsilence_phones.txt
lexicon_nosil=$dst_dir/lexicon/lexicon_nosil.txt
train_text=exp/data/lm_train_text

mkdir -p $dst_dir
local/get_phones_from_lexicon.py corpora_data/data/local/lexicon.txt $nonsil_phones data/local/lexicon.txt

echo "Preparing phone lists"
echo SIL > $silence_phones
echo SIL > $optional_silence


(echo '!SIL SIL'; echo '<UNK> SIL'; echo '<Noise/> SIL'; ) |\
cat - data/local/lexicon.txt | sort | uniq >$dst_dir/lexicon.txt
echo "Lexicon text file saved as: $dst_dir/lexicon.txt"

exit 0
