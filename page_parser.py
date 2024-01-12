#!/usr/bin/env python3
import sys
import os
import tempfile
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import yt_dlp
import mpv
import shutil

OUTPUT_DIR = '/tmp/'
OUTPUT_FILENAME = OUTPUT_DIR + 'get.sh'

if os.path.isfile(OUTPUT_FILENAME):
    TF = tempfile.NamedTemporaryFile()
    OUTPUT_TEMPFILE = TF.name
    print(f" renaming {OUTPUT_FILENAME} to {OUTPUT_TEMPFILE}")
    os.rename( OUTPUT_FILENAME, OUTPUT_TEMPFILE )

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

if len(sys.argv) < 2:
    print ('Need to specify a query string')
    sys.exit(1)



SEARCH_STRING = sys.argv[1]

if len(sys.argv) < 3:
    URL = "https://heroero.com/search.php?q=" + SEARCH_STRING    
else:
    URL = sys.argv[2]
    SEARCH_STRING = sys.argv[1]

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
        #print(RANGE)
    return RANGE

def parse_identifier(FULL_PATH):
    print(f"Path: {FULL_PATH}")
    path=urlparse(FULL_PATH).path
    print(f"Path: {path}")
    chunks=path.split('/')
    ID=chunks[2]
    BASE_RANGE=get_base(ID)
    VIDEO_NAME=chunks[3]
    VIDEO_URL = "https://heroero.com/movie/" + BASE_RANGE + "/" + ID + "/" + ID + ".mp4"
    YTDL_COMMAND = "yt-dlp " + VIDEO_URL + " --output /tmp/doolb/" + VIDEO_NAME + ".mp4"
    #print(f"{ID} {BASE_RANGE} {VIDEO_NAME}")
    return YTDL_COMMAND , VIDEO_NAME, VIDEO_URL


def play_accept_cleanup(OUTPUT_TEMPFILE, VIDEO_PATH):
    player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True, osc=True)
    player.volume = 20
    player.screen = 1
    player.play(OUTPUT_TEMPFILE)
    player.wait_for_playback()
    answer = input(f"Keep {OUTPUT_TEMPFILE} video file as {VIDEO_PATH} ? (yes/no)")
    # Remove white spaces after the answers and convert the characters into lower cases.
    answer = answer.strip().lower()
    
    if answer in ["yes", "y", "1", ""]:
        shutil.copy(OUTPUT_TEMPFILE, VIDEO_PATH)
        print(f"{VIDEO_PATH} successfully downloaded and copied")
    elif answer in ["no", "n", "0"]:
        print('You answered no.') # or do something else
    else:
        print(f"Your answer can only be yes/y/1 or no/n/0. You answered {answer}")


def download_video(VIDEO_URL,VIDEO_NAME, VIDEO_PATH):
    TF = tempfile.NamedTemporaryFile()
    OUTPUT_TEMPFILE = TF.name

    # yt-dlp will create the output file and fail if it exists already... workaround is to delete temporary

    os.remove(OUTPUT_TEMPFILE)

    ydl_options = {
         'outtmpl': OUTPUT_TEMPFILE,
    }

    ydl = yt_dlp.YoutubeDL(ydl_options)

    try:
        ydl.download(VIDEO_URL)
    except KeyboardInterrupt:
        return
    except:
        print(f"Call to ytdl with {VIDEO_URL} failed")
        return


    print(f"{VIDEO_URL} will be downloaded")


    if os.path.isfile(OUTPUT_TEMPFILE):
         print(f"{VIDEO_NAME}  successfully downloaded")
         play_accept_cleanup(OUTPUT_TEMPFILE,VIDEO_PATH)
    else:
        print(f"{VIDEO_PATH} failed to download")



for a in soup.find_all('a', href=True):
    THIS_HREF = a['href']
    if SEARCH_STRING in THIS_HREF:
        THIS_YTDL, VIDEO_NAME, VIDEO_URL = parse_identifier(THIS_HREF)
        VIDEO_PATH = TARGET_DIR + VIDEO_NAME + ".mp4"
        if os.path.isfile(VIDEO_PATH):
            print(f"{VIDEO_PATH} already exists")
        else:
            #print(f"yt-dlp {THIS_URL} -o /tmp/blood/")
            FILE_HANDLE = open(OUTPUT_FILENAME, 'a')
            FILE_HANDLE.write(THIS_YTDL +"\n")
            download_video(VIDEO_URL, VIDEO_NAME, VIDEO_PATH)

try:
    FILE_HANDLE.close()
except NameError:
    print("No file to close.")
