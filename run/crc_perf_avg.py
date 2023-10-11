#! /usr/bin/env python
import sys

num_file = len(sys.argv) - 1

def compute_avg(l):
    if len(l) == 0:
        return 0
    return sum(l) / len(l)

time_list = []
for fname in sys.argv[1:]:
    with open(fname) as f:
        for line in f:
            if 'Time' in line:
                items = line.split(' ')
                time_list.append(int(items[1]))
                break
assert(len(time_list) == num_file)
cur_avg = compute_avg(time_list)
print(f'avg: {cur_avg}')



