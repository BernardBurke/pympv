#!/usr/bin/env python3
# this is broken https://www.aznude.com/view/movie/p/pierwszamilosc.html
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

# if os.path.isfile(OUTPUT_FILENAME):
#     TF = tempfile.NamedTemporaryFile()
#     OUTPUT_TEMPFILE = TF.name
#     print(f" renaming {OUTPUT_FILENAME} to {OUTPUT_TEMPFILE}")
#     os.rename( OUTPUT_FILENAME, OUTPUT_TEMPFILE )

# try:
#     TARGET_PATH = os.environ["SCREEN_TARGET_PATH"]
# except KeyError:
#     print('SCREEN_TARGET_PATH not defined')
#     sys.exit(1)


# if os.path.exists(TARGET_PATH):
#     TARGET_DIR = TARGET_PATH
# else:
#     print('No target path defined for TARGET_PATH')
#     sys.exit(1)

# ydl_options = {
#     'outputmpl': OUTPUT_DIR
# }

# if len(sys.argv) < 2:
#     print ('Need to specify a query string')
#     sys.exit(1)




# if len(sys.argv) < 3:
#     URL = "https://heroero.com/search.php?q=" + SEARCH_STRING    
# else:
#     URL = sys.argv[2]
#     SEARCH_STRING = sys.argv[1]

# page = requests.get(URL)
# soup = BeautifulSoup(page.content, "html.parser")

    

# def get_base(ID):
#     LEN = len(ID) - 1
#     STR_ID = str(ID)
#     TOP_RANGE = STR_ID[:-LEN]
#     NEXT_LEN = LEN - 1
#     NEXT_DIGIT = STR_ID[1:-NEXT_LEN]
#     ZERO_FILL = "0" * LEN
#     RANGE = TOP_RANGE + ZERO_FILL
#     #print (TOP_RANGE)
#     if int(RANGE) > 9999:
#         #print ('Fixing range')
#         #print (f'NEXT_DIGIT = {NEXT_DIGIT}')
#         ZERO_FILL = "0" * (LEN - 1)
#         RANGE=TOP_RANGE + NEXT_DIGIT + ZERO_FILL
#         #print(RANGE)
#     return RANGE

# def parse_identifier(FULL_PATH):
#     print(f"Path: {FULL_PATH}")
#     path=urlparse(FULL_PATH).path
#     print(f"Path: {path}")
#     chunks=path.split('/')
#     ID=chunks[2]
#     BASE_RANGE=get_base(ID)
#     VIDEO_NAME=chunks[3]
#     VIDEO_URL = "https://heroero.com/movie/" + BASE_RANGE + "/" + ID + "/" + ID + ".mp4"
#     YTDL_COMMAND = "yt-dlp " + VIDEO_URL + " --output /tmp/doolb/" + VIDEO_NAME + ".mp4"
#     #print(f"{ID} {BASE_RANGE} {VIDEO_NAME}")
#     return YTDL_COMMAND , VIDEO_NAME, VIDEO_URL


# def play_accept_cleanup(OUTPUT_TEMPFILE, VIDEO_PATH):
#     player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True, osc=True)
#     player.volume = 20
#     player.screen = 2
#     player.play(OUTPUT_TEMPFILE)
#     player.wait_for_playback()
#     answer = input(f"Keep {OUTPUT_TEMPFILE} video file as {VIDEO_PATH} ? (yes/no)")
#     # Remove white spaces after the answers and convert the characters into lower cases.
#     answer = answer.strip().lower()
    
#     if answer in ["yes", "y", "1", ""]:
#         shutil.copy(OUTPUT_TEMPFILE, VIDEO_PATH)
#         print(f"{VIDEO_PATH} successfully downloaded and copied")
#     elif answer in ["no", "n", "0"]:
#         print('You answered no.') # or do something else
#     else:
#         print(f"Your answer can only be yes/y/1 or no/n/0. You answered {answer}")


def download_video(vURL, filename):

    filename = "/home/ben/bikini/grls2/a2znudes/" + filename

    ydl_options = {
         'outtmpl': filename,
    }

    ydl = yt_dlp.YoutubeDL(ydl_options)

    try:
        ydl.download(vURL)
    except KeyboardInterrupt:
        return
    except:
        print(f"Call to ytdl with {vURL} failed")
        return


    print(f"{vURL} will be downloaded")


    if os.path.isfile(filename):
         print(f"{vURL}  successfully downloaded")
    else:
        print(f"{VIDEO_PATH} failed to download")


