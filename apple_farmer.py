#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import yt_dlp

OUTPUT_DIR = "/tmp/"

ydl_options = {
    'outputmpl': OUTPUT_DIR
}

if sys.argv[1] == '':
    print ('Need to specify a query string')
    sys.exit(1)

SEARCH_STRING = sys.argv[1]
REFINE_STRING = sys.argv[2]
URL = SEARCH_STRING
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

def get_base(ID):
    LEN = len(ID) - 1
    STR_ID = str(ID)
    TOP_RANGE = STR_ID[:-LEN]
    ZERO_FILL = "0" * LEN
    RANGE = TOP_RANGE + ZERO_FILL
    #print (TOP_RANGE)
    return RANGE

def parse_identifier(FULL_PATH):
    path=urlparse(FULL_PATH).path
    chunks=path.split('/')
    ID=chunks[2]
    BASE_RANGE=get_base(ID)
    VIDEO_NAME=chunks[3]
    VIDEO_URL = "https://ro.com/movie/" + BASE_RANGE + "/" + ID + "/" + ID + ".mp4"
    YTDL_COMMAND = "yt-dlp " + VIDEO_URL + " --output /tmp/" + VIDEO_NAME + ".mp4"
    #print(f"{ID} {BASE_RANGE} {VIDEO_NAME}")
    return YTDL_COMMAND

for a in soup.find_all('a', href=True):
    THIS_HREF = a['href']
    if REFINE_STRING in THIS_HREF:
        #THIS_URL=parse_identifier(THIS_HREF)
        #print(f"yt-dlp {THIS_URL} -o /tmp/")
        print(THIS_HREF)
        #with yt_dlp.YoutubeDL(ydl_options) as ydl:
        #    ydl.download(THIS_URL)
        #print("Found the URL:", a['href'])