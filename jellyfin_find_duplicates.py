# #############################################################################
# Original Author: Gemini
#
# Description:  Python script to find duplicate movies and TV show episodes
#               in a single Jellyfin server.
#
# #############################################################################

import requests
import os
import sys
from configobj import ConfigObj
from collections import defaultdict
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# #############################################################################
# CONFIGURATION
# #############################################################################
CONFIG_PATH = "settings.ini"

def getConfig(path, section, option):
    """Reads a specific option from the config file."""
    config = ConfigObj(path)
    return config[section][option]

def createConfig(path):
    """Creates a default settings.ini file if one doesn't exist."""
    print(f"{Fore.CYAN}Creating a default 'settings.ini' file...{Style.RESET_ALL}")
    config = ConfigObj(path)
    config.filename = path

    general_section = {
        'APIKEY': 'YOUR_JELLYFIN_API_KEY',
        'URLBASE': 'http://127.0.0.1:8096/jellyfin/'
    }
    config['Jellyfin_Server'] = general_section

    config.write()
    print(f"{Fore.GREEN}'settings.ini' created. Please edit it with your server details and API key.{Style.RESET_ALL}")

def get_items_from_server(urlbase, apikey, item_type):
    """Fetches all items of a specific type (Movie, Episode) from a Jellyfin server."""
    print(f"\n{Fore.CYAN}Fetching all {item_type.lower()}s from the server...{Style.RESET_ALL}")
    all_items = []
    # Fetching all items from the server. Using a user ID is required.
    # The default user ID will work for this purpose as we're just querying the library.
    # A user with admin privileges is recommended for this API key.
    
    # First, get an admin user ID
    api_url_users = f"{urlbase}Users?api_key={apikey}"
    headers = {'accept': 'application/json'}
    try:
        response = requests.get(api_url_users, headers=headers, timeout=10)
        response.raise_for_status()
        admin_user_id = response.json()[0]['Id']
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error connecting to {urlbase} or fetching users: {e}{Style.RESET_ALL}")
        return []
    except IndexError:
        print(f"{Fore.RED}Could not find any users on the server.{Style.RESET_ALL}")
        return []

    # Now, fetch the items using the admin user ID
    api_url = f"{urlbase}Users/{admin_user_id}/Items?IncludeItemTypes={item_type}&Recursive=True&Fields=ProviderIds,Path,Overview,SeriesName,SeasonName,EpisodeNumber&api_key={apikey}"
    try:
        response = requests.get(api_url, headers=headers, timeout=60)
        response.raise_for_status()
        all_items = response.json().get('Items', [])
        print(f"{Fore.GREEN}Found {len(all_items)} {item_type.lower()}s.{Style.RESET_ALL}")
        return all_items
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error fetching {item_type.lower()} items: {e}{Style.RESET_ALL}")
        return []

def find_duplicate_movies(movies):
    """Finds duplicate movies by Provider ID or Name/Year."""
    print(f"\n{Fore.CYAN}Searching for duplicate movies...{Style.RESET_ALL}")
    duplicates = defaultdict(list)
    
    # Group by provider IDs first (most reliable)
    for movie in movies:
        providers = movie.get('ProviderIds', {})
        found_id = False
        for prov_key, prov_id in providers.items():
            if prov_id:
                duplicates[f"{prov_key}:{prov_id}"].append(movie)
                found_id = True
                break
        
        # If no provider ID, fall back to name and year
        if not found_id:
            name = movie.get('Name')
            year = movie.get('ProductionYear')
            if name and year:
                duplicates[f"name:{name} ({year})"].append(movie)
            elif name:
                duplicates[f"name:{name}"].append(movie)

    # Filter out non-duplicates
    duplicate_movies = {key: items for key, items in duplicates.items() if len(items) > 1}
    return duplicate_movies

def find_duplicate_episodes(episodes):
    """Finds duplicate episodes by Series, Season, and Episode number."""
    print(f"\n{Fore.CYAN}Searching for duplicate TV show episodes...{Style.RESET_ALL}")
    duplicates = defaultdict(list)
    
    for episode in episodes:
        series_name = episode.get('SeriesName')
        season_name = episode.get('SeasonName')
        episode_number = episode.get('IndexNumber')
        
        if series_name and season_name and episode_number is not None:
            # Create a unique key for each episode
            key = f"{series_name} - {season_name} - E{episode_number:02d}"
            duplicates[key].append(episode)
            
    # Filter out non-duplicates
    duplicate_episodes = {key: items for key, items in duplicates.items() if len(items) > 1}
    return duplicate_episodes

def print_duplicates(duplicate_items):
    """Prints the found duplicates in a human-readable format."""
    total_duplicates_found = 0
    if not duplicate_items:
        print(f"{Fore.GREEN}No duplicates found.{Style.RESET_ALL}")
        return

    for key, items in duplicate_items.items():
        total_duplicates_found += len(items)
        print(f"\n{Fore.YELLOW}Duplicate ID: {key}{Style.RESET_ALL}")
        for item in items:
            name = item.get('Name')
            path = item.get('Path')
            size_mb = round(item.get('Size', 0) / (1024 * 1024), 2)
            print(f"  - {Fore.WHITE}{name}{Style.RESET_ALL}")
            print(f"    {Fore.LIGHTBLACK_EX}Path: {path}{Style.RESET_ALL}")
            print(f"    {Fore.LIGHTBLACK_EX}Size: {size_mb} MB{Style.RESET_ALL}")

    print(f"\n\n{Fore.MAGENTA}##### Duplicate Check Complete #####{Style.RESET_ALL}")
    print(f"{Fore.RED}Found {total_duplicates_found} items with duplicates.{Style.RESET_ALL}")

if __name__ == "__main__":
    # Check if config file exists
    if not os.path.exists(CONFIG_PATH):
        createConfig(CONFIG_PATH)
        sys.exit()

    # Read server configuration
    try:
        urlbase = getConfig(CONFIG_PATH, 'Jellyfin_Server', 'URLBASE')
        apikey = getConfig(CONFIG_PATH, 'Jellyfin_Server', 'APIKEY')
        if apikey == "YOUR_JELLYFIN_API_KEY":
            print(f"{Fore.RED}Please edit 'settings.ini' and set the 'APIKEY' variable.{Style.RESET_ALL}")
            sys.exit()
    except Exception as e:
        print(f"{Fore.RED}Error reading server configuration: {e}{Style.RESET_ALL}")
        sys.exit()
        
    # Find duplicate movies
    movies = get_items_from_server(urlbase, apikey, 'Movie')
    if movies:
        duplicate_movies = find_duplicate_movies(movies)
        print_duplicates(duplicate_movies)

    # Find duplicate TV episodes
    episodes = get_items_from_server(urlbase, apikey, 'Episode')
    if episodes:
        duplicate_episodes = find_duplicate_episodes(episodes)
        print_duplicates(duplicate_episodes)