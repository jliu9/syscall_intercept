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

CONFIG_NAME="$DIR/$case_name.config"

echo "CFS_FT_LIB_MEM_SIZE_KB:$CFS_FT_LIB_MEM_SIZE_KB" >> "${CONFIG_NAME}"
echo "=======" >> "${CONFIG_NAME}"
git log -1 >>"${CONFIG_NAME}"
echo "=======" >> "${CONFIG_NAME}"
TS_STR="$(date +%m_%d_%H-%M-%S)"
git diff >"$DIR/${case_name}.${TS_STR}.diff"

sudo rm -rf /tmp/fsMainOpts*

IS_FAULT=0
for ITER in {1..15}
do
    sudo rm -rf /dev/shm/*
    sleep 10
    sudo -E python run_cpdir_crc.py $DIR "$case_name$ITER" $IS_FAULT
    ARGS="$ARGS $DIR/$case_name$ITER-app.timer"
done

echo $ARGS
python crc_perf_avg.py $ARGS | tee "$DIR/$case_name.avg"

