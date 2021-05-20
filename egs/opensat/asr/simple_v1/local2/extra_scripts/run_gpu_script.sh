#!/usr/bin/env bash
#$ -l gpu=1 -q g.q -M ashish.arora.88888@gmail.com -m bea
source /home/gqin2/scripts/acquire-gpus 1
source $HOME/miniconda3/bin/activate
conda activate k2
/home/aaror/miniconda3/envs/k2/bin/python3 /export/c03/aarora8/snowfall/egs/safet/asr/simple_v1/mmi_bigram_train.py

#. ./cmd.sh
#utils/queue.pl --mem 10G --gpu 1 train.log /home/aaror/miniconda3/envs/k2/bin/python mmi_bigram_train.py
#utils/queue.pl --mem 10G --gpu 1 train.log /home/aaror/miniconda3/envs/k2/bin/python mmi_bigram_decode.py
