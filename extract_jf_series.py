import requests
import os
import json
import collections

# Configuration (get values from environment variables)
JELLYFIN_SHOWS_LIB_TYPE = "tvshows"

seen_episodes = collections.defaultdict(set)  


def find_duplicates(series_name, episode_name, episode_path, outfile_duplicates):
  """
  Identifies and writes duplicate series and episode names to a file.

  Args:
    series_name: The name of the series.
    episode_name: The name of the episode.
    episode_path: The path to the episode file.
    outfile_duplicates: File object for writing duplicates.
  """

  episode_key = (series_name, episode_name)
  
  # Add the current episode path to the set
  seen_episodes[episode_key].add(episode_path)

  # Check if there are multiple paths for the same episode key
  if len(seen_episodes[episode_key]) > 1:  
      outfile_duplicates.write(f"Duplicate found: {series_name} - {episode_name}\n")
      for path in seen_episodes[episode_key]:
          outfile_duplicates.write(f"  - {path}\n")

def log_json(data, message=">"):
    if os.environ.get('DEBUG') == 'True':
        print(message)
        print(json.dumps(data, indent=4))

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
    print(f"Requesting: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    """
    Fetches TV show episode information from multiple libraries 
    and writes it to a CSV file.
    """

    output_filename = "/tmp/jellyfin_episodes.txt"
    output_dupes = "/tmp/jellyfin_duplicates.txt"

    try:
        #with open(output_filename, "w") as outfile:
        with open(output_filename, "w") as outfile, open(output_dupes, "w") as output_duplicates: 

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
                print(f"Found {len(series_ids_names)} series")
                for series_id, series_name in series_ids_names:
                    try:
                        episodes_data = req(f"/Shows/{series_id}/Episodes?userId={user_id}&fields=Path")
                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching episodes for series '{series_name}' (ID: {series_id}): {e}")
                        continue

                    for episode in episodes_data["Items"]:
                        outfile.write(f"{series_name}\t{episode['Name']}\t{episode['Path']}\n")
                        find_duplicates(series_name, episode['Name'], episode['Path'],output_duplicates) 


    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except OSError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()