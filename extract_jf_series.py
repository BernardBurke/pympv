import requests
import os
import json

# Configuration (get values from environment variables)
JELLYFIN_SHOWS_LIB_TYPE = "tvshows"

def get_env_var(name):
    """Retrieves an environment variable and exits if it's not set."""
    import os
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
    response.raise_for_status()
    return response.json()

def main():
    """
    Fetches TV show episode information from multiple libraries 
    and writes it to a CSV file.
    """

    output_filename = "/tmp/jellyfin_episodes.txt"

    try:
        with open(output_filename, "w") as outfile:
            # Get user ID
            users = req("/Users")
            user_id = next((user["Id"] for user in users if user["Name"] == JELLYFIN_USERNAME), None)
            if not user_id:
                print(f"User '{JELLYFIN_USERNAME}' not found.")
                exit(1)

            # Get library IDs (multiple libraries with CollectionType == 'tvshows')
            media_folders = req("/Library/MediaFolders")
            lib_ids = [folder["Id"] for folder in media_folders["Items"] if folder["CollectionType"] == JELLYFIN_SHOWS_LIB_TYPE]

            if not lib_ids:
                print(f"No libraries found with CollectionType '{JELLYFIN_SHOWS_LIB_TYPE}'.")
                exit(1)

            # Write header to output file
            outfile.write("SeriesName\tEpisodeName\tPath\n")

            for lib_id in lib_ids:
                # Get series IDs and names
                print(f"Getting series IDs for library {lib_id}")
                series_data = req(f"/Items?isSeries=true&userId={user_id}&parentId={lib_id}")
                series_ids_names = [(series["Id"], series["Name"]) for series in series_data["Items"]]

                for series_id, series_name in series_ids_names:
                    episodes_data = req(f"/Shows/{series_id}/Episodes?userId={user_id}&fields=Path")

                    for episode in episodes_data["Items"]:
                        outfile.write(f"{series_name}\t{episode['Name']}\t{episode['Path']}\n")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except OSError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()