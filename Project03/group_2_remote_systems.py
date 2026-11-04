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
