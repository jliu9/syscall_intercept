#!/bin/bash

# Check if directory name is provided
if [ -z "$1" ]; then
    echo "Please provide a directory name."
    exit 1
fi

# Assign the first argument to dir_name
dir_name="$1"

# Check if the directory exists
if [ ! -d "$dir_name" ]; then
    echo "Directory does not exist: $dir_name"
    exit 1
fi

# Loop over the non-BK files in the given directory
for file in "$dir_name"/*[^BK].avg; do
    # Extract the base filename
    base_file=$(basename "$file")
    echo "$base_file"

    # Construct the BK file name
    bk_file="${base_file%.avg}BK.avg"

    # Check if the BK file exists in the directory
    if [ -f "$dir_name/$bk_file" ]; then
        # Concatenate the contents of the pair
        cat "$dir_name/$base_file"
        cat "$dir_name/$bk_file"
    else
        echo "BK file for $base_file not found in $dir_name."
    fi
done

