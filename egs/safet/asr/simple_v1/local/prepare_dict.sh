#!/usr/bin/env bash

dst_dir=data/local/dict
silence_phones=$dst_dir/silence_phones.txt
optional_silence=$dst_dir/optional_silence.txt
nonsil_phones=$dst_dir/nonsilence_phones.txt
lexicon_nosil=$dst_dir/lexicon/lexicon_nosil.txt

# get monophone lexicon from librispeech lexicon
mkdir -p $dst_dir/lexicon
wget -P $dst_dir/lexicon/ https://www.openslr.org/resources/11/librispeech-lexicon.txt
cat $dst_dir/lexicon/librispeech-lexicon.txt  | \
  perl -ne '($a, $b) = split " ", $_, 2; $b =~ s/[0-9]//g; print "$a $b";' > $lexicon_nosil

# Preparing phone lists
(echo SIL; echo SPN;) > $silence_phones
echo SIL > $optional_silence

# create biphone lexicon from monophone lexicon
local/get_phones_from_lexicon.py $lexicon_nosil $nonsil_phones

# add silence and oov words and phones to the combined lexicon to get final lexicon
(echo '!SIL SIL'; echo '<SPOKEN_NOISE> SPN'; echo '<UNK> SPN'; ) |\
cat - $lexicon_nosil | sort | uniq > $dst_dir/lexicon.txt

echo "Lexicon text file saved as: $dst_dir/lexicon.txt"
exit 0
