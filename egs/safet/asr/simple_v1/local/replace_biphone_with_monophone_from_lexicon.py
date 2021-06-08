#!/usr/bin/env python
import os

def main():


    biphone_text_handle = open('/Users/ashisharora/Desktop/corpora/kaldi_data_safet/e2e/output/text_to_biphones.txt', 'r', encoding='utf8')
    biphones_text_data = biphone_text_handle.read().strip().split("\n")
    biphone_train_count = dict()
    for line in biphones_text_data:
        biphones = line.split(" ")
        for biphone in biphones:
            biphone_train_count[biphone] = 1


    biphone_handle = open('/Users/ashisharora/Desktop/corpora/kaldi_data_safet/e2e/output/bilexicon.txt', 'r', encoding='utf8')
    biphones_lexicon = biphone_handle.read().strip().split("\n")
    word2biphone = dict()
    for key_val in biphones_lexicon:
        key_val = key_val.split(" ")
        word = key_val[0]
        word2biphone[word] = list()
        for biphone in key_val[1:]:
            if biphone not in biphone_train_count:
                print(key_val[0])
                print(biphone)
                phone = biphone.split('_')[1]
                word2biphone[word].append(phone) 
            else:
               word2biphone[word].append(biphone)


    text_file = os.path.join('/Users/ashisharora/Desktop/corpora/kaldi_data_safet/e2e/output/filtered_biphone_lexicon.txt')
    text_fh = open(text_file, 'w')
    for key in word2biphone:
        text_fh.write(key + " " + " ".join(word2biphone[key]) + '\n')    


if __name__ == '__main__':
    main()