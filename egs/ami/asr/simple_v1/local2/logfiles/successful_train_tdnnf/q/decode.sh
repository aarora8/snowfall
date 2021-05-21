#!/bin/bash
cd /home/hltcoe/aarora/snowfall/egs/ami/asr/simple_v1
. ./path.sh
( echo '#' Running on `hostname`
  echo '#' Started at `date`
  echo -n '# '; cat <<EOF
/home/hltcoe/aarora/miniconda3/envs/k2/bin/python3 mmi_bigram_decode.py 
EOF
) >exp/decode.log
time1=`date +"%s"`
 ( /home/hltcoe/aarora/miniconda3/envs/k2/bin/python3 mmi_bigram_decode.py  ) 2>>exp/decode.log >>exp/decode.log
ret=$?
time2=`date +"%s"`
echo '#' Accounting: time=$(($time2-$time1)) threads=1 >>exp/decode.log
echo '#' Finished at `date` with status $ret >>exp/decode.log
[ $ret -eq 137 ] && exit 100;
touch exp/q/sync/done.325693
exit $[$ret ? 1 : 0]
## submitted with:
# qsub -v PATH -cwd -S /bin/bash -j y -l arch=*64* -o exp/q/decode.log -l gpu=1 -q gpu.q@@v100 -l h_rt=24:00:00 -l mem_free=10G   /home/hltcoe/aarora/snowfall/egs/ami/asr/simple_v1/exp/q/decode.sh >>exp/q/decode.log 2>&1
