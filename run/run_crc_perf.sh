#! /bin/bash

case_name=$1

# Note: remember to source env

IS_FAULT=0
for ITER in 1 2 3
do
    sudo -E python run_cpdir_crc.py ./crc_perf "$case_name$ITER" $IS_FAULT
done

