#VISUALIZING THE DATA
import streamlit as st
import pandas as pd
import requests

# Get selected_movie_id from URL query params
query_params = st.experimental_get_query_params()
selected_movie_id = query_params.get("selected_movie_id", [None])[0]

# --- TMDB API Setup ---(STEP-1)
API_KEY = "46cf6218239ae777cc7aab58edd1f34a"
URL = "https://api.themoviedb.org/3/movie/top_rated"

# If user clicked a movie, fetch and show its detailed page
if selected_movie_id:
    detail_url = f"https://api.themoviedb.org/3/movie/{selected_movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }
    response = requests.get(detail_url, params=params)

    st.write("Selected movie ID:", selected_movie_id)
    if response.status_code == 200:
        movie = response.json()

        st.markdown(f"## 🎬 {movie['title']}")
        st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}")
        st.markdown(f"**Release Date:** {movie['release_date']}")
        st.markdown(f"**Rating:** {movie['vote_average']}/10")
        st.markdown(f"**Runtime:** {movie['runtime'] // 60} hr {movie['runtime'] % 60} min")
        genres = ", ".join([genre['name'] for genre in movie['genres']])
        st.markdown(f"**Genres:** {genres}")
        st.markdown(f"**Overview:** {movie['overview']}")

        # --- Get YouTube Trailer Link ---
        trailer_url = f"https://api.themoviedb.org/3/movie/{selected_movie_id}/videos"
        trailer_params = {
            "api_key": API_KEY,
            "language": "en-US"
        }
        trailer_response = requests.get(trailer_url, params=trailer_params)
        if trailer_response.status_code == 200:
            trailer_data = trailer_response.json()
            youtube_trailers = [video for video in trailer_data["results"] if video["site"] == "YouTube" and video["type"] == "Trailer"]
            if youtube_trailers:
                youtube_key = youtube_trailers[0]["key"]
                youtube_link = f"https://www.youtube.com/watch?v={youtube_key}"
                st.markdown(f"[▶️ Watch Trailer on YouTube]({youtube_link})")
            else:
                st.info("No YouTube trailer found.")
        else:
            st.warning("Failed to load trailer.")

    else:
        st.error("Failed to fetch movie details.")
    st.stop()  # ⛔ Stop further code execution (so the main page doesn't show)

# --- Get Genre List ---(STEP-5.1)
genre_url = "https://api.themoviedb.org/3/genre/movie/list"# This is another TMDb endpoint which return all genres and their IDs
genre_params = {
    "api_key": API_KEY,
    "language": "en-US"
}
genre_response = requests.get(genre_url, params=genre_params)# Makes the HTTP request to TMDb to fetch genre list
genre_data = genre_response.json()# Converts raw data into python dictionary 
genre_dict = {genre["name"]: genre["id"] for genre in genre_data["genres"]}# Maps genre names to its IDs

# --- Initialize session state for page ---(STEP-5)
# If no page is assigned initially session state just defaults it to page 1
if "page" not in st.session_state:
    st.session_state["page"] = 1

# --- Page Title ---
st.title(" 🎬 Top Rated Movies (TMDB)")

# --- Search Box ---(STEP-4)
st.markdown("""
    <h4 style='font-size:24px; font-weight:700; color:#4FC3F7;'>🔍 Search for a movie:</h4>
""", unsafe_allow_html=True)# This line is to make our title pop more to users 
search_query = st.text_input("", key="search_bar")#Saves the movie_name searched by the user into search_query

# --- Genre DropDown ---(STEP-5.1 contd)
# Deafault option is "All" which means no filter
genre_names = ["All"] + list(genre_dict.keys())# Give "All" genres if no filter selected otherwise gives a list of genre names 
selected_genre = st.selectbox("🎭 Filter by Genre", genre_names)# Adds a dropdown menu & Selects the genre given by the user, if no genre chosen give "All" genres

# --- Sorting DropDown ---(STEP-6)
sort_options = ["Top Rated", "Latest", "A-Z"]
selected_sort = st.selectbox("🔽 Sort By", sort_options)

# --- Handle pagination buttons ---(STEP-5 contd)
col1, col2, col3 = st.columns(3)
with col1:
    #It keeps the previous button at the leftmost column i.e. col1
    if st.button("⬅️ Previous") and st.session_state["page"] > 1:
        st.session_state["page"] -= 1
with col3:
    #keeps the next button at the rightmost column i.e. col3
    if st.button("Next ➡️"):
        st.session_state["page"] += 1
# Show current page number
st.markdown(f"<p style='text-align:center; font-weight:bold;'>Page {st.session_state['page']}</p>", unsafe_allow_html=True)

# --- API Call ---
if search_query:# (STEP-3 contd)if search_query has a value entered by the user it goes to /search/movie/query=(movie_name) to search the movie
    endpoint = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "query": search_query,# Only included if the user is searching for a movie.
        "page": st.session_state["page"]# This tells TMDB which page of results to return, session_state keeps track on which page user is on
        # Do not apply genre filter here because search endpoint doesn't support 'with_genres'
    }
elif selected_genre != "All": # (STEP-5.2)If user selects a specific genre and is not searching
    endpoint = "https://api.themoviedb.org/3/discover/movie"  # Use discover endpoint for genre filtering
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "page": st.session_state["page"],
        "with_genres": genre_dict[selected_genre]# Tells the TMDB API which genre of movies you want to fetch.
    }
else:# (STEP-3 contd)If the search_query is empty and genre is "All" we fall back to our first page /movie/top_rated
    endpoint = "https://api.themoviedb.org/3/movie/top_rated"
    params = {
        "api_key": API_KEY,
        "language": "en-US", 
        "page": st.session_state["page"]
    }

# --- Fetch Data ---
response = requests.get(endpoint, params=params)
data = response.json()
movies = data['results']

# --- Clean & Structure ---(STEP-2)
cleaned_movies = []
for movie in movies:
    cleaned_movies.append({
        'Title': movie['title'],
        'Overview': movie['overview'],
        'Rating': movie['vote_average'],
        'Release Date': movie['release_date'],
        'Poster URL': "https://image.tmdb.org/t/p/w500" + movie['poster_path'] if movie['poster_path'] else None
    })
df = pd.DataFrame(cleaned_movies)

# --- Apply Sorting ---(STEP-6 contd)
if selected_sort == "A-Z":
    df = df.sort_values("Title")# Sort movies in alphabetical order
elif selected_sort == "Latest":
    df = df.sort_values("Release Date", ascending = False)# Sort movies according to the release date
# "Top Rated" is already handled by the API, so no need to sort manually

# --- Display Cards ---(STEP-3)
# Displayed movies in Netflix-style 3-card layout.
for i in range(0, len(df), 3):  # Show 3 cards per row
    cols = st.columns(3) # Creates 3 side by side
    for j in range(3):
        if i + j < len(df):
            movie = df.iloc[i + j]
            with cols[j]:
                st.image(movie['Poster URL'], use_container_width=True)
                st.markdown(f"### {movie['Title']}")
                st.markdown(f"**⭐ Rating:** {movie['Rating']}")
                st.markdown(f"**📅 Release Date:** {movie['Release Date']}")
                st.markdown(f"_{movie['Overview'][:200]}..._")
                movie_id = movies[i + j]['id']
                movie_url = f"?selected_movie_id={movie_id}"
                st.markdown(f"[🔍 View More](/{movie_url})", unsafe_allow_html=True)