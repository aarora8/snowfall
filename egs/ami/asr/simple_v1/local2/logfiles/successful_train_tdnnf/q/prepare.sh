#!/bin/bash
cd /home/hltcoe/aarora/snowfall/egs/ami/asr/simple_v1
. ./path.sh
( echo '#' Running on `hostname`
  echo '#' Started at `date`
  echo -n '# '; cat <<EOF
/home/hltcoe/aarora/miniconda3/envs/k2/bin/python3 prepare.py 
EOF
) >exp/prepare.log
time1=`date +"%s"`
 ( /home/hltcoe/aarora/miniconda3/envs/k2/bin/python3 prepare.py  ) 2>>exp/prepare.log >>exp/prepare.log
ret=$?
time2=`date +"%s"`
echo '#' Accounting: time=$(($time2-$time1)) threads=1 >>exp/prepare.log
echo '#' Finished at `date` with status $ret >>exp/prepare.log
[ $ret -eq 137 ] && exit 100;
touch exp/q/sync/done.49887
exit $[$ret ? 1 : 0]
## submitted with:
# qsub -v PATH -cwd -S /bin/bash -j y -l arch=*64* -o exp/q/prepare.log -q all.q -l h_rt=24:00:00 -l mem_free=30G   /home/hltcoe/aarora/snowfall/egs/ami/asr/simple_v1/exp/q/prepare.sh >>exp/q/prepare.log 2>&1
