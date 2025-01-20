import pickle
import streamlit as st
import requests
import pandas as pd
import numpy as np

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
        movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

# First, let's properly load and save the files in a compatible format
def save_compressed_files():
    try:
        # Load and save movies data
        with open('movie_list.pkl', 'rb') as f:
            movies_data = pickle.load(f)
        with open('movie_list_new.pkl', 'wb') as f:
            pickle.dump(movies_data, f, protocol=4)
            
        

# Now load the data
try:
    # Load movies data
    with open('movie_list.pkl', 'rb') as f:
        movies = pickle.load(f)
    
    # Load similarity matrix
    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)

    # Convert to DataFrame if it's a dictionary
    if isinstance(movies, dict):
        movies = pd.DataFrame(movies)

    print("Type of movies:", type(movies))
    print("Movies columns:", movies.columns if isinstance(movies, pd.DataFrame) else "Not a DataFrame")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)
        return recommended_movie_names, recommended_movie_posters
    except Exception as e:
        st.error(f"Error in recommendation: {e}")
        return [], []

st.header('Movie Recommender System')

# Get movie list based on data type
if isinstance(movies, pd.DataFrame):
    movie_list = movies['title'].tolist()
else:
    movie_list = movies['title'] if isinstance(movies, dict) else []

selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    with st.spinner('Getting recommendations...'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
        if recommended_movie_names and recommended_movie_posters:
            cols = st.columns(5)
            for idx, (col, name, poster) in enumerate(zip(cols, recommended_movie_names, recommended_movie_posters)):
                with col:
                    st.text(name)
                    st.image(poster)
