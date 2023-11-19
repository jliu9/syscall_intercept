#! /bin/bash

# Define the workspace directory
WORKSPACE_DIR="${CFS_ROOT_DIR}/cfs"

CUR_DIR=$(pwd)

# Array of combinations and corresponding names
declare -A combinations=(
    ["-DDO_UNDOLOG_CRC=OFF -DDO_OPLOG_CRC=OFF -DDO_UFS_FT_CRC=OFF -DDO_UFS_FT_OPLOG=OFF -DENABLE_UFS_FT=OFF"]="CRetry"
    #["-DDO_UNDOLOG_CRC=OFF -DDO_OPLOG_CRC=OFF -DDO_UFS_FT_CRC=ON -DDO_UFS_FT_OPLOG=OFF -DENABLE_UFS_FT=OFF"]="Crc"
    #["-DDO_UNDOLOG_CRC=OFF -DDO_OPLOG_CRC=OFF -DDO_UFS_FT_CRC=OFF -DDO_UFS_FT_OPLOG=ON -DENABLE_UFS_FT=OFF"]="OpLog"
    #["-DDO_UNDOLOG_CRC=OFF -DDO_OPLOG_CRC=ON -DDO_UFS_FT_CRC=OFF -DDO_UFS_FT_OPLOG=ON -DENABLE_UFS_FT=OFF"]="OpLogSelfCrc"
    #["-DDO_UNDOLOG_CRC=OFF -DDO_OPLOG_CRC=OFF -DDO_UFS_FT_CRC=ON -DDO_UFS_FT_OPLOG=ON -DENABLE_UFS_FT=OFF"]="OpLogDSCrc"
    #["-DDO_UNDOLOG_CRC=OFF -DDO_OPLOG_CRC=ON -DDO_UFS_FT_CRC=ON -DDO_UFS_FT_OPLOG=ON -DENABLE_UFS_FT=OFF"]="OpLogDSCrcSelfCrc"
    #["-DDO_UNDOLOG_CRC=OFF -DDO_OPLOG_CRC=OFF -DDO_UFS_FT_CRC=OFF -DDO_UFS_FT_OPLOG=OFF -DENABLE_UFS_FT=ON"]="UndoLog"
    #["-DDO_UNDOLOG_CRC=ON -DDO_OPLOG_CRC=OFF -DDO_UFS_FT_CRC=OFF -DDO_UFS_FT_OPLOG=OFF -DENABLE_UFS_FT=ON"]="UndoLogSelfCrc"
    #["-DDO_UNDOLOG_CRC=OFF -DDO_OPLOG_CRC=OFF -DDO_UFS_FT_CRC=ON -DDO_UFS_FT_OPLOG=OFF -DENABLE_UFS_FT=ON"]="UndoLogDSCrc"
    #["-DDO_UNDOLOG_CRC=ON -DDO_OPLOG_CRC=OFF -DDO_UFS_FT_CRC=ON -DDO_UFS_FT_OPLOG=OFF -DENABLE_UFS_FT=ON"]="UndoLogDSCrcSelfCrc"
)


# Loop through the combinations and run the script
for flags in "${!combinations[@]}"; do
    cd $WORKSPACE_DIR
    git checkout ec-client
    echo $flags
    rm -rf build
    mkdir -p build
    rm -rf ~/.cache
    cd build
    cmake $flags -DCMAKE_BUILD_TYPE=Release -DCFS_DISK_LAYOUT_LEVELDB=ON -DBUILD_TESTS=ON ../
    make -j20
    sleep 10
    cd $CUR_DIR
    for MEM_LIMIT_KB in "-1" "128" "256" "512" "1024" "2048" "4096" "8192" "16384"
    do
        export CFS_FT_LIB_MEM_SIZE_KB=$MEM_LIMIT_KB
        echo "$CFS_FT_LIB_MEM_SIZE_KB"
        case_name="${combinations[$flags]}KB_${MEM_LIMIT_KB}"
        echo $case_name
        bash ./run_crc_perf.sh "${case_name}" && bash ./run_crc_perf.sh "${case_name}BK"
    done
done
