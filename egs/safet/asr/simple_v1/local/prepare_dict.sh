#!/usr/bin/env bash

dst_dir=data/local/dict_nosp
silence_phones=$dst_dir/silence_phones.txt
optional_silence=$dst_dir/optional_silence.txt
nonsil_monophones=$dst_dir/nonsilence_monophones.txt
nonsil_biphones=$dst_dir/nonsilence_biphones.txt
nonsil_phones=$dst_dir/nonsilence_phones.txt
lexicon_monophones_nosil=$dst_dir/lexicon/lexicon_monophones_nosil.txt
lexicon_biphones_nosil=$dst_dir/lexicon/lexicon_biphones_nosil.txt
lexicon_monobiphones_nosil=$dst_dir/lexicon/lexicon_monobiphones_nosil.txt
lexicon_combined_nosil=$dst_dir/lexicon/lexicon_combined_nosil.txt
oov_word_phone=$dst_dir/oov_text.txt
train_text=exp/data/lm_train_text

# get monophone lexicon from librispeech lexicon
mkdir -p $dst_dir/lexicon
wget -P $dst_dir/lexicon/ https://www.openslr.org/resources/11/librispeech-lexicon.txt
cat $dst_dir/lexicon/librispeech-lexicon.txt  | \
  perl -ne '($a, $b) = split " ", $_, 2; $b =~ s/[0-9]//g; print "$a $b";' > $lexicon_monophones_nosil


# Preparing phone lists
(echo SIL; echo SPN;) > $silence_phones
echo SIL > $optional_silence
echo '<UNK> SPN' > $oov_word_phone


# create biphone lexicon from monophone lexicon
local/get_biphone_lexicon.py $lexicon_monophones_nosil $nonsil_biphones $lexicon_biphones_nosil


# convert words in the text to monophone sequence (exp/data/lm_train_monotext)
# convert words in the text to biphone sequence (exp/data/lm_train_bitext)
local/text_to_phones.py $dst_dir/oov_text.txt $dst_dir/optional_silence.txt \
  $lexicon_monophones_nosil $train_text \
  exp/data/lm_train_monotext exp/data/lm_train_bitext


# replace biphones in the biphone lexicon which do not occur 
# in the biphone training text with monophones 
local/replace_biphone_with_monophone_from_lexicon.py exp/data/lm_train_bitext \
  $lexicon_biphones_nosil $lexicon_monobiphones_nosil


# combine monophone lexicon and monobiphone lexicon
cat  $lexicon_monophones_nosil $lexicon_monobiphones_nosil |\
  sort | uniq > $lexicon_combined_nosil
# get non-silence phones from this lexicon
# Note: non-silence phones can be less than non-silence biphones, since some of the biphones
# are not present in the training data
local/get_phones_from_lexicon.py $lexicon_combined_nosil $nonsil_phones


# add silence and oov words and phones to the combined lexicon to get final lexicon
(echo '!SIL SIL'; echo '<SPOKEN_NOISE> SPN'; echo '<UNK> SPN'; ) |\
cat - $lexicon_combined_nosil | sort | uniq > $dst_dir/lexicon.txt


echo "Lexicon text file saved as: $dst_dir/lexicon.txt"
exit 0
