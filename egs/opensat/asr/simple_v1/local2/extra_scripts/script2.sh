#!/bin/bash

#$ -cwd
#$ -q gpu.q -l gpu=2
#$ -l mem_free=32G
#$ -l num_proc=2
#$ -l h_rt=8:00:00
#$ -j y#

hostname
env| grep SGE_HGR_gpu
ml load cuda90/toolkit
env | grep CUDA_VISIBLE_DEVICES
nvidia-smi
