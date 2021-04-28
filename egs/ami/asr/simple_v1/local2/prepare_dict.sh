#!/usr/bin/env bash
# Prepares the dictionary

lm_dir=$1
dst_dir=$2

mkdir -p data/local/dict_nosp
curl http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b > data/local/cmudict-0.7b

# add cmu dict words in lowercase in the lexicon
uconv -f iso-8859-1 -t utf-8 data/local/cmudict-0.7b| grep -v ';;' | sed 's/([0-9])//g' | \
  perl -ne '($a, $b) = split " ", $_, 2; $b =~ s/[0-9]//g; $a = lc $a; print "$a $b";' > data/local/lexicon.txt

# add SIL, <UNK>, %uh, {breath}, {lipsmack}, {laugh}, {cough}, <noise> words in the lexicon 
# <UNK> word is mapped to <unk> phone
# {breath}, {lipsmack}, {laugh}, {cough}, <noise> are mapped to <noise>
echo -e "SIL <sil>\n<UNK> <unk>" |  cat - local2/safet_hesitations.txt data/local/lexicon.txt | sort -u > data/local/dict_nosp/lexicon1.txt

# add some specific words, those are only with 100 missing occurences or more
# add mm hmm mm-hmm  words in the lexicon
( echo "mm M"; \
  echo "hmm HH M"; \
  echo "mm-hmm M HH M" ) | cat - data/local/dict_nosp/lexicon1.txt \
     | sort -u > data/local/dict_nosp/lexicon2.txt

# Add prons for laughter, noise, oov as phones in the silence phones
for w in laughter noise oov; do echo $w; done > data/local/dict_nosp/silence_phones.txt

# add [laughter], [noise], [oov] words in the lexicon
for w in `grep -v sil data/local/dict_nosp/silence_phones.txt`; do
  echo "[$w] $w"
done | cat - data/local/dict_nosp/lexicon2.txt > data/local/dict_nosp/lexicon.txt

# Add <sil>, <unk>, <noise>, <hes> as phones in the silence phones
echo -e "SIL <sil>\n<UNK> <unk>" |  cat - local2/safet_hesitations.txt | cut -d ' ' -f 2- | sed 's/ /\n/g' | \
  sort -u | sed '/^ *$/d' >> data/local/dict_nosp/silence_phones.txt

echo '<UNK>' > data/local/dict_nosp/oov.txt

echo '<sil>' > data/local/dict_nosp/optional_silence.txt

cat data/local/lexicon.txt | cut -d ' ' -f 2- | sed 's/ /\n/g' | \
  sort -u | sed '/^ *$/d' > data/local/dict_nosp/nonsilence_phones.txt

exit 0
