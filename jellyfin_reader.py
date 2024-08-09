import requests
import os
from collections import defaultdict

def get_env_var_or_raise(var_name):
    """Gets an environment variable or raises an error if it's not set."""
    value = os.environ.get(var_name)
    if not value:
        raise ValueError(f"Environment variable '{var_name}' is not set. Please configure it.")
    return value

# Jellyfin API Configuration from Environment Variables
API_KEY = get_env_var_or_raise("JELLYFIN_API_KEY")
BASE_URL = get_env_var_or_raise("JELLYFIN_BASE_URL")

# ... (rest of the code, including the filter function, remains the same) ...

def filter_movies_with_multiple_paths(movies):
    """Filters movies that have more than one unique path."""
    movies.sort(key=lambda movie: movie.get('Name'))
    path_counts = defaultdict(int)
    for movie in movies:
        #print(f"processing movie: {movie.get('Name')} with path: {movie.get('Path')}")
        path = movie.get('Path')
        if path:
            path_counts[path] += 1

    filtered_movies = [movie for movie in movies if path_counts[movie.get('Path')] > 1]
    return filtered_movies

# Example: Get a list of all movies with full path and filter
endpoint = "/Items"
params = {
    "api_key": API_KEY,
    "IncludeItemTypes": "Movie",
    "Recursive": "true",
    "Fields": "Path"
}

response = requests.get(BASE_URL + endpoint, params=params)

if response.status_code == 200:
    all_movies = response.json()["Items"]
    movies_with_multiple_paths = filter_movies_with_multiple_paths(all_movies)

    for movie in movies_with_multiple_paths:
        print(f"Title: {movie['Name']}, Year: {movie.get('ProductionYear')}, Path: {movie.get('Path')}")
else:
    print(f"Error fetching data: {response.status_code}")