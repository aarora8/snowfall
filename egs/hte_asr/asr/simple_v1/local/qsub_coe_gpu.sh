#!/usr/bin/env bash

#$ -q gpu.q@@v100 -l gpu=1
#$ -wd /home/hltcoe/aarora/snowfall/egs/safet/asr/simple_v1/
#$ -V
#$ -N decode_job
#$ -j y -o $JOB_NAME
#$ -M ashish.arora.88888@gmail.com
#$ -l mem_free=32G
#$ -l h_rt=24:00:00
#$ -l hostname='!r8n04'

# big data config
# qsub -l gpu=4 -q gpu.q@@v100 -l h_rt=72:00:00
# #$ -m bea
# Activate dev environments and call programs

epoch=30
. ./utils/parse_options.sh
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

/home/hltcoe/aarora/miniconda3/envs/k2/bin/python3 mmi_att_transformer_decode.py --epoch $epoch
echo "$0: ended at `date`"
