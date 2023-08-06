from os import name
import cloudsync as cs
import tempfile as tf
from .config import make_auth
import pandas as pd
import json
from . import vars

def connect():
    oauth_config = cs.command.utils.generic_oauth_config('onedrive')
    if vars.token is None:
        if vars.creds_path == "":
            make_auth()
        f = open(vars.creds_path, 'r')
        creds = json.load(f)
    else:
        print("[DEBUG] Loading token from file")
        creds = vars.token # The ouath token is read from file on the local machine and "imported" on the remote one
    vars.provider = cs.create_provider('onedrive', oauth_config=oauth_config)
    vars.provider.connect(creds)

def change_namespace(path_in_ns, namespace=None):
    # Change namespace to shared folder
    ns = vars.provider.list_ns()
    if namespace is None:
        shared_folder_name = path_in_ns
        for x in ns:
            if shared_folder_name in x.name:
                break
        print("Changing namespace to: {}".format(x.id))
        vars.provider.namespace = x
    else:
        for x in ns:
            if namespace in x.name:
                break
        print("Changing namespace to: {}".format(x.id))
        vars.provider.namespace = x

def download_file(filename, namespace=None, output=None):
    if vars.provider is None:
        connect()
    if not namespace is None:
        change_namespace(namespace)
    if output is None:
        tmp = tf.NamedTemporaryFile()
        print("Downloading to {} ...".format(tmp.name))
    else:
        tmp = open(output, 'w')
    vars.provider.download_path(filename, tmp)
    tmp.seek(0) # Go back to first line
    return tmp

def upload_file():
    print("> upload_file()")
    print("Still to be implemented...")