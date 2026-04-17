from dotenv import load_dotenv
import os
import stat
from paramiko import AutoAddPolicy
from paramiko import SSHClient

file_path = "/home/keoni/sync_folder/"

load_dotenv()
HOSTNAME = os.getenv("HOSTNAME")
USERNAME = os.getenv("USERNAME")
PORT = os.getenv("PORT")

def setup_connection():
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(hostname=HOSTNAME, username=USERNAME, port=PORT)
    return client

def create_file(final_path):
    client = setup_connection()
    sftp = client.open_sftp()
    sftp.put(final_path, file_path+final_path[1:])
    sftp.close()
    client.close()

def deleted_file(final_path):
    client = setup_connection()
    sftp = client.open_sftp()
    sftp.remove(file_path+final_path)
    sftp.close()
    client.close()

def moved_file_or_dir(initial_name, final_name):
    client = setup_connection()
    sftp = client.open_sftp()
    sftp.rename(file_path+initial_name, file_path+final_name)
    sftp.close()
    client.close()

def create_directory(final_path):
    client = setup_connection()
    sftp = client.open_sftp()
    sftp.mkdir(file_path+final_path[1:])
    sftp.close()
    client.close()

def remove_directory(sftp, file_path):
    for i in sftp.listdir_attr(file_path):
        child_path = file_path.rstrip("/") + "/" + i.filename

        if stat.S_ISDIR(i.st_mode):
            remove_directory(sftp, child_path)
        else:
            sftp.remove(child_path)

    sftp.rmdir(file_path)

def remove_file_n_directory(sftp, final_path):
    full_path = "/home/keoni/sync_folder/" + final_path.lstrip("./")
    attr = sftp.stat(full_path)
    if stat.S_ISDIR(attr.st_mode):
        remove_directory(sftp, full_path)
    else:
        sftp.remove(full_path)

# client = setup_connection()
# sftp = client.open_sftp()
# remove_directory(sftp, "/home/keoni/sync_folder/hello")
# sftp.close()
# client.close()