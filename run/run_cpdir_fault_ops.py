import subprocess
import time
import sys
import os

# REQUIRE:
# - current working directory is leveldb-1.22/
# - environment variables "CFS_ROOT_DIR", "MKFS_SPDK_BIN", "CFS_MAIN_BIN_NAME"
# - spdk has already taken over SSD
CFS_ROOT_DIR = os.environ['CFS_ROOT_DIR']
MKFS_SPDK_BIN = os.environ['MKFS_SPDK_BIN']
CFS_MAIN_BIN_NAME = os.environ['CFS_MAIN_BIN_NAME']

assert (len(sys.argv) == 5)
log_type = sys.argv[1]
output_dir = sys.argv[2]
is_exec = int(sys.argv[3])
bg_sync_no = int(sys.argv[4])
try:
    os.mkdir(output_dir)
except:
    pass


def mkfs():
    # clear the data...
    subprocess.run([MKFS_SPDK_BIN, "mkfs"])
    time.sleep(1)


def checkpoint_journal():
    ckpt_bin_name = "{}/cfs/build/test/fsproc/fsProcOfflineCheckpointer".format(
        CFS_ROOT_DIR)
    p = subprocess.run(ckpt_bin_name, shell=True)
    if p.returncode != 0:
        raise RuntimeError('Cannot checkpoint the journal.')


ready_fname = "/tmp/cfs_ready"
exit_fname = "/tmp/cfs_exit"
os.environ["READY_FILE_NAME"] = ready_fname


# Use same number of workers as apps
def start_fsp(additional_flags, fsp_out):
    # fsp_command = [CFS_MAIN_BIN_NAME]
    # fsp_command.append(str(num_app))
    # fsp_command.append(str(num_app))
    # offset_string = ""
    # for j in range(0, num_app):
    #     offset_string += str(10 * j + 1)
    #     if j != num_app - 1:
    #         offset_string += ","
    # fsp_command.append(offset_string)
    # fsp_command.append(exit_fname)
    # fsp_command.append("/tmp/spdk.conf")
    # offset_string = ""
    # for j in range(0, num_app):
    #     offset_string += str(j + 1)
    #     if j != num_app - 1:
    #         offset_string += ","
    # fsp_command.append(offset_string)
    # fsp_command.append(ufs_config_path)
    # print(fsp_command)

    os.system(f"rm -rf {ready_fname}")
    os.system(f"rm -rf {exit_fname}")

    fsp_command = "$CFS_ROOT_DIR/cfs/build/fsMainOpts -w 1 -a 1 -k 1 -c 1 -e /tmp/cfs_exit -s /tmp/spdk.conf " + additional_flags

    fs_proc = subprocess.Popen(fsp_command, stdout=fsp_out, shell=True)
    while not os.path.exists(ready_fname):
        if fs_proc.poll() is not None:
            raise RuntimeError("uFS Server exits unexpectedly")
        time.sleep(0.1)
    return fs_proc


def shutdown_fsp(fs_proc):
    # Create a exit file to signal server
    with open(exit_fname, 'w+') as f:
        f.write('Apparate')  # This is just for fun :)
    fs_proc.wait()
    # this kill should return non-zero for not finding fsMain...
    if subprocess.run(["pkill", "fsMainOpts"]).returncode == 0:
        print("WARN: Detect fsMain after shutdown; kill...")

    os.system(f"rm -rf {ready_fname}")
    os.system(f"rm -rf {exit_fname}")


def load_data(num_app, num_worker, log_dir):
    ldb_load_command = "python3 scripts/run_ldb_common.py {} {} traces/load-10m-16.txt".format(
        num_app, num_app)
    ldb_load_command = [
        "python3", "scripts/run_ldb_common.py",
        str(num_app),
        str(num_worker), "traces/load-10m-16.txt", log_dir
    ]
    return subprocess.run(ldb_load_command)


