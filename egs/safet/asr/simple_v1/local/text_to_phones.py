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
parser.add_argument('oov_word', type=str, help='File name of a file that contains the'
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
# oov word and silence phone
oov_word = open(args.oov_word, 'r', encoding='utf8').readline().strip()
sil_phone = open(args.optional_silence, 'r', encoding='utf8').readline().strip()
lexicon = dict()
with open(args.monophone_lexicon) as f:
    for line in f:
        parts = line.strip().split()
        lexicon[parts[0]] = parts[1:]

utt2phonetranscription = dict()
text_handle = open(args.output_monotext, 'w', encoding='utf8')
for line in open(args.text):
    line = line.strip().split()
    uttid = line[0]
    word_trans = line[1:]   # word-level transcription
    phone_trans = []        # phone-level transcription
    for i in range(len(word_trans)):
        word = word_trans[i]
        if word not in lexicon:
            pronunciation = lexicon[oov_word]
        else:
            pronunciation = copy.deepcopy(lexicon[word])
        phone_trans += pronunciation 
        phone_trans.append(sil_phone)  
    utt2phonetranscription[uttid] = phone_trans
    text_handle.write(uttid + " " + " ".join(phone_trans) + '\n')

utt2biphonetranscription = dict()
text_handle = open(args.output_bitext, 'w', encoding='utf8')
for uttid in utt2phonetranscription:
    prev_phone = '0'
    phone_sequence = []
    for phone in utt2phonetranscription[uttid]:
        if prev_phone == sil_phone or prev_phone == lexicon[oov_word][0]:
            prev_phone = '0'
        new_phone = prev_phone + '_' + phone
        prev_phone = phone
        if phone == sil_phone:
            phone_sequence.append(sil_phone)
        elif phone == lexicon[oov_word][0]:
            phone_sequence.append(lexicon[oov_word][0])
        else:
            phone_sequence.append(new_phone)            
    utt2biphonetranscription[uttid] = phone_sequence
    text_handle.write(uttid + " " + " ".join(phone_trans) + '\n')
