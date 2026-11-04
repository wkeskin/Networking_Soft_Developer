# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 13:05:45 2025

@author:
    COMP216 - SEC 401
    Networking for Software Developers - Lab 6
    Group 2: 
        Aiko Bislig 
        Jacob Ferreira
        Lissette Gorrin Rodriguez
        Samer Aljundi Al Fattouhi Aljundi
        Wardatul Keskin
        
Lab 6 – Remote Systems
"""

# Exercise #1 - Downnload files via FTP
import ftplib
import os

#Creating local directory to store downloads
local = 'Video_Downloads'
os.makedirs(local, exist_ok=True)

#Initialize FTP connection & Login
ftp_conn = ftplib.FTP('ftp.gnu.org')
ftp_conn.login()

#Print welcome to show successful connection
print(ftp_conn.getwelcome())

#Changing working directory to /video
ftp_conn.cwd('/video')

#Storing list of files in video directory
files = ftp_conn.nlst()
#Printing list to verify
print(files)

#Function to download .webm files
def download_files(filename):
    #Establishing local path
    local_path = os.path.join(local, filename)
    #Using with-as to download from directory
    with open(local_path, 'wb') as download_file:
        ftp_conn.retrbinary(f'RETR {filename}', download_file.write)
    #Printing successful download
    print(f'{filename} downloaded successfully.')
    
#Specifying files to be downloaded as .webm only
webm_files = [file for file in files if file.endswith('.webm')]
for file in webm_files:
    #Calling download_file on specified files
    download_files(file)

#Closing connection
ftp_conn.quit()

#Printing success message
print("All files downloaded successfully.")

#Checking the total vidoes as .webm
print(f"Total .webm files found: {len(webm_files)}")
print("List of .webm files found:")
for file in webm_files:
    print(file)

# Exercise #2 - SSH with Cloud Services
import paramiko

#AWS Lightsail connection details
IP = '35.182.225.45'
USERNAME = 'ec2-user'
PRIVATE_KEY_PATH = 'COMP216.pem'
REMOTE_DIRECTORY = "/home/ec2-user/Documents"
LOCAL_FILE = "sample.txt"

# Create a sample file for upload
with open(LOCAL_FILE, "w") as f:
    f.write("This is a test file uploaded via SFTP.")

try:
    #Load Pivate (SSH) key
    key = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_PATH)

    # Establish SSH connection
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to AWS Lightsail VM
    print("Connecting to AWS Lightsail...")
    ssh_client.connect(hostname=IP, username=USERNAME, pkey=key)
    print("Connected to AWS Lightsail.")

    # Create Documents directory
    command = f"mkdir -p {REMOTE_DIRECTORY}"
    stdin, stdout, stderr = ssh_client.exec_command(command)

    # Print any errors from command execution
    for error_line in stderr.readlines():
        print(f"Error: {error_line}")

    print(f"Ensured {REMOTE_DIRECTORY} exists.")

    # Open SFTP session
    sftp = ssh_client.open_sftp()
    remote_path = f"{REMOTE_DIRECTORY}/sample.txt"

    # Upload file
    print("Uploading file via SFTP...")
    sftp.put(LOCAL_FILE, remote_path)
    print(f"Uploaded {LOCAL_FILE} to {remote_path}")

    # Close connections
    sftp.close()
    ssh_client.close()
    print("SSH session closed.")

except Exception as e:
    print(f"SSH/SFTP Error{e}") #Print any SSH/SFTP errors