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
mkdir -p $dst_dir/lexicon
wget -P $dst_dir/lexicon/ https://www.openslr.org/resources/11/librispeech-lexicon.txt

cat $dst_dir/lexicon/librispeech-lexicon.txt  | \
  perl -ne '($a, $b) = split " ", $_, 2; $b =~ s/[0-9]//g; print "$a $b";' > $lexicon_monophones_nosil

awk '{for (i=2; i<=NF; ++i) { print $i; gsub(/[0-9]/, "", $i); print $i}}' $lexicon_monophones_nosil |\
  sort -u |\
  perl -e 'while(<>){
    chop; m:^([^\d]+)(\d*)$: || die "Bad phone $_";
    $phones_of{$1} .= "$_ "; }
    foreach $list (values %phones_of) {print $list . "\n"; } ' | sort \
    > $nonsil_monophones || exit 1;

local/get_biphone_lexicon.py $lexicon_monophones_nosil $nonsil_biphones $lexicon_biphones_nosil


echo "Preparing phone lists"
(echo SIL; echo SPN;) > $silence_phones
echo SIL > $optional_silence
echo '<UNK> SPN' > $oov_word_phone
cat $nonsil_biphones $nonsil_monophones | sort > $nonsil_phones

(echo '!SIL SIL'; echo '<SPOKEN_NOISE> SPN'; echo '<UNK> SPN'; ) |\
cat - $lexicon_biphones_nosil $lexicon_monophones_nosil | sort | uniq >$dst_dir/lexicon.txt
echo "Lexicon text file saved as: $dst_dir/lexicon.txt"

exit 0
