# #############################################################################
# Original Author: CobayeGunther
# Modified for Jellyfin-to-Jellyfin single-user sync - Ben Burke and Gemini
#
# Description: 	Python script to migrate watched content for a single user
#				from a source Jellyfin server to a destination Jellyfin server.
#
# #############################################################################

import json
import requests
import sys
import os
from configobj import ConfigObj

# #############################################################################
# CONFIGURATION: Set the username you want to sync here.
# #############################################################################
TARGET_USERNAME = "ben"
# #############################################################################

def getConfig(path, section, option):
    """Reads a specific option from the config file."""
    config = ConfigObj(path)
    return config[section][option]

def createConfig(path):
    """Creates a default settings.ini file if one doesn't exist."""
    print("Creating a default 'settings.ini' file...")
    config = ConfigObj(path)
    config.filename = path

    source_section = {
        'APIKEY': 'YOUR_SOURCE_JELLYFIN_API_KEY',
        'URLBASE': 'http://127.0.0.1:8096/jellyfin/'
    }
    config['Jellyfin_Source'] = source_section

    destination_section = {
        'APIKEY': 'YOUR_DESTINATION_JELLYFIN_API_KEY',
        'URLBASE': 'http://192.168.1.100:8096/jellyfin/'
    }
    config['Jellyfin_Destination'] = destination_section

    config.write()
    print("'settings.ini' created. Please edit it with your server details and API keys.")

def get_user_id(urlbase, apikey, username):
    """Fetches the User ID for a given username from a Jellyfin server."""
    api_url = f"{urlbase}Users?api_key={apikey}"
    headers = {'accept': 'application/json'}
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        users = response.json()
        for user in users:
            if user['Name'].lower() == username.lower():
                print(f"Found user '{username}' with ID: {user['Id']}")
                return user['Id']
        return None
    except requests.exceptions.RequestException as e:
        print(f"\033[91mError connecting to {urlbase}: {e}\033[00m")
        return None

def get_source_watched_status(urlbase, apikey, user_id):
    """Gets all watched media for a user from the source server."""
    print("\nFetching watched status from the SOURCE server...")
    migration_data = []
    api_url = f"{urlbase}Users/{user_id}/Items?Filters=IsPlayed&IncludeItemTypes=Movie,Episode&Recursive=True&Fields=ProviderIds&api_key={apikey}"
    headers = {'accept': 'application/json'}
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        items = response.json().get('Items', [])
        for item in items:
            media_info = {
                'Type': item.get('Type'),
                'Name': item.get('Name'),
                'ProviderIds': item.get('ProviderIds', {})
            }
            migration_data.append(media_info)
        print(f"\033[92mFound {len(migration_data)} watched items on the source server.\033[00m")
        return migration_data
    except requests.exceptions.RequestException as e:
        print(f"\033[91mError fetching watched items: {e}\033[00m")
        return []

def find_item_in_destination(source_item, dest_library):
    """Finds a corresponding item in the destination library using ProviderIds or Name."""
    # First, try matching by Provider IDs (most reliable)
    for dest_item in dest_library:
        if dest_item['Type'] != source_item['Type']:
            continue
        # Compare provider IDs
        source_providers = source_item.get('ProviderIds', {})
        dest_providers = dest_item.get('ProviderIds', {})
        if not source_providers or not dest_providers:
            continue
        
        for prov_key, prov_id in source_providers.items():
            if dest_providers.get(prov_key) == prov_id:
                return dest_item['Id']

    # As a fallback, try matching by name
    for dest_item in dest_library:
        if dest_item['Type'] == source_item['Type'] and dest_item['Name'] == source_item['Name']:
            return dest_item['Id']
            
    return None

