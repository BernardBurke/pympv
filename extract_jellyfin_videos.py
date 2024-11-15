import requests
import os
import json
import collections

# Configuration (get values from environment variables)
JELLYFIN_SHOWS_LIB_TYPE = "tvshows"
JELLYFIN_MOVIES_LIB_TYPE = "movies"

seen_episodes = collections.defaultdict(set)  
seen_movies = collections.defaultdict(set)


def find_duplicates_shows(series_name, season_name, episode_name, episode_path, outfile_duplicates):
  """
  Stores episode information for later duplicate detection.

  Args:
    series_name: The name of the series.
    episode_name: The name of the episode.
    episode_path: The path to the episode file.
    outfile_duplicates: File object for writing duplicates (not used here).
  """
  episode_key = (series_name, episode_name, season_name)
  seen_episodes[episode_key].add(episode_path)

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

def main_shows():
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
                #log_json(series_data)
                #input("Press Enter to continue...")
                series_ids_names = [(series["Id"], series["Name"]) for series in series_data["Items"]]
                print(f"Found {len(series_ids_names)} series")
                for series_id, series_name in series_ids_names:
                    try:
                        episodes_data = req(f"/Shows/{series_id}/Episodes?userId={user_id}&fields=Path")
                        #log_json(episodes_data)
                        try:
                            season_name = episodes_data["Items"][0]["SeasonName"]
                        except (IndexError, KeyError) as e:
                            print(f"Error retrieving season name for series '{series_name}': {e}")
                            season_name = "Unknown"
                        #input(season_name)
                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching episodes for series '{series_name}' (ID: {series_id}): {e}")
                        continue

                    for episode in episodes_data["Items"]:
                        outfile.write(f"{series_name}\t{season_name}\t{episode['Name']}\t{episode['Path']}\n")
                        find_duplicates_shows(series_name, season_name, episode['Name'], episode['Path'],output_duplicates) 

                print(f"Finished processing library {lib_id}, sorting and finding duplicates...")
                sorted_episodes = sorted(seen_episodes.items())  # Sort by episode_key
                print(f"Found {len(sorted_episodes)} unique episodes.")
                for episode_key, paths in sorted_episodes:
                    outfile.write(f"{episode_key[0]}\t{episode_key[1]}\t{', '.join(paths)}\n")
                # Now iterate through the sorted items and find duplicates
                prev_episode_key = None
                for episode_key, paths in sorted_episodes:
                    if episode_key == prev_episode_key:
                        output_duplicates.write(f"Duplicate found: {episode_key[0]} - {episode_key[1]}\n")
                        for path in paths:
                            output_duplicates.write(f"  - {path}\n")
                            prev_episode_key = episode_key 


    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except OSError as e:
        print(f"Error writing to file: {e}")

def main_movies():
    """
    Fetches movie information from a library and writes it to a CSV file.
    """

    output_filename = "/tmp/jellyfin_movies.txt"

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
            lib_id = next((folder["Id"] for folder in media_folders["Items"] if folder["CollectionType"] == JELLYFIN_MOVIES_LIB_TYPE), None)
            if not lib_id:
                print(f"Library with CollectionType '{JELLYFIN_MOVIES_LIB_TYPE}' not found.")
                exit(1)

            # Write header to output file
            outfile.write("MovieName\tPath\n")

            # Get movie IDs and names
            movies_data = req(f"/Items?isMovie=true&userId={user_id}&parentId={lib_id}")
            log_json(movies_data)
            input("Press Enter to continue...")
            movie_ids_names = [(movie["Id"], movie["Name"]) for movie in movies_data["Items"]]
            log_json(movie_ids_names)
            input("Press and Press Enter to continue...")

            for movie_id, movie_name in movie_ids_names:
                try:
                    movie_data = req(f"/Movies/{movie_id}?userId={user_id}&fields=Path")
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching movie '{movie_name}' (ID: {movie_id}): {e}")
                    input("Press Enter to scarper") 
                    continue


                outfile.write(f"{movie_name}\t{movie_data['Path']}\n")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except OSError as e:
        print(f"Error writing to file: {e}")

def main():
    #main_shows()
    main_movies()

if __name__ == "__main__":
    main()