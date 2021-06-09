#!/usr/bin/env bash

dst_dir=data/local/dict_nosp
silence_phones=$dst_dir/silence_phones.txt
optional_silence=$dst_dir/optional_silence.txt
nonsil_monophones=$dst_dir/nonsilence_monophones.txt
nonsil_biphones=$dst_dir/nonsilence_biphones.txt
nonsil_phones=$dst_dir/nonsilence_phones.txt
lexicon_monophones_nosil=$dst_dir/lexicon/lexicon_monophones_nosil.txt
lexicon_biphones_nosil=$dst_dir/lexicon/lexicon_biphones_nosil.txt
oov_word_phone=$dst_dir/oov_text.txt


# get mono-phone lexicon from librispeech lexicon
mkdir -p $dst_dir/lexicon
wget -P $dst_dir/lexicon/ https://www.openslr.org/resources/11/librispeech-lexicon.txt
cat $dst_dir/lexicon/librispeech-lexicon.txt  | \
  perl -ne '($a, $b) = split " ", $_, 2; $b =~ s/[0-9]//g; print "$a $b";' > $lexicon_monophones_nosil


# Preparing phone lists
(echo SIL; echo SPN;) > $silence_phones
echo SIL > $optional_silence
echo '<UNK> SPN' > $oov_word_phone


# get non-silence monophones
local/get_phones_from_lexicon.py $lexicon_monophones_nosil $nonsil_monophones


# create biphone lexicon from monophone lexicon
local/get_biphone_lexicon.py $lexicon_monophones_nosil $nonsil_biphones $lexicon_biphones_nosil


# convert text to monophone text and biphone text
local/text_to_phones.py $dst_dir/oov_text.txt $dst_dir/optional_silence.txt \
    $dst_dir/lexicon/lexicon_monophones_nosil.txt exp/data/lm_train_text \
    exp/data/lm_train_monotext exp/data/lm_train_bitext


# replace biphones in the biphone lexicon which do not occur 
# in the biphone training text with monophones 
  local/replace_biphone_with_monophone_from_lexicon.py exp/data/lm_train_bitext \
    $dst_dir/lexicon/lexicon_biphones_nosil.txt \
    $dst_dir/lexicon/lexicon_monobiphones_nosil.txt


# get non-silence phones from $lexicon_monophones_nosil
# $dst_dir/lexicon/lexicon_monobiphones_nosil.txt
cat  $lexicon_monophones_nosil $dst_dir/lexicon/lexicon_monobiphones_nosil.txt \
  > $dst_dir/lexicon/lexicon_nonsil_combined.txt
local/get_phones_from_lexicon.py $dst_dir/lexicon/lexicon_nonsil_combined.txt $nonsil_phones


# add silence and oov words and phones to the lexicon to get final lexicon
(echo '!SIL SIL'; echo '<SPOKEN_NOISE> SPN'; echo '<UNK> SPN'; ) |\
cat - $dst_dir/lexicon/lexicon_nonsil_combined.txt | sort | uniq > $dst_dir/lexicon.txt


echo "Lexicon text file saved as: $dst_dir/lexicon.txt"
exit 0
