#TEST TMDb CALL
import requests

url = "https://api.themoviedb.org/3/movie/top_rated"
params = {
    "api_key": "46cf6218239ae777cc7aab58edd1f34a",  # V3 KEY goes here
    "language": "en-US",
    "page": 1
}

response = requests.get(url, params=params)

print(response.status_code)
print(response.json())

#STRUCTURE DATA INTO A DATFRAME(CONVERTED RAW TMDb RESPONSE TO A CLEANED VERSION)
#DATA CLEANING PART
import pandas as pd

# Extract movie data
data = response.json()
movies = data['results']

# Select only useful fields
cleaned_movies = []
for movie in movies:
    cleaned_movies.append({
        'Title': movie['title'],
        'Overview': movie['overview'],
        'Rating': movie['vote_average'],
        'Release Date': movie['release_date'],
        'Poster URL': "https://image.tmdb.org/t/p/w500" + movie['poster_path'] if movie['poster_path'] else None
    })

# Create DataFrame
df = pd.DataFrame(cleaned_movies)
print(df.head())