def start_leveldb(trace_path, num_app, num_worker, log_dir):
    ldb_load_command = [
        "python3", "scripts/run_ldb_common.py",
        str(num_app),
        str(num_worker), trace_path, log_dir
    ]
    return subprocess.run(ldb_load_command)

def prepare_dir():
    mkfs()

    fs_proc = start_fsp("", sys.stdout)
    p = subprocess.Popen("LD_PRELOAD=../build/examples/libsyscall_fsp.so cp -r cptest FSPs", shell=True)
    p.wait()
    time.sleep(5)
    shutdown_fsp(fs_proc)
    time.sleep(2)
    checkpoint_journal()

timer_out = open(f"{output_dir}/timer.out", "w")
for op_num in range(499, 48001, 499):
    # Do mkfs
    # mkfs()

    # # Load data
    # with open(f"{output_dir}/fill_num-app-{num_app}_ufs.out", "w") as fsp_out:
    #     fs_proc = start_fsp(num_app, "ufs_cfgs/ufs-fill.conf", fsp_out)

    # ldb_output_dir = f"{output_dir}/fill_num-app-{num_app}_leveldb"
    # os.mkdir(ldb_output_dir)

    # # use same number of workers as apps
    # p = start_leveldb(workload_trace_map[f"fillseq"], num_app, num_app,
    #                   ldb_output_dir)
    # shutdown_fsp(fs_proc)
    # if p.returncode != 0:
    #     print("LevelDB return non-zero exit code!")
    #     exit(1)

    # # Checkpoint the journal
    # checkpoint_journal()
    if bg_sync_no > 0:
        os.environ["SYSCALL_LOG_PATH"] = 'prep.timer'
        prepare_dir()
    checkpoint_flag = '--checkpoint'

    if is_exec:
        recover_flag = '--recover_mode 2'
    else:
        recover_flag = ''
    os.environ['FSP_SYNCALL_SEQ_NO'] = f'{bg_sync_no}'

    # Run trace
    with open(f"{output_dir}/fault_op_num-{op_num}-0.out", "w") as fsp_out:
        fs_proc = start_fsp(f"--fault_op_num {op_num} {recover_flag} {checkpoint_flag}", fsp_out)

    start_time = time.perf_counter_ns()
    os.environ["SYSCALL_LOG_PATH"] = f"{output_dir}/fault_op_num-{op_num}-app.timer"
    with open(f"{output_dir}/fault_op_num-{op_num}-app.out", "w") as app_out:
        p = subprocess.Popen("LD_PRELOAD=../build/examples/libsyscall_fsp.so cp -r FSPs FSPd", shell=True, stdout=app_out, stderr=app_out)

    # time.sleep(10)

    # shutdown_fsp(fs_proc)

    # fs_proc.wait()

    # with open(f"{output_dir}/fault_op_num-{op_num}-1.out", "w") as fsp_out:
    #     fs_proc = start_fsp("-r" if log_type == "eclog" else "-o" if log_type == "oplog" else "-t", fsp_out)

    p.wait()
    if log_type == "rawec":
        time_elapse = int((time.perf_counter_ns() - start_time))
        print(f"Fault_op_num: {op_num} FirstTime: {time_elapse} us\n", file=timer_out)
        start_time = time.perf_counter_ns()
        os.environ["SYSCALL_LOG_PATH"] = f"{output_dir}/fault_op_num-{op_num}-app.timer2"
        with open(f"{output_dir}/fault_op_num-{op_num}-appretry.out", "w") as app_out:
            p = subprocess.Popen("LD_PRELOAD=../build/examples/libsyscall_fsp.so cp -r FSPs FSPd", shell=True, stdout=app_out, stderr=app_out)
    p.wait()
    
    time_elapse = int((time.perf_counter_ns() - start_time))
    print(f"Fault_op_num: {op_num} SecondTime: {time_elapse} us\n", file=timer_out)

    time.sleep(2)

    shutdown_fsp(fs_proc)

    time.sleep(2)
