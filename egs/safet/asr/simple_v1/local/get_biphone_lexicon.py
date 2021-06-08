#!/usr/bin/env python
import os


def get_lexicon_details():
    # AMI_ES2011a_H00 1113.845
    # <reco-id> <dur>
    # AMI_ES2011a_H00_FEE041_0003427_0003714 AMI_ES2011a_H00 34.27 37.14
    # <utt-id> <reco-id> <seg-beg> <seg-end>
    lexicon_dict= dict()
    for line in open('/Users/ashisharora/Desktop/corpora/kaldi_data_safet/e2e/dict_nosp/lexicon.txt'):
        parts = line.strip().split()
        word = parts[0]
        lexicon_dict[parts[0]]=parts[1:]
    return lexicon_dict


def main():
    lexicon_dict = get_lexicon_details()
    non_silphone_dict = dict()
    text_file = os.path.join('/Users/ashisharora/Desktop/corpora/kaldi_data_safet/e2e/output/bilexicon.txt')
    text_fh = open(text_file, 'w')
    nsp_text_file = os.path.join('/Users/ashisharora/Desktop/corpora/kaldi_data_safet/e2e/output/nonsilence_phones.txt')
    nsp_text_fh = open(nsp_text_file, 'w')
    for key in lexicon_dict:
        prev_phone = '0'
        phone_sequence = []
        for phone in lexicon_dict[key]:
            new_phone = prev_phone + '_' + phone
            if new_phone not in non_silphone_dict:
                non_silphone_dict[new_phone] = new_phone
                nsp_text_fh.write(new_phone + '\n')
            phone_sequence.append(new_phone)
            prev_phone = phone
        phone_sequence = ' '.join(phone_sequence)
        pronunciation = key + ' ' + phone_sequence
        text_fh.write(pronunciation + '\n')
    

if __name__ == '__main__':
    main()