#!/usr/bin/env bash
# Prepares the dictionary

lm_dir=$1
dst_dir=$2

mkdir -p data/local/dict_nosp
curl http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b > data/local/cmudict-0.7b

# add cmu dict words in lowercase in the lexicon
uconv -f iso-8859-1 -t utf-8 data/local/cmudict-0.7b| grep -v ';;' | sed 's/([0-9])//g' | \
  perl -ne '($a, $b) = split " ", $_, 2; $b =~ s/[0-9]//g; $a = lc $a; print "$a $b";' > data/local/lexicon.txt

echo -e "SIL <sil>\n<UNK> <unk>" |  cat - data/local/lexicon.txt | sort -u > data/local/dict_nosp/lexicon.txt

echo '<sil>' > data/local/dict_nosp/silence_phones.txt
echo '<unk>' >> data/local/dict_nosp/silence_phones.txt

echo '<sil>' > data/local/dict_nosp/optional_silence.txt

echo '<UNK>' > data/local/dict_nosp/oov.txt

cat data/local/lexicon.txt | cut -d ' ' -f 2- | sed 's/ /\n/g' | \
  sort -u | sed '/^ *$/d' > data/local/dict_nosp/nonsilence_phones.txt

exit 0
