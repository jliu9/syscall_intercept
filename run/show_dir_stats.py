#! /usr/bin/env python

import os
import sys

def get_file_sizes(directory):
    file_sizes = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_sizes.append(file_size)
    return file_sizes

directory = sys.argv[1]  # Replace with your directory path
file_sizes = get_file_sizes(directory)
file_sizes.sort()

# Print sorted file sizes
for size in file_sizes:
    print(size)


