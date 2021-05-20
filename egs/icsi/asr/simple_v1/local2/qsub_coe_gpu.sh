#!/usr/bin/env bash

#$ -q gpu.q -l gpu=1
#$ -wd /home/hltcoe/aarora/snowfall/egs/icsi/asr/simple_v1/
#$ -V
#$ -N train_job
#$ -j y -o $JOB_NAME-$JOB_ID.out
#$ -M ashish.arora.88888@gmail.com
#$ -m bea
#$ -l mem_free=32G
#$ -l h_rt=24:00:00
#$ -l hostname='!r7n04'

# big data config
# qsub -l gpu=4 -q gpu.q@@v100 -l h_rt=72:00:00

# Activate dev environments and call programs
source ~/.bashrc
export PATH="/home/hltcoe/aarora/miniconda3/bin:$PATH"
conda activate k2

env| grep SGE_HGR_gpu
module load cuda10.0/toolkit
env | grep CUDA_VISIBLE_DEVICES
nvidia-smi

echo "$0: Running on `hostname`"
echo "$0: Started at `date`"
echo "$0: Running the job on GPU(s) $CUDA_VISIBLE_DEVICES"
"$@"

/home/hltcoe/aarora/miniconda3/envs/k2/bin/python3 mmi_att_transformer_train.py
#bash run.sh

echo "$0: ended at `date`"
# -l hostname='!r3n03&!r3n06&!r3n01&!r8n02&!r3n04&!r8n05&!r5n02'
