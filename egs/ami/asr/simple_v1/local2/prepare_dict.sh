#!/usr/bin/env bash

dst_dir=data/local/dict_nosp
silence_phones=$dst_dir/silence_phones.txt
optional_silence=$dst_dir/optional_silence.txt
nonsil_phones=$dst_dir/nonsilence_phones.txt
lexicon_raw_nosil=$dst_dir/lexicon/librispeech-lexicon.txt

mkdir -p $dst_dir/lexicon
wget -P $dst_dir/lexicon/ https://www.openslr.org/resources/11/librispeech-lexicon.txt

echo "Preparing phone lists"
(echo SIL; echo SPN;) > $silence_phones
echo SIL > $optional_silence

# nonsilence phones; on each line is a list of phones that correspond
# really to the same base phone.
awk '{for (i=2; i<=NF; ++i) { print $i; gsub(/[0-9]/, "", $i); print $i}}' $lexicon_raw_nosil |\
  sort -u |\
  perl -e 'while(<>){
    chop; m:^([^\d]+)(\d*)$: || die "Bad phone $_";
    $phones_of{$1} .= "$_ "; }
    foreach $list (values %phones_of) {print $list . "\n"; } ' | sort \
    > $nonsil_phones || exit 1;

(echo '!SIL SIL'; echo '<SPOKEN_NOISE> SPN'; echo '<UNK> SPN'; ) |\
cat - $lexicon_raw_nosil | sort | uniq >$dst_dir/lexicon.txt
echo "Lexicon text file saved as: $dst_dir/lexicon.txt"

exit 0
