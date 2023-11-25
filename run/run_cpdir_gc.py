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

assert (len(sys.argv) == 4)
output_dir = sys.argv[1]
output_file = sys.argv[2]
#is_fault = int(sys.argv[3])
gc_num_slot = int(sys.argv[3])
is_fault = False
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

mkfs()
# Run trace
with open(f"{output_dir}/{output_file}.fsp", "w") as fsp_out:
    cur_flag = f"--gc_num_slot {gc_num_slot}"
    if gc_num_slot <= 0:
        cur_flag = ""
    fs_proc = start_fsp(cur_flag , fsp_out)

os.environ["SYSCALL_LOG_PATH"] = f"{output_dir}/{output_file}-app.0.timer"
os.environ["FSP_SYNCALL_SEQ_NO"] = "19408";
with open(f"{output_dir}/{output_file}.0.app", "w") as app_out:
    # p = subprocess.Popen("LD_PRELOAD=../build/examples/libsyscall_fsp.so cp -r FSPs FSPd", shell=True, stdout=app_out, stderr=app_out)
    #p = subprocess.Popen("LD_PRELOAD=../build/examples/libsyscall_fsp.so cp -r FSPs FSPd", shell=True, stdout=app_out, stderr=app_out)
    p = subprocess.Popen("LD_PRELOAD=../build/examples/libsyscall_fsp.so cp -r cptest FSPs", shell=True, stdout=app_out, stderr=app_out)

p.wait()

time.sleep(10)
os.environ["FSP_SYNCALL_SEQ_NO"] = "0";
os.environ["SYSCALL_LOG_PATH"] = f"{output_dir}/{output_file}-app.timer"
with open(f"{output_dir}/{output_file}.app", "w") as app_out:
    # p = subprocess.Popen("LD_PRELOAD=../build/examples/libsyscall_fsp.so cp -r FSPs FSPd", shell=True, stdout=app_out, stderr=app_out)
    #p = subprocess.Popen("LD_PRELOAD=../build/examples/libsyscall_fsp.so cp -r FSPs FSPd", shell=True, stdout=app_out, stderr=app_out)
    p = subprocess.Popen("LD_PRELOAD=../build/examples/libsyscall_fsp.so cp -r FSPs FSPd", shell=True, stdout=app_out, stderr=app_out)

p.wait()
shutdown_fsp(fs_proc)
