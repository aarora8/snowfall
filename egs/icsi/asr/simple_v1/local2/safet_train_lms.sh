#!/usr/bin/env bash

# To be run from one directory above this script.
. ./path.sh

text=data/local/train/text
lexicon=data/local/dict_nosp/lexicon.txt

for f in "$text" "$lexicon"; do
  [ ! -f $x ] && echo "$0: No such file $f" && exit 1
done

# This script takes no arguments.  It assumes you have already run
# aishell_data_prep.sh.
# It takes as input the files
# data/local/train/text
# data/local/dict_nosp/lexicon.txt
dir=data/local/lm
mkdir -p $dir

kaldi_lm=$(which train_lm.sh)
if [ -z $kaldi_lm ]; then
  echo "$0: train_lm.sh is not found. That might mean it's not installed"
  echo "$0: or it is not added to PATH"
  echo "$0: Please use the following commands to install it"
  echo "  git clone https://github.com/danpovey/kaldi_lm.git"
  echo "  cd kaldi_lm"
  echo "  make -j"
  echo "Then add the path of kaldi_lm to PATH and rerun $0"
  exit 1
fi

cleantext=$dir/text.no_oov

cat $text | awk -v lex=$lexicon 'BEGIN{while((getline<lex) >0){ seen[$1]=1; } }
  {for(n=1; n<=NF;n++) {  if (seen[$n]) { printf("%s ", $n); } else {printf("<UNK> ");} } printf("\n");}' \
  >$cleantext || exit 1

cat $cleantext | awk '{for(n=2;n<=NF;n++) print $n; }' | sort | uniq -c |
  sort -nr >$dir/word.counts || exit 1

# Get counts from acoustic training transcripts, and add  one-count
# for each word in the lexicon (but not silence, we don't want it
# in the LM-- we'll add it optionally later).
cat $cleantext | awk '{for(n=2;n<=NF;n++) print $n; }' |
  cat - <(grep -w -v '!SIL' $lexicon | awk '{print $1}') |
  sort | uniq -c | sort -nr >$dir/unigram.counts || exit 1

# note: we probably won't really make use of <UNK> as there aren't any OOVs
cat $dir/unigram.counts | awk '{print $2}' | get_word_map.pl "<s>" "</s>" "<UNK>" >$dir/word_map ||
  exit 1

# note: ignore 1st field of train.txt, it's the utterance-id.
cat $cleantext | awk -v wmap=$dir/word_map 'BEGIN{while((getline<wmap)>0)map[$1]=$2;}
  { for(n=2;n<=NF;n++) { printf map[$n]; if(n<NF){ printf " "; } else { print ""; }}}' | gzip -c >$dir/train.gz ||
  exit 1

train_lm.sh --arpa --lmtype 3gram-mincount $dir || exit 1
exit 0
