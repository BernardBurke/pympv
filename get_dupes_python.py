import requests
import os
import json
from datetime import datetime

# Configuration (replace with your actual values or use environment variables)
#JELLYFIN_HOST = "https://jellyfin.local"  # Example
#JELLYFIN_API_KEY = "abc123abc123"  # Example
#JELLYFIN_USERNAME = "bob"  # Example
JELLYFIN_SHOWS_LIB_NAME = "Shows"  # Example


def get_env_var(name):
    import os
    # check if the environment variable exists and return it. Otherwise print an error and exit the script.
    if not os.environ.get(name):
        print(f"Error: Environment variable '{name}' not set.")
        exit(1)
    return os.environ.get(name)

JELLYFIN_USERNAME = get_env_var('JELLYFIN_USERNAME')
JELLYFIN_HOST = get_env_var('JELLYFIN_HOST')
#password = get_env_var('JELLYFIN_PASSWORD')
JELLYFIN_API_KEY = get_env_var('JELLYFIN_API_KEY')

# a general purpose logger for json that only logs output when the environment variable DEBUG is set to True
def log_json(data, message=">"):
    if os.environ.get('DEBUG') == 'True':
        print(message)
        print(json.dumps(data, indent=4))


# a general purpose logger for json that only logs output when the environment variable DEBUG is set to True
def log_general(message=">"):
    if os.environ.get('DEBUG') == 'True':
        print(message)
        


def req(endpoint):
    """Makes a request to the Jellyfin API."""
    headers = {
        "Accept": "application/json",
        "Authorization": f"MediaBrowser Token=\"{JELLYFIN_API_KEY}\""
    }
    url = f"{JELLYFIN_HOST}{endpoint}"
    log_general(f"Requesting: {url}")

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()

def main():
    """Finds and prints duplicate TV show episodes."""

    # Get user ID
    log_general("Getting user ID")
    users = req("/Users")
    user_id = next((user["Id"] for user in users if user["Name"] == JELLYFIN_USERNAME), None)
    if not user_id:
        print(f"User '{JELLYFIN_USERNAME}' not found.")
        exit(1)

    # Get library ID
    log_general("Getting library ID")
    media_folders = req("/Library/MediaFolders")
    lib_id = next((folder["Id"] for folder in media_folders["Items"] if folder["Name"] == JELLYFIN_SHOWS_LIB_NAME), None)
    if not lib_id:
        print(f"Library '{JELLYFIN_SHOWS_LIB_NAME}' not found.")
        exit(1)

    # Get series IDs
    log_general("Getting series IDs")
    series_data = req(f"/Items?isSeries=true&userId={user_id}&parentId={lib_id}")
    series_ids = [series["Id"] for series in series_data["Items"]]

    for series_id in series_ids:
        episodes_data = req(f"/Shows/{series_id}/Episodes?userId={user_id}&fields=DateCreated,Path")
        log_json(episodes_data)

        # Group episodes by season and episode number
        log_general("Grouping episodes by season and episode number")
        episodes_by_season_episode = {}
        for episode in episodes_data["Items"]:
            key = (episode["ParentIndexNumber"], episode["IndexNumber"])
            episodes_by_season_episode.setdefault(key, []).append(episode)

        # Find duplicates (episodes with the same season and episode number)
        duplicates = [episodes for episodes in episodes_by_season_episode.values() if len(episodes) > 1]

        if duplicates:
            series_name = duplicates[0][0]["SeriesName"]
            print(f"Series \"{series_name}\" has duplicates:")
            for dupe_episodes in duplicates:
                season_num = dupe_episodes[0]["ParentIndexNumber"]
                episode_num = dupe_episodes[0]["IndexNumber"]
                print(f"  {series_name} S{season_num:02d}E{episode_num:02d}")

                # Sort duplicates by creation date
                dupe_episodes.sort(key=lambda x: x["DateCreated"])
                for episode in dupe_episodes:
                    date_created = datetime.fromisoformat(episode["DateCreated"].replace('Z', '+00:00')).isoformat()
                    print(f"  - {date_created}: {episode['Path']}")

if __name__ == "__main__":
    main()