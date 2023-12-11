import pandas as pd
import sys

assert len(sys.argv) == 2

result_dir = sys.argv[1]
output_name = f'{result_dir}/result.csv'

results_dict = dict()
results_dict[f'total_time_ns'] = list()
results_dict['fault_op_num'] = list()
results_dict['recovery_us'] = list()
results_dict['clean_restart_us'] = list()
results_dict['deserialize_us'] = list()
results_dict['serialize_us'] = list()
results_dict['write_us'] = list()
results_dict['read_us'] = list()
results_dict['replay_us'] = list()
results_dict['ckpt_us'] = list()

def get_time_us(item:str):
    return int(item)

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
        timers = {}
        for line in lines:
            split = line.split()
            if len(split) > 3 and split[0] == "Timer" and split[1] == "0:":
                timers[0] = get_time_us(split[2])
            if len(split) > 3 and split[0] == "Timer" and split[1] == "1:":
                timers[1] = get_time_us(split[2])
            if len(split) > 3 and split[0] == "Timer" and split[1] == "2:":
                timers[2] = get_time_us(split[2])
            if len(split) > 3 and split[0] == "Timer" and split[1] == "3:":
                timers[3] = get_time_us(split[2])
            if len(split) > 3 and split[0] == "Timer" and split[1] == "4:":
                timers[4] = get_time_us(split[2])
            if len(split) > 3 and split[0] == "Timer" and split[1] == "5:":
                timers[5] = get_time_us(split[2])
            if len(split) > 3 and split[0] == "Timer" and split[1] == "6:":
                timers[6] = get_time_us(split[2])
            if len(split) > 3 and split[0] == "Timer" and split[1] == "7:":
                timers[7] = get_time_us(split[2])
        cur_time_before_shutdown_us = timers[0]
        cur_deserialize_us = timers[1]
        cur_ckpt_us = timers[4]
        cur_serialize_us = timers[5]
        cur_write_us = timers[6]
        cur_read_us = timers[7]
        cur_replay_us = timers[2]
        cur_clean_restart_us = timers[3] - cur_read_us
        cur_recovery_us = cur_read_us + cur_time_before_shutdown_us \
            + cur_replay_us + cur_deserialize_us
        results_dict['recovery_us'].append(cur_recovery_us)
        results_dict['clean_restart_us'].append(cur_clean_restart_us)
        results_dict['deserialize_us'].append(cur_deserialize_us)
        results_dict['serialize_us'].append(cur_serialize_us)
        results_dict['write_us'].append(cur_write_us)
        results_dict['read_us'].append(cur_read_us)
        results_dict['replay_us'].append(cur_replay_us)
        results_dict['ckpt_us'].append(cur_ckpt_us)


results_df = pd.DataFrame(dict([(key, pd.Series(value)) for key, value in results_dict.items()]))
results_df.to_csv(output_name, index=False)