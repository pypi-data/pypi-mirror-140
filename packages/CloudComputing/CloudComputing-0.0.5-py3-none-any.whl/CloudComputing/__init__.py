from cloud_storage import connect, change_namespace, download_file
from config import get_auth_token, save_auth_token, check_auth, make_auth, check_config, make_config, load_config, check_ssh_connection
from remote_exec import remote_exec
import vars

# CloudComputing version
_version = "0.0.4"

## Global variables
# cloud_storage
vars.creds_path = check_auth(silent=True)
creds = vars.creds_path
# remote_exec
check_config(silent=True)
c = load_config()
vars.ssh_host = c['SSH']['host']
vars.ssh_port = c['SSH']['port']