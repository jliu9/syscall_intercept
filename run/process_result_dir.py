import pandas as pd
import sys

assert len(sys.argv) == 2

result_dir = sys.argv[1]
output_name = f'{result_dir}/result.csv'

results_dict = dict()
results_dict[f'total_time_ns'] = list()
results_dict['fault_op_num'] = list()
results_dict['recovery_ns'] = list()
results_dict['checkpoint_ns'] = list()
results_dict['restart_ns'] = list()

for op_num in range(499, 48001, 499):
    results_dict['fault_op_num'].append(op_num)
    with open(f'{result_dir}/fault_op_num-{op_num}-app.timer') as f:
        lines = f.readlines()
        for line in lines:
            split = line.split()
            if len(split) > 2 and split[0] == "Time:":
                results_dict[f'total_time_ns'].append(int(split[1]))
    with open(f'{result_dir}/fault_op_num-{op_num}-0.out') as f:
        lines = f.readlines()
        recovery_time = 0
        for line in lines:
            split = line.split()
            if len(split) > 3 and split[0] == "Timer" and split[1] == "0:":
                # results_dict["save_ns"].append(int(split[2])*1000)
                recovery_time += int(split[2])*1000
            if len(split) > 3 and split[0] == "Timer" and split[1] == "1:":
                recovery_time += int(split[2])*1000
            if len(split) > 3 and split[0] == "Timer" and split[1] == "2:":
                recovery_time += int(split[2])*1000
            if len(split) > 3 and split[0] == "Timer" and split[1] == "3:":
                results_dict["restart_ns"].append(int(split[2])*1000)
            if len(split) > 3 and split[0] == "Timer" and split[1] == "4:":
                if '-nan' not in line:
                    results_dict["checkpoint_ns"].append(int(split[2])*1000)
        results_dict["recovery_ns"].append(recovery_time)


results_df = pd.DataFrame(dict([(key, pd.Series(value)) for key, value in results_dict.items()]))
results_df.to_csv(output_name, index=False)
