import requests
import os
import json

# Configuration (get values from environment variables)
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
JELLYFIN_API_KEY = get_env_var('JELLYFIN_API_KEY')

def req(endpoint):
    """Makes a request to the Jellyfin API."""
    headers = {
        "Accept": "application/json",
        "Authorization": f"MediaBrowser Token=\"{JELLYFIN_API_KEY}\""
    }
    url = f"{JELLYFIN_HOST}{endpoint}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()

def main():
    """Fetches TV show episode information and writes it to a file."""

    output_filename = "/tmp/jellyfin_episodes.txt"  # Or any other desired path

    try:
        with open(output_filename, "w") as outfile:
            # Get user ID
            users = req("/Users")
            user_id = next((user["Id"] for user in users if user["Name"] == JELLYFIN_USERNAME), None)
            if not user_id:
                print(f"User '{JELLYFIN_USERNAME}' not found.")
                exit(1)

            # Get library ID
            media_folders = req("/Library/MediaFolders")
            lib_id = next((folder["Id"] for folder in media_folders["Items"] if folder["Name"] == JELLYFIN_SHOWS_LIB_NAME), None)
            if not lib_id:
                print(f"Library '{JELLYFIN_SHOWS_LIB_NAME}' not found.")
                exit(1)

            # Get series IDs and names
            series_data = req(f"/Items?isSeries=true&userId={user_id}&parentId={lib_id}")
            series_ids_names = [(series["Id"], series["Name"]) for series in series_data["Items"]]

            # Write header to output file
            outfile.write("SeriesName,EpisodeName,Path\n")  # Write header

            for series_id, series_name in series_ids_names:
                episodes_data = req(f"/Shows/{series_id}/Episodes?userId={user_id}&fields=Path")

                for episode in episodes_data["Items"]:
                    outfile.write(f"{series_name},{episode['Name']},{episode['Path']}\n")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except OSError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()