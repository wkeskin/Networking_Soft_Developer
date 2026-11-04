'''
Created by Narendra for COMP216

Downloads a file from a 'real' web server
'''

import requests

pathname = 'client_download/text.txt'
requested_file = 'test.txt'
URL = f'http://127.0.0.1:5000/download/{requested_file}'        #Request URL

r = requests.get(URL, stream=True)                              #Make a HTTP GET request

with open(pathname, 'wb') as fd:
    for chunk in r.iter_content(chunk_size=50):                 #Ridiculously small size
        print('+', end='')                                      #Provide feedback in the terminal
        fd.write(chunk)                                         #Write the bit to file
    print('\n...download completed')                            #Completion indicator