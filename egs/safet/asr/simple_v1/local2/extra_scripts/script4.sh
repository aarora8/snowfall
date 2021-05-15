#!/usr/bin/env bash

#$ -q gpu.q -l gpu=1 
#$ -wd /home/hltcoe/aarora/snowfall/egs/safet/asr/simple_v1/
#$ -V
#$ -N decode_job
#$ -j y -o $JOB_NAME-$JOB_ID.out
#$ -M ashish.arora.88888@gmail.com
#$ -m bea
#$ -l mem_free=16G
#$ -l h_rt=1:00:00

# Activate dev environments and call programs
source ~/.bashrc
export PATH="/home/hltcoe/aarora/miniconda3/bin:$PATH"
conda activate k2

hostname
env| grep SGE_HGR_gpu
module load cuda10.0/toolkit
env | grep CUDA_VISIBLE_DEVICES
nvidia-smi

/home/hltcoe/aarora/miniconda3/envs/k2/bin/python3 mmi_bigram_decode.py
