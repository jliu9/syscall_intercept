#! /bin/bash

# Define the workspace directory
WORKSPACE_DIR="${CFS_ROOT_DIR}/cfs"

CUR_DIR=$(pwd)

# Define the flag combinations
OPLOG_FLAGS="-DDO_UNDOLOG_CRC=OFF -DDO_OPLOG_CRC=OFF -DDO_UFS_FT_CRC=ON -DDO_UFS_FT_OPLOG=ON -DENABLE_UFS_FT=OFF -DSINGLE_THREADED_TIMER=ON"
UNDOLOG_FLAGS="-DDO_UNDOLOG_CRC=OFF -DDO_OPLOG_CRC=OFF -DDO_UFS_FT_CRC=ON -DDO_UFS_FT_OPLOG=OFF -DENABLE_UFS_FT=ON -DSINGLE_THREADED_TIMER=ON"

# Check input argument
if [ "$1" == "oplog" ]; then
    FLAGS=$OPLOG_FLAGS
elif [ "$1" == "undolog" ]; then
    FLAGS=$UNDOLOG_FLAGS
else
    echo "Invalid input. Please specify 'oplog' or 'undolog'."
    exit 1
fi

cd $WORKSPACE_DIR
echo "Using flags: $FLAGS"
rm -rf build
mkdir -p build
rm -rf ~/.cache
cd build
cmake $FLAGS -DCMAKE_BUILD_TYPE=Release -DCFS_DISK_LAYOUT_LEVELDB=ON -DBUILD_TESTS=ON ../
make -j20
sleep 10
cd $CUR_DIR

# bash recompile_recover_perf_comb.sh undolog && bash run_perf.sh UNDO 24000 && bash run_perf.sh UNDO 0 && bash recompile_recover_perf_comb.sh oplog && bash run_perf.sh EXEC 24000 && bash run_perf.sh EXEC 0 && bash run_perf.sh REPLAY 24000 && bash run_perf.sh REPLAY 0