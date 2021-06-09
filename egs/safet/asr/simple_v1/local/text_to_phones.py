#!/usr/bin/env python

# Copyright    2017 Hossein Hadian
# Copyright    2021 Ashish Arora
# Apache 2.0

""" This reads a text file such as (data/train/text), and converts the word
    transcriptions to monophone and biphone transcriptions using the
    provided lexicon.
"""
from __future__ import print_function
import argparse
import os
import copy

parser = argparse.ArgumentParser(description="""creates left bi-phone lexicon from monophone lexicon""")
parser.add_argument('oov_text', type=str, help='File name of a file that contains the'
                    'lexicon with monophones. Each line must be: <word> <phone1> <phone2> ...')
parser.add_argument('optional_silence', type=str, help='Output file that contains'
                    'non-silence left bi-phones')
parser.add_argument('monophone_lexicon', type=str, help='Output file that'
                    'contains left bi-phone lexicon. Each line must be: <word> <biphone1> <biphone2> ...')
parser.add_argument('text', type=str, help='Output file that'
                    'contains left bi-phone lexicon. Each line must be: <word> <biphone1> <biphone2> ...')
parser.add_argument('output_monotext', type=str, help='Output file that'
                    'contains left bi-phone lexicon. Each line must be: <word> <biphone1> <biphone2> ...')
parser.add_argument('output_bitext', type=str, help='Output file that'
                    'contains left bi-phone lexicon. Each line must be: <word> <biphone1> <biphone2> ...')
args = parser.parse_args()
# oov word and silence phone
oov_text = open(args.oov_text, 'r', encoding='utf8').readline().strip()
oov_word = oov_text.strip().split()[0]
oov_phone = oov_text.strip().split()[1]
sil_phone = open(args.optional_silence, 'r', encoding='utf8').readline().strip()
lexicon = dict()
with open(args.monophone_lexicon) as f:
    for line in f:
        parts = line.strip().split()
        lexicon[parts[0]] = parts[1:]

phonetranscription = list()
text_handle = open(args.output_monotext, 'w', encoding='utf8')
for line in open(args.text):
    line = line.strip().split()
    word_trans = line   # word-level transcription
    phone_trans = []    # phone-level transcription
    for i in range(len(word_trans)):
        word = word_trans[i]
        if word not in lexicon:
            pronunciation = list(oov_phone.split(" "))
        else:
            pronunciation = copy.deepcopy(lexicon[word])
        phone_trans += pronunciation
        phone_trans.append(sil_phone)
    phonetranscription.append(phone_trans)
    text_handle.write(" ".join(phone_trans) + '\n')

biphonetranscription = list()
text_handle = open(args.output_bitext, 'w', encoding='utf8')
for line in phonetranscription:
    prev_phone = ''
    biphone_trans = []
    for phone in line:
        if prev_phone == sil_phone or prev_phone == oov_phone:
            prev_phone = ''
        if not prev_phone:
            new_phone = prev_phone + '_' + phone
        else:
            new_phone = phone
        prev_phone = phone
        if phone == sil_phone:
            biphone_trans.append(sil_phone)
        elif phone == oov_phone:
            biphone_trans.append(oov_phone)
        else:
            biphone_trans.append(new_phone)

    biphonetranscription.append(biphone_trans)
    text_handle.write(" ".join(biphone_trans) + '\n')
