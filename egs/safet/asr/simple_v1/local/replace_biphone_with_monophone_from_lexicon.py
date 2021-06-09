#!/usr/bin/env python

import os
import argparse
parser = argparse.ArgumentParser(description="""creates left bi-phone lexicon from monophone lexicon""")
parser.add_argument('bitext', type=str, help='File name of a file that contains the'
                    'lexicon with monophones. Each line must be: <word> <phone1> <phone2> ...')
parser.add_argument('bilexicon', type=str, help='Output file that contains'
                    'non-silence left bi-phones')
parser.add_argument('output_monobi_lexicon', type=str, help='Output file that'
                    'contains left bi-phone lexicon. Each line must be: <word> <biphone1> <biphone2> ...')

def main():
    args = parser.parse_args()
    text_handle = open(args.output_monobi_lexicon, 'w', encoding='utf8')
    biphone_text_handle = open(args.bitext, 'r', encoding='utf8')
    biphones_text_data = biphone_text_handle.read().strip().split("\n")
    biphone_train_count = dict()
    for line in biphones_text_data:
        biphones = line.split(" ")[1:]
        for biphone in biphones:
            biphone_train_count[biphone] = 1

    biphone_handle = open(args.bilexicon, 'r', encoding='utf8')
    biphones_lexicon = biphone_handle.read().strip().split("\n")
    word2biphone = dict()
    for word_biphone in biphones_lexicon:
        word_biphone = word_biphone.strip().split(" ")
        word = word_biphone[0]
        word2biphone[word] = list()
        for biphone in word_biphone[1:]:
            if biphone not in biphone_train_count:
                monophone = biphone.split('_')[1]
                word2biphone[word].append(monophone)
            else:
               word2biphone[word].append(biphone)
        text_handle.write(word + " " + " ".join(word2biphone[word]) + '\n')


if __name__ == '__main__':
    main()