FQDN = "https://www.aznude.com"
MOVIE_NAME = sys.argv[1]
first_characters = MOVIE_NAME[0]
if len(sys.argv) > 2:
    if sys.argv[2] == 'celeb':
        SEARCH_STRING = FQDN + "/view/celeb/" + first_characters + "/" + MOVIE_NAME + ".html"
else:
    SEARCH_STRING = FQDN + "/view/movie/" + first_characters + "/" + MOVIE_NAME + ".html"
MOVIE_NAME = MOVIE_NAME.split('-')
MOVIE_NAME = MOVIE_NAME[0]

                   
print(SEARCH_STRING) 


def switch_cdn(child_href):
    cdn_style = child_href.split('/')

    print(f"Length of cdn style is {len(cdn_style)}")

    if len(cdn_style) == 5:
        print(f"I am a azncdn style cdn {len(cdn_style)} {child_href}")
        movieSeparator = '/' + MOVIE_NAME 
        actorName = ""
        fname = cdn_style[4]
    else:
        print(f"I am a skin cdn style")
        movieSeparator = MOVIE_NAME + '/' 
        #actorName = cdn_style[3]
        #fname = actorName + '-' + cdn_style[5]
        fname = cdn_style[5]
        print(f" my child href is {len(cdn_style)} {child_href}") 
    top_of_path = urlparse(child_href).path
    add_proto = "https:" + child_href
    add_proto = child_href
    #fname = MOVIE_NAME +  "-" + actorName + "-" + fname
    print(f" I created {fname} and will pull from {add_proto}")
    download_video(add_proto, fname)


def get_child(HREF):
    # print(f"{HREF}")
    # top_of_path = urlparse(HREF).path
    # chunks=top_of_path.split('/')
    # print(f"Chunk {chunks[2]}")
    next_path = FQDN + HREF
    #print(f"I would fetch {next_path}")
    page = requests.get(next_path)
    soup = BeautifulSoup(page.content, "html.parser")
    for a in soup.find_all('a', href=True):
        next_href = a['href']
        if ".mp4" in next_href:
            print(f"{next_href} is sent")
            switch_cdn(next_href)
            # temp_movie = MOVIE_NAME + "/"
            # print(f"Next {next_href}")
            # print(f"tempmovie {temp_movie} ")
            # chunks = next_href.split(temp_movie)
            # print(f"length of chunks {len(chunks)}")
            # #print(f"Fetching {chunks[1]}")
            # chumps = next_href.split('/')
            # print(f" Length: {len(chunks)} chunks and {len(chumps)} chumps")
            # actor = chumps[3]
            # print(f"{actor} actor")
            # add_proto = "https:" + next_href
            # if ( len(chunks) == 2 and len(chumps) == 6 ):
            #     fname = MOVIE_NAME +  "-" + actor + "-" + chunks[1] 
            # print(add_proto, fname)

            #     download_video(add_proto, fname)
            # else:
            #     print(f"Skip downloading for strangely formatted Chunks")

page = requests.get(SEARCH_STRING)
soup = BeautifulSoup(page.content, "html.parser")

ANYTHING_FOUND = False    

for a in soup.find_all('a', href=True):
    
    THIS_HREF = a['href']
    #print(f"Processing {THIS_HREF} and looking for {MOVIE_NAME}")
    if MOVIE_NAME in THIS_HREF:
        if ".html" in THIS_HREF:
            ANYTHING_FOUND = True
            get_child(THIS_HREF)
    if not ANYTHING_FOUND:
        #print(f"I didn't find anything - looking for anzcdn")
        if "/azncdn" in THIS_HREF:
            print(f"Fixup for {THIS_HREF}")
            if ".html" in THIS_HREF:
                ANYTHING_FOUND = True
                get_child(THIS_HREF)

            #print(f"This page is is {THIS_HREF}")
    # if SEARCH_STRING in THIS_HREF:
    #     THIS_YTDL, VIDEO_NAME, VIDEO_URL = parse_identifier(THIS_HREF)
    #     VIDEO_PATH = TARGET_DIR + VIDEO_NAME + ".mp4"
    #     if os.path.isfile(VIDEO_PATH):
    #         print(f"{VIDEO_PATH} already exists")
    #     else:
    #         #print(f"yt-dlp {THIS_URL} -o /tmp/blood/")
    #         FILE_HANDLE = open(OUTPUT_FILENAME, 'a')
    #         FILE_HANDLE.write(THIS_YTDL +"\n")
    #         download_video(VIDEO_URL, VIDEO_NAME, VIDEO_PATH)

try:
    FILE_HANDLE.close()
except NameError:
    print("No file to close.")
