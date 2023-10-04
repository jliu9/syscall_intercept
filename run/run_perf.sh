#! /bin/bash

# Check for the required argument
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 EXEC|REPLAY <SYNC_NO>"
    exit 1
fi

# Set is_exec based on the argument
if [[ $1 == "EXEC" ]]; then
    is_exec=1
elif [[ $1 == "REPLAY" ]]; then
    is_exec=0
else
    echo "Error: Invalid argument. Please use either EXEC or REPLAY."
    exit 1
fi

SYNC_NO=$2


dir_name="RESULTS-2023-$(date +%m-%d-%H-%M)"
mkdir -p "$dir_name"

echo "$1" >> "$dir_name/config"
echo "SYNC_NO:$SYNC_NO" >> "$dir_name/config"
sudo -E python run_cpdir_fault_ops.py oplog "$dir_name" $is_exec $SYNC_NO
