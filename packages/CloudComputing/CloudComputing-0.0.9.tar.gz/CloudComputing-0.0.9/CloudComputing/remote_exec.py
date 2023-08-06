import os
import subprocess
import tempfile as tf
from . import vars

def remote_exec(path, rdir="", verbose=True, logfile=None):
    # If localhost, return
    if 'localhost' in vars.ssh_host or '127.0.0.1' in vars.ssh_host:
        print("Running on local machine...")
        return
    print("Running from file: {}".format(path))
    # Open the calling script (from path) and read the file
    fin = open(path, 'r')
    # Split the script and take everything after separator
    s = fin.read().split("remote_exec(__file__)")[-1]
    # Do we need to import CloudComputing? 
    if "CloudComputing" in s or "cc" in s:
        s = "import CloudComputing as cc\n" + s
    # Write to file
    tmp = os.path.join(tf.gettempdir(), os.urandom(8).hex() + '.py')
    fout = open(tmp, 'w')
    fout.write(s)
    fout.close()
    # CD to remote dir (if any)
    cmd = cmd = "/usr/bin/ssh -p {} {}".format(vars.ssh_port, vars.ssh_host)
    cmd = cmd + " 'cd {} &&".format(rdir)
    # Run over SSH
    print(vars.ssh_host + " " + vars.ssh_port)
    cmd = cmd + " python -V && python -u -' < {}".format(tmp)
    print(cmd)
    if not verbose:
        cmd = cmd + " 1>/dev/null 2>&1"
    if not logfile is None:
        print("Logging to file: {}".format(logfile))
        cmd = cmd + " > {}".format(logfile)
    subprocess.Popen(cmd, shell=True)
    # Remove the temp file
    os.system("rm {}".format(tmp))
    # Exit to prevent the calling script to run locally
    exit(0)