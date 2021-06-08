#!/usr/bin/env python

# Copyright    2017 Hossein Hadian
# Apache 2.0


""" This reads data/train/text from standard input, converts the word transcriptions
    to phone transcriptions using the provided lexicon,
    and writes them to standard output.
"""
from __future__ import print_function

import argparse
from os.path import join
import sys
import copy
import random

# oov_word
oov_word = open('lang_nosp/oov.txt').readline().strip()
sil = open('lang_nosp/phones/optional_silence.txt').readline().strip()
# load the lexicon
lexicon = dict()
with open("dict_nosp/lexicon.txt") as f:
    for line in f:
        line = line.strip()
        parts = line.split()
        lexicon[parts[0]] = parts[1:]

phone_transcription_dict = dict()
for line in open('/Users/ashisharora/Desktop/corpora/kaldi_data_safet/e2e/train_cleaned/text'):
    line = line.strip().split()
    key = line[0]
    word_trans = line[1:]   # word-level transcription
    phone_trans = []        # phone-level transcription
    for i in range(len(word_trans)):
        word = word_trans[i]
        if word not in lexicon:
            pronunciation = lexicon[oov_word]
        else:
            pronunciation = copy.deepcopy(lexicon[word])
        phone_trans += pronunciation 
        phone_trans.append(sil)  
    phone_transcription_dict[key] = phone_trans


text_file = join('/Users/ashisharora/Desktop/corpora/kaldi_data_safet/e2e/output/text_to_phones.txt')
text_fh = open(text_file, 'w')
for key in phone_transcription_dict:
    text_fh.write(key + " " + " ".join(phone_transcription_dict[key]) + '\n')

biphone_transcription_dict = dict()
for key in phone_transcription_dict:
    prev_phone = '0'
    phone_sequence = []
    for phone in phone_transcription_dict[key]:
        if prev_phone == sil or prev_phone == lexicon[oov_word][0]:
            prev_phone = '0'
        new_phone = prev_phone + '_' + phone
        prev_phone = phone
        if phone == sil:
            phone_sequence.append(phone)
        elif phone == lexicon[oov_word][0]:
            phone_sequence.append(phone)
        else:
            phone_sequence.append(new_phone)            
    biphone_transcription_dict[key] = phone_sequence

text_file = join('/Users/ashisharora/Desktop/corpora/kaldi_data_safet/e2e/output/text_to_biphones.txt')
text_fh = open(text_file, 'w')
for key in biphone_transcription_dict:
    # print(biphone_transcription_dict[key])
    text_fh.write(key + " " + " ".join(biphone_transcription_dict[key]) + '\n')
        
