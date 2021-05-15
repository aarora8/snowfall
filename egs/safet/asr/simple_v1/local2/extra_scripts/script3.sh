#!/bin/bash

hostname
env| grep SGE_HGR_gpu
module load cuda10.0/toolkit
env | grep CUDA_VISIBLE_DEVICES
nvidia-smi
