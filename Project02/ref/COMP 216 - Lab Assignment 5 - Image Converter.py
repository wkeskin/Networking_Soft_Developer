'''
Created for COMP216

Downloads an image and convert the image formate
'''

import requests
from PIL import Image

def download_image(image_url):
    response = requests.get(image_url)              #Make a HTTP GET request to fetch a response object with an image
    image_data = response.content                   #Retrieve the image payload from the response object
    with open('photo.jpg', 'wb') as image_file:     #Capture the image data in binary format as a local file
        image_file.write(image_data)

def convert_image_png(image_file):
    image = Image.open(image_file)                  #Use Pillow (PIL) to open image file object 
    image.save('photo.png', 'png')                  #Save the image in a new format (i.e., new file extension)

def image_properties(image_file):
    image = Image.open(image_file)                  #Use Image module from Pillow (PIL) to open image file 
    print(image.format, image.size, image.mode)     #Use the Image class attributes to capture image properties 

if __name__ == "__main__":
    url = 'https://images.unsplash.com/photo-1504208434309-cb69f4fe52b0'
    image = download_image(url)
    
    convert_image_png('photo.jpg')
    image_properties('photo.jpg')
    image_properties('photo.png')

