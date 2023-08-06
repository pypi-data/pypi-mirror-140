import os
import subprocess
import tempfile as tf
from . import vars
from .config import get_token

def remote_exec(path, rdir="./", verbose=True, logfile=None):
    # If localhost, return
    if 'localhost' in vars.ssh_host or '127.0.0.1' in vars.ssh_host:
        print("Running on local machine...")
        return
    print("Running from file: {}".format(path))
    # Open the calling script (from path) and read the file
    fin = open(path, 'r')
    # Split the script and take everything after separator
    s = fin.read().split("__file__")[-1]
    s = s[s.find("\n")+1:len(s)]   
    # Do we need to import CloudComputing? 
    if "CloudComputing" in s or "cc" in s:
        s = "import CloudComputing as cc\ncc.vars.token = {}\ncc.__token__ = cc.vars.token\n".format(get_token()) + s
    # Write to file
    tmp = os.path.join(tf.gettempdir(), os.urandom(8).hex() + '.py')
    fout = open(tmp, 'w')
    fout.write(s)
    fout.close()
    # CD to remote dir (if any)
    cmd = cmd = "/usr/bin/ssh -p {} {}".format(vars.ssh_port, vars.ssh_host)
    cmd = cmd + " 'cd {} &&".format(rdir)
    # Copy the temp file (script) to the remote working dir
    xmd = "/usr/bin/scp -P {} {} {}:{}".format(vars.ssh_port, tmp, vars.ssh_host, rdir)
    subprocess.run(xmd, shell=True)
    # Run over SSH
    cmd = cmd + " python {}'".format(tmp.split("/")[-1]) # Remove "/tmp/" from the filename
    if not verbose:
        cmd = cmd + " 1>/dev/null 2>&1"
    if not logfile is None:
        print("Logging to file: {}".format(logfile))
        cmd = cmd + " > {}".format(logfile)
    subprocess.Popen(cmd, shell=True)
    # Remove the local temp file
    subprocess.run("rm {}".format(tmp), shell=True)
    # Remove the remote temp file
    # os.system("/usr/bin/ssh -p {} {} 'rm {}/{}'".format(vars.ssh_port, vars.ssh_host, rdir, tmp.split("/")[-1]))
    # Exit to prevent the calling script to run locally
    exit(0)