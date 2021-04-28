#!/bin/bash
cd /export/c03/aarora8/snowfall/egs/safet/asr/simple_v1
. ./path.sh
( echo '#' Running on `hostname`
  echo '#' Started at `date`
  echo -n '# '; cat <<EOF
/home/aaror/miniconda3/envs/k2/bin/python3 prepare.py 
EOF
) >train.log
time1=`date +"%s"`
 ( /home/aaror/miniconda3/envs/k2/bin/python3 prepare.py  ) 2>>train.log >>train.log
ret=$?
time2=`date +"%s"`
echo '#' Accounting: time=$(($time2-$time1)) threads=1 >>train.log
echo '#' Finished at `date` with status $ret >>train.log
[ $ret -eq 137 ] && exit 100;
touch ./q/sync/done.6436
exit $[$ret ? 1 : 0]
## submitted with:
# qsub -v PATH -cwd -S /bin/bash -j y -l arch=*64* -o ./q/train.log -q all.q -l hostname='!b02*&!c12*' -l mem_free=30G,ram_free=30G   /export/c03/aarora8/snowfall/egs/safet/asr/simple_v1/./q/train.sh >>./q/train.log 2>&1
