#! /bin/bash

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <case_name>"
    exit 1
fi

case_name=$1

# Note: remember to source env
DIR=crc_perf_inmem
mkdir -p $DIR

ARGS=""

IS_FAULT=0
for ITER in 1 2 3 4 5
do
    sudo -E python run_cpdir_crc.py $DIR "$case_name$ITER" $IS_FAULT
    ARGS="$ARGS $DIR/$case_name$ITER-app.timer"
done

echo $ARGS
python crc_perf_avg.py $ARGS | tee "$DIR/$case_name.avg"

