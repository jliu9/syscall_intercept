#! /bin/bash

# Define the workspace directory
WORKSPACE_DIR="${CFS_ROOT_DIR}/cfs/build"

CUR_DIR=$(pwd)


# Array of combinations and corresponding names
declare -A combinations=(
    ["-DDO_UFS_FT_CRC=OFF -DDO_UFS_FT_OPLOG=OFF"]="Baseline"
    ["-DDO_UFS_FT_CRC=ON -DDO_UFS_FT_OPLOG=OFF"]="Crc"
    ["-DDO_UFS_FT_CRC=OFF -DDO_UFS_FT_OPLOG=ON"]="OpLog"
    ["-DDO_UFS_FT_CRC=ON -DDO_UFS_FT_OPLOG=ON"]="Full"
)

# Loop through the combinations and run the script
for flags in "${!combinations[@]}"; do
    cd $WORKSPACE_DIR
    echo $flags
    cmake "$flags" ../
    rm -rf ~/.cache
    make -j20
    cd $CUR_DIR
    # Run the script with the combination name and the combination name with "BK" appended
    bash ./run_crc_perf.sh "${combinations[$flags]}" && bash ./run_crc_perf.sh "${combinations[$flags]}BK"
done
