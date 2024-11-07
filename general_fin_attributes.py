import requests
import os

server_url = 'http://127.0.0.1:8096'
api_key = os.environ.get('JELLYFIN_API_KEY')

headers = {
    'Authorization': f'MediaBrowser Client="other", Device="my-script", DeviceId="some-unique-id", Version="0.0.0", Token="{api_key}"'
}

def get_collection_attributes(collection_type):
    try:
        # Get all collections
        r = requests.get(server_url + '/Collections', headers=headers)
        r.raise_for_status()
        collections = r.json()['Items']  # Access the 'Items' list directly

        # Find the collection with the matching CollectionType
        for collection in collections:
            if collection.get('CollectionType') == collection_type:
                return {
                    'Name': collection.get('Name'),
                    'Id': collection.get('Id'),
                    'Path': collection.get('Path')
                }

        return None  # Collection not found

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Example usage:
movies_attributes = get_collection_attributes('movies')
if movies_attributes:
    print("Movies attributes:", movies_attributes)

tvshows_attributes = get_collection_attributes('tvshows')
if tvshows_attributes:
    print("TV Shows attributes:", tvshows_attributes)