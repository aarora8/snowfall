#!/usr/bin/env python

import os
import argparse
parser = argparse.ArgumentParser(description="""creates left bi-phone lexicon from monophone lexicon""")
parser.add_argument('lexicon', type=str, help='File name of a file that contains the'
                    'lexicon with monophones. Each line must be: <word> <phone1> <phone2> ...')
parser.add_argument('nonsilence_pd_phones', type=str, help='Output file that contains'
                    'non-silence left bi-phones')
parser.add_argument('pd_lexicon', type=str, help='Output file that'
                    'contains left bi-phone lexicon. Each line must be: <word> <biphone1> <biphone2> ...')

def main():

    args = parser.parse_args()
    word2monophones = dict()
    lexicon_handle = open(args.lexicon, 'r', encoding='utf8')
    lexicon_data = lexicon_handle.read().strip().split("\n")
    for line in lexicon_data:
        parts = line.strip().split()
        if parts[0] not in word2monophones:
            word2monophones[parts[0]] = list()
        word2monophones[parts[0]].append(parts[1:])

    output_nonsilence_pd_phones_handle = open(args.nonsilence_pd_phones, 'w', encoding='utf8')
    output_pd_lexicon_handle = open(args.pd_lexicon, 'w', encoding='utf8')
    nonsilbiphones_dict = dict()
    for word in word2monophones:
        for mono_pronunciation in word2monophones[word]:
            # (_B, _E, _S, _I)
            phone_sequence = []
            if len(mono_pronunciation) == 1:
                phone = mono_pronunciation[0]
                phone = phone + '_B'
                phone_sequence.append(phone)
                if phone not in nonsilbiphones_dict:
                    nonsilbiphones_dict[phone] = phone
                    output_nonsilence_pd_phones_handle.write(phone + '\n')

            else:
                phone = mono_pronunciation[0]
                phone = phone + '_B'
                phone_sequence.append(phone)
                if phone not in nonsilbiphones_dict:
                    nonsilbiphones_dict[phone] = phone
                    output_nonsilence_pd_phones_handle.write(phone + '\n')

                for phone in mono_pronunciation[1:]:
                    new_phone = phone
                    phone_sequence.append(new_phone)
                    if new_phone not in nonsilbiphones_dict:
                        nonsilbiphones_dict[new_phone] = new_phone
                        output_nonsilence_pd_phones_handle.write(new_phone + '\n')

            phone_sequence = ' '.join(phone_sequence)
            pronunciation = word + ' ' + phone_sequence
            output_pd_lexicon_handle.write(pronunciation + '\n')


if __name__ == '__main__':
    main()
