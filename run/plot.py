import pandas as pd
import matplotlib.pyplot as plt
import sys

def plot_stacked_area(input_csv_name, case_name):
    # Read the CSV file
    df = pd.read_csv(input_csv_name)

    # Convert all the time columns from ns to ms
    df['recovery_ms'] = df['recovery_ns'] / 1e6
    df['save_ms'] = df['save_ns'] / 1e6
    df['restart_ms'] = df['restart_ns'] / 1e6
    df['workload_ms'] = df['total_time_ns'] / 1e6 - df['recovery_ns'] / 1e6 - df['save_ns'] / 1e6 - df['restart_ns'] / 1e6
    print(list(df['workload_ms']))

    # Plotting
    plt.stackplot(df['fault_op_num'], df['restart_ms'], df['recovery_ms'], df['save_ms'], df['workload_ms'],
                  labels=['Restart', 'Recovery', 'Save', 'Workload'], alpha=0.6)
    plt.legend(loc='upper left')
    plt.title(case_name)
    plt.xlabel('fault_op_num')
    plt.ylabel('Time (ms)')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()

    plt.ylim(0, 1500)

    # Save to PNG
    png_name = input_csv_name.replace('.csv', f'{case_name}.png')
    plt.savefig(png_name, dpi=300)
    print(f"Plot saved as {png_name}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot_script.py <input_csv_name> <case_name>")
        sys.exit(1)
    
    input_csv_name = sys.argv[1]
    case_name = sys.argv[2]
    plot_stacked_area(input_csv_name, case_name)