def sync_to_destination(urlbase, apikey, user_id, migration_data):
    """Syncs the watched status to the destination server."""
    print("\nStarting sync to the DESTINATION server...")
    
    # 1. Get the entire library from the destination server for matching
    print("Fetching full library from destination server (this may take a moment)...")
    library_url = f"{urlbase}Users/{user_id}/Items?Recursive=True&IncludeItemTypes=Movie,Episode&Fields=ProviderIds&api_key={apikey}"
    headers = {'accept': 'application/json'}
    try:
        response = requests.get(library_url, headers=headers, timeout=60)
        response.raise_for_status()
        destination_library = response.json().get('Items', [])
        print(f"Destination library has {len(destination_library)} items.")
    except requests.exceptions.RequestException as e:
        print(f"\033[91mCould not fetch destination library: {e}\033[00m")
        return

    # 2. Iterate and sync each item
    ok_count = 0
    nok_count = 0
    total_items = len(migration_data)
    
    for i, source_item in enumerate(migration_data):
        item_id = find_item_in_destination(source_item, destination_library)
        
        if item_id:
            mark_watched_url = f"{urlbase}Users/{user_id}/PlayedItems/{item_id}?api_key={apikey}"
            try:
                post_response = requests.post(mark_watched_url, headers=headers, timeout=10)
                if post_response.status_code == 200:
                    ok_count += 1
                    print(f"\033[92mOK ({i+1}/{total_items}): Marked '{source_item['Name']}' as watched.\033[00m")
                else:
                    nok_count += 1
                    print(f"\033[91mFAIL ({i+1}/{total_items}): Could not mark '{source_item['Name']}' as watched. Status: {post_response.status_code}\033[00m")
            except requests.exceptions.RequestException as e:
                nok_count += 1
                print(f"\033[91mFAIL ({i+1}/{total_items}): Network error while marking '{source_item['Name']}' as watched: {e}\033[00m")
        else:
            nok_count += 1
            print(f"\033[93mSKIP ({i+1}/{total_items}): Could not find matching item for '{source_item['Name']}' on destination server.\033[00m")

    print("\n\n\033[95m##### Sync Complete #####\033[00m")
    print(f"\033[92mSuccessfully synced: {ok_count}\033[00m")
    print(f"\033[91mFailed or skipped: {nok_count}\033[00m")


if __name__ == "__main__":
    CONFIG_PATH = "settings.ini"

    # Check if config file exists
    if not os.path.exists(CONFIG_PATH):
        createConfig(CONFIG_PATH)
        sys.exit()
        
    # Check if the username has been changed from the default
    if TARGET_USERNAME == "YOUR_JELLYFIN_USERNAME_HERE":
        print("\033[91mPlease edit the script and set the 'TARGET_USERNAME' variable.\033[00m")
        sys.exit()

    # --- SOURCE SERVER ---
    source_url = getConfig(CONFIG_PATH, 'Jellyfin_Source', 'URLBASE')
    source_api_key = getConfig(CONFIG_PATH, 'Jellyfin_Source', 'APIKEY')
    source_user_id = get_user_id(source_url, source_api_key, TARGET_USERNAME)
    if not source_user_id:
        print(f"\033[91mCould not find user '{TARGET_USERNAME}' on the SOURCE server. Exiting.\033[00m")
        sys.exit()
        
    migration_list = get_source_watched_status(source_url, source_api_key, source_user_id)
    if not migration_list:
        print("No watched items to migrate. Exiting.")
        sys.exit()
        
    # --- DESTINATION SERVER ---
    dest_url = getConfig(CONFIG_PATH, 'Jellyfin_Destination', 'URLBASE')
    dest_api_key = getConfig(CONFIG_PATH, 'Jellyfin_Destination', 'APIKEY')
    dest_user_id = get_user_id(dest_url, dest_api_key, TARGET_USERNAME)
    if not dest_user_id:
        print(f"\033[91mCould not find user '{TARGET_USERNAME}' on the DESTINATION server. Exiting.\033[00m")
        sys.exit()

    # --- RUN SYNC ---
    sync_to_destination(dest_url, dest_api_key, dest_user_id, migration_list)