#!/bin/bash

#$ -q all.q
#$ -l num_proc=1,mem_free=10G,h_rt=8:00:00
#$ -N mytest

hostname

# print date and time
date
# Sleep for 20 seconds
sleep 20
# print date and time again
date
