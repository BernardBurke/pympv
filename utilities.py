import os
import subprocess
import random
import logging


try:
    import mpv
except ImportError:
    mpv = None  # Or set a flag to indicate mpv is not available

# Logging setup
LOG_FILE = "/tmp/mpv_utlities.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

def logmessage(message):
    logging.info(message)

def message(*args):
    script_name = os.path.basename(__file__).split('.')[0]
    message_text = f"{script_name} {' '.join(args)}"
    print(message_text)
    logmessage(message_text)

def shuffle_edl(edl_file, shuffle_num=100, shuffle_restore="N"):
    temp_file = "/tmp/shuffled_edl_{}".format(random.randint(1000, 9999))
    with open(temp_file, "w") as f:
        f.write("# mpv EDL v0\n")
        if os.path.exists(edl_file):
            with open(edl_file, "r") as infile:
                lines = [line for line in infile if not line.startswith("#")]
                random.shuffle(lines)
                f.writelines(lines[:shuffle_num])
        else:
            return 1

    message(f"shuffle_edl wrote {temp_file} - and SHUFFLE_RESTORE is {shuffle_restore}")
    if shuffle_restore.upper() == "Y":
        subprocess.run(["cp", "-v", temp_file, edl_file])

def get_subtitle_related_media(subtitle_file):
    if not os.path.exists(subtitle_file):
        exit(1)

    media_extensions = [".m4a", ".mp3", ".webm", ".mpv", ".mkv", ".avi", ".wmv"]
    directory = os.path.dirname(subtitle_file)
    filename = os.path.basename(subtitle_file).split(".")[0]

    for ext in media_extensions:
        media_file = os.path.join(directory, filename + ext)
        if os.path.exists(media_file):
            return media_file

    exit(1) 

def get_random_subtitles(search_term):
    command = f'find {AUDEY} \( -iname "*.srt" -o -iname "*.vtt" \) -exec grep -il "{search_term}" {{}} \; | shuf -n 1'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()



def get_random_edl_file(search_term):
    command = f'find {EDLROOT} -iname "*{search_term}*.edl" | grep -iv windows | shuf -n 1'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    result_file = result.stdout.strip()
    if not result_file:
        exit(1)
    return result_file

def get_random_video():
    command = 'find {} -iname "*.mp4" -o -iname "*.avi" -o -iname "*.mkv" -o -iname "*.webm" -o -iname "*.wmv" | shuf -n 1'.format(GRLSRC)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_length(media_file):
    if not os.path.exists(media_file):
        return "0"

    command = f'ffprobe -v quiet -of csv=p=0 -show_entries format=duration "{media_file}"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    length = result.stdout.strip().split(".")[0]
    return length

def minimum_length(media_file, min_length=300):
    length = int(get_length(media_file))
    return length >= min_length

def validate_edl(edl_file):
    any_problems = False
    edl_file_only = os.path.basename(edl_file)
    temp_edl_dir = "/tmp"
    temp_edl_file = os.path.join(temp_edl_dir, edl_file_only)

    message(f"{temp_edl_dir} is the correction directory")

    if not os.path.exists(edl_file):
        print(f"{edl_file} does not exist")
        return 1

    with open(temp_edl_file, "w") as tmp_f:
        tmp_f.write("# mpv EDL v0\n")
        with open(edl_file, "r") as f:
            for line in f:
                if not line.startswith("#"):
                    parts = line.strip().split(",")
                    if len(parts) != 3:
                        any_problems = True
                        message(f"invalid line format in {edl_file}: {line}")
                        tmp_f.write(f"# {line}")
                    else:
                        file_path, start, end = parts
                        if not os.path.exists(file_path):
                            any_problems = True
                            message(f"{file_path} does not exist")
                            tmp_f.write(f"# {line}")
                        elif not start or not end:
                            any_problems = True
                            message(f"invalid start or end time in {edl_file} on line {line}")
                            tmp_f.write(f"# {line}")
                        else:
                            tmp_f.write(line)
                else:
                    tmp_f.write(line)

    message(f"The temp EDL directory is {temp_edl_dir}")

    if any_problems:
        message(f"{edl_file} had problems. A corrected version written as {temp_edl_file}")
        return 1
    else:
        os.remove(temp_edl_file)
        print(f"no problems in {temp_edl_file}")

def convert_edl_file_content(edl_file, player_file):
    max_size = os.sysconf('SC_ARG_MAX')
    nominal_max = max_size - 100
    isize = 0

    if not os.path.exists(edl_file):
        message(f"EDL_FILE provided does not exist - {edl_file}")
        exit(1)
    else:
        message(f"Processing {edl_file}")

    if not os.path.exists(player_file):
        message(f"PLAYER_FILE provided does not exist - {player_file}")
        exit(1)
    else:
        message(f"Processing {player_file}")

    with open(player_file, "a") as pf:
        with open(edl_file, "r") as f:
            for line in f:
                file, start, length = line.strip().split(",")
                lion = f'--{{ "{file}" --start={start} --length={length} --}} \\'
                strlen = len(lion)
                isize += strlen
                if isize > max_size:
                    message(f"command became too long {isize}")
                    exit(1)
                pf.write(lion + "\n")

    message(f"{edl_file} became {isize} in length vs {max_size}")

def convert_edl_file(edl_file, player_file=None, screen=0, profile=None):
    if not os.path.exists(edl_file):
        message(f"{edl_file} does not exist")
        exit(1)
    else:
        message(f"Processing {edl_file}")
        if player_file is None:
            player_file = "/tmp/temp_player_file_{}".format(random.randint(1000, 9999))
        temp_edl_file = "/tmp/temp_edl_file_{}".format(random.randint(1000, 9999))

        with open(temp_edl_file, "w") as tmp_f:
            with open(edl_file, "r") as f:
                for line in f:
                    if not line.startswith("#"):
                        tmp_f.write(line)

        if profile is None:
            with open(player_file, "w") as pf:
                pf.write(f"nohup mpv --screen={screen} \\\n")
        else:
            with open(player_file, "w") as pf:
                pf.write(f"nohup mpv --screen={screen} --profile={profile} \\\n")

        convert_edl_file_content(temp_edl_file, player_file)
