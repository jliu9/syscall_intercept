import os
import numpy as np
import matplotlib.pyplot as plt
import sys

# Use the ggplot style for the plot
plt.style.use('ggplot')

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
    for i in range(1, 15):
        file_path = os.path.join(dir_name, f"{case_name}{i}-app.timer")
        times.append(parse_timing_file(file_path))
    stats[case_name] = compute_stats(times)

# Compute Baseline mean
baseline_mean = stats["Baseline"][0]

# Normalized values plot
fig, ax = plt.subplots(figsize=(10, 6))
labels = []
normalized_means = []
normalized_stddevs = []

# Gather normalized data
for case_name, (mean, stddev) in stats.items():
    labels.append(case_name)
    normalized_means.append(mean / baseline_mean)
    normalized_stddevs.append(stddev / baseline_mean)

# Custom colors
custom_colors = []
for case_name in labels:
    if case_name == "Baseline" or case_name == "Crc":
        custom_colors.append('gray')
    elif case_name.startswith("UndoLog"):
        # UndoLog and onwards use the custom color
        custom_colors.append((0.31, 0.64, 0.52))
    else:
        custom_colors.append('#3E8EDE')  # Other cases use the default color

# Bar plot with custom colors
bar_width = 0.4  # Adjust bar width here
bars = ax.bar(
    labels,
    normalized_means,
    width=bar_width,
    yerr=normalized_stddevs,
    capsize=5,
    color=custom_colors)

# Setting y-axis limits and labels
ax.set_ylim(0.9, 1.10)  # Adjusted based on the new yticks
ax.set_yticks([0.9, 1.0, 1.02, 1.04, 1.06, 1.08, 1.10])
ax.set_ylabel('Normalized Latency', fontsize=15)

# Set y-tick numbers to font size 14
ax.tick_params(axis='y', labelsize=14)

# Adding labels to each bar
for bar, value in zip(bars, normalized_means):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,  # X position (center of the bar)
        height - (height - 0.95) / 2,
        # Y position (inside the bar, adjusted to be in the middle)
        f"{value:.3f}",  # Text to be displayed
        ha='center',  # Horizontal alignment
        va='center',  # Vertical alignment
        fontsize=14,  # Font size
        color='white',  # Text color
        rotation=90  # Rotate the text 90 degrees
    )

# Set the title and labels with a larger font size
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=15)

plt.tight_layout()

# Save the plot as EPS
plt.savefig(f'{dir_name}/normalized_times.eps', format='eps')
plt.savefig(f'{dir_name}/normalized_times.png')
