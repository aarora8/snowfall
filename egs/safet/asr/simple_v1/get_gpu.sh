#!/usr/bin/env bash

qlogin -l gpu=1 -l mem_free=10G,ram_free=10G -l "hostname=b1[12345678]|c0[1345678]|c1[0123456789]*" -q i.q -M ashish.arora.88888@gmail.com -m bea -now no
export CUDA_VISIBLE_DEVICES=$(free-gpu)
echo $CUDA_VISIBLE_DEVICES
source $HOME/miniconda3/bin/activate
conda activate k2
cd /export/c03/aarora8/snowfall/egs/safet/asr/simple_v1
./run.sh

