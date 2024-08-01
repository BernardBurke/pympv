#!/usr/bin/env python3

# This script takes a URL and downloads all the images from the site
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import shutil

if len(sys.argv) < 2:
    print ('Need to specify a URL')
    sys.exit(1)

# debug function - when environment variable DEBUG is set to 1, print the contents of params
def debug_write(params):
    if os.environ.get('DEBUG') == '1':
        print(params)


URL = sys.argv[1]
debug_write(URL)

page = requests.get(URL)

debug_write(page)
soup = BeautifulSoup(page.content, "html.parser")
debug_write(soup)



def get_images(soup):
    images = []
    for img in soup.find_all('img'):
        images.append(img.get('src'))
    return images



def download_images(images):
    for image in images:
        try:
            response = requests.get(image, stream=True)
            filename = os.path.basename(urlparse(image).path)
            with open(filename, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        except Exception as e:
            print(f"Failed to download {image}: {e}")

# This function takes the base page on a site and walks through the subsequent pages
# Calling get_images and download_images on each page


# call get_images and download_images on the URL specified - log the steps using the debug_write function
images = get_images(soup)
debug_write(images)
download_images(images)
debug_write('done')
