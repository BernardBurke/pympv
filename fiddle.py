import requests
import os
import json
server_url = 'http://127.0.0.1:8096'

api_key = os.environ.get('JELLYFIN_API_KEY')

# a general purpose logger for json that only logs output when the environment variable DEBUG is set to True
def log_json(data, message=">"):
    if os.environ.get('DEBUG') == 'True':
        print(message)
        print(json.dumps(data, indent=4))


headers = {
    'Authorization': 'MediaBrowser Client="other", Device="my-script", DeviceId="some-unique-id", Version="0.0.0"'
}

try:
    if api_key:
        # API Key Authentication
        headers['X-Emby-Authorization'] = f'MediaBrowser Client="other", Device="my-script", DeviceId="some-unique-id", Version="0.0.0", Token="{api_key}"'
        r = requests.get(server_url + '/Users', headers=headers) 
        UserID = r.json()[0]['Id']
    else:
        # ... (Username/Password Authentication - handle later) ...
        pass

    r.raise_for_status()  # Raise an exception for bad status codes
    log_json("Status Code:", r.status_code)  # Print status code
    log_json("Response Headers:", r.headers)  # Print headers
    log_json("Response Text:", r.text)  # Print raw response

    # Skip getting user_id from this response (not available)


except requests.exceptions.RequestException as e:
    print(f"Error: {e}")


print(f"UserID: {UserID} now walking the path of the media folder")

# Example API call to get server info
r = requests.get(server_url + '/Library/MediaFolders', headers=headers)
r.raise_for_status()
log_json(r.json())

collections = r.json()['Items']

for collection in collections:
    print(f"CollectionType: {collection['CollectionType']}")
    #when the collection type is "shows" call walk_shows function passing the collection['Id']. When the collection type is "movies" call walk_movies function passing the collection['Id']
    if collection['CollectionType'] == "shows":
        print("Walking shows")
    elif collection['CollectionType'] == "movies":
        print("Walking movies")
    else:
        print("Unknown CollectionType")

# each folder has an CollectionType, Path, and Id. Print out CollectionType and Path and Id
#for folder in r.json("Item"):
#    print(f"CollectionType: {folder['CollectionType']}, Path: {folder['Path']}, Id: {folder['Id']}")