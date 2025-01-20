import pickle
import streamlit as st
import requests
import pandas as pd
import numpy as np
import os

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
        movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

# Modified loading function with error handling and debugging
def load_data():
    try:
        # Check if files exist
        if not os.path.exists('movie_list.pkl') or not os.path.exists('similarity.pkl'):
            st.error("Required data files are missing. Please ensure movie_list.pkl and similarity.pkl are in the same directory as the script.")
            return None, None

        # Load movies with protocol handling
        movies = None
        similarity = None
        
        # Try different pickle protocols
        for protocol in range(5):  # Python supports protocols 0-4
            try:
                with open('movie_list.pkl', 'rb') as f:
                    movies = pickle.load(f)
                break
            except Exception as e:
                continue

        for protocol in range(5):
            try:
                with open('similarity.pkl', 'rb') as f:
                    similarity = pickle.load(f)
                break
            except Exception as e:
                continue

        if movies is None or similarity is None:
            st.error("Could not load data files. Please ensure they are properly formatted.")
            return None, None

        # Convert to DataFrame if needed
        if isinstance(movies, dict):
            movies = pd.DataFrame(movies)
        
        # Verify data structure
        if not isinstance(movies, pd.DataFrame):
            st.error("Invalid movie data format")
            return None, None
            
        if not isinstance(similarity, np.ndarray):
            st.error("Invalid similarity data format")
            return None, None

        # Verify required columns
        required_columns = ['title', 'movie_id']
        if not all(col in movies.columns for col in required_columns):
            st.error(f"Missing required columns in movie data. Required: {required_columns}")
            return None, None

        return movies, similarity

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def recommend(movie, movies, similarity):
    if movies is None or similarity is None:
        return [], []
        
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
        st.error(f"Error generating recommendations: {str(e)}")
        return [], []

# Main Streamlit app
st.header('Movie Recommender System')

# Load data
movies, similarity = load_data()

if movies is not None and similarity is not None:
    movie_list = movies['title'].tolist()
    
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list
    )

    if st.button('Show Recommendation'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)
        if recommended_movie_names and recommended_movie_posters:
            cols = st.columns(5)
            for idx, (col, name, poster) in enumerate(zip(cols, recommended_movie_names, recommended_movie_posters)):
                with col:
                    st.text(name)
                    st.image(poster)
