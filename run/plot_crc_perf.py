import os
import numpy as np
import matplotlib.pyplot as plt
import sys

# Define the combinations
combinations = [
    "Baseline",
    "Crc",
    "OpLog",
    "OpLogSelfCrc",
    "OpLogDSCrc",
    "OpLogDSCrcSelfCrc",
    "UndoLog",
    "UndoLogSelfCrc",
    "UndoLogDSCrc",
    "UndoLogDSCrcSelfCrc",
]

# Directory name where the results are stored
dir_name = sys.argv[1]

# Function to parse the timing file


def parse_timing_file(file_path):
    with open(file_path, 'r') as file:
        line = file.readline()
        # Extract the number from "Time: XXX ns"
        time_ns = int(line.split()[1])
    return time_ns

# Function to compute statistics


def compute_stats(times):
    return np.mean(times), np.std(times)


# Store the statistics for each case
stats = {}
for case_name in combinations:
    times = []
    for i in range(1, 11):
        file_path = os.path.join(dir_name, f"{case_name}{i}-app.timer")
        times.append(parse_timing_file(file_path))
    stats[case_name] = compute_stats(times)

# Absolute values plot
fig, ax = plt.subplots(figsize=(10, 6))
labels, means, stddevs = zip(*[(k, *v) for k, v in stats.items()])
ax.bar(labels, means, yerr=stddevs, capsize=5, color='#3E8EDE')
ax.set_title('Absolute Times with Variance')
ax.set_ylabel('Time (ns)')
ax.set_xticklabels(labels, rotation=45, ha='right')
plt.tight_layout()
plt.savefig('absolute_times.png')  # Save the first plot

# Normalized values plot with box plot
fig, ax = plt.subplots(figsize=(10, 6))
baseline_mean = stats['Baseline'][0]
normalized_means = [m / baseline_mean for m in means]
normalized_data = [times / baseline_mean for times in stats.values()]

# Bar plot
bars = ax.bar(labels, normalized_means, color='#3E8EDE')

# Setting y-axis limits and labels
ax.set_ylim(0.9, 1.075)
ax.set_yticks([0.9, 1.0, 1.02, 1.04, 1.06])
ax.set_ylabel('Normalized Time')

# Adding labels to each bar
for bar, value in zip(bars, normalized_means):
    ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}",
            ha='center', va='bottom', fontsize=8)

ax.set_title('Normalized Times to Baseline')
ax.set_xticklabels(labels, rotation=45, ha='right')
plt.tight_layout()
plt.savefig('normalized_times.png')  # Save the second plot
