#!/usr/bin/env python3
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import yt_dlp
OUTPUT_DIR = '/tmp/'

try:
    TARGET_PATH = os.environ["SCREEN_TARGET_PATH"]
except KeyError:
    print('SCREEN_TARGET_PATH not defined')
    sys.exit(1)


if os.path.exists(TARGET_PATH):
    TARGET_DIR = TARGET_PATH
else:
    print('No target path defined for TARGET_PATH')
    sys.exit(1)

ydl_options = {
    'outputmpl': OUTPUT_DIR
}

if sys.argv[1] == '':
    print ('Need to specify a query string')
    sys.exit(1)

SEARCH_STRING = sys.argv[1]

URL = "https://heroero.com/search.php?q=" + SEARCH_STRING
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

    

def get_base(ID):
    LEN = len(ID) - 1
    STR_ID = str(ID)
    TOP_RANGE = STR_ID[:-LEN]
    NEXT_LEN = LEN - 1
    NEXT_DIGIT = STR_ID[1:-NEXT_LEN]
    ZERO_FILL = "0" * LEN
    RANGE = TOP_RANGE + ZERO_FILL
    #print (TOP_RANGE)
    if int(RANGE) > 9999:
        #print ('Fixing range')
        #print (f'NEXT_DIGIT = {NEXT_DIGIT}')
        ZERO_FILL = "0" * (LEN - 1)
        RANGE=TOP_RANGE + NEXT_DIGIT + ZERO_FILL
        print(RANGE)
    return RANGE

def parse_identifier(FULL_PATH):
    path=urlparse(FULL_PATH).path
    chunks=path.split('/')
    ID=chunks[2]
    BASE_RANGE=get_base(ID)
    VIDEO_NAME=chunks[3]
    VIDEO_URL = "https://heroero.com/movie/" + BASE_RANGE + "/" + ID + "/" + ID + ".mp4"
    YTDL_COMMAND = "yt-dlp " + VIDEO_URL + " --output /tmp/blood/" + VIDEO_NAME + ".mp4"
    #print(f"{ID} {BASE_RANGE} {VIDEO_NAME}")
    return YTDL_COMMAND , VIDEO_NAME

for a in soup.find_all('a', href=True):
    THIS_HREF = a['href']
    if SEARCH_STRING in THIS_HREF:
        THIS_YTDL, VIDEO_NAME = parse_identifier(THIS_HREF)
        VIDEO_PATH = TARGET_DIR + VIDEO_NAME + ".mp4"
        if os.path.isfile(VIDEO_PATH):
            print(f"{VIDEO_PATH} already exists")
        else:
            #print(f"yt-dlp {THIS_URL} -o /tmp/blood/")
            print(THIS_YTDL)
            #with yt_dlp.YoutubeDL(ydl_options) as ydl:
            #    ydl.download(THIS_URL)
            #print("Found the URL:", a['href'])