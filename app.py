import pickle
import streamlit as st
import requests
import pandas as pd
import numpy as np
import joblib
import sys
import os

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
        movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def verify_file_size(file_path):
    """Verify if file exists and print its size"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        st.write(f"File {file_path} size: {size/1024/1024:.2f} MB")
        return True
    else:
        st.error(f"File {file_path} not found!")
        return False

def load_similarity_matrix(file_path):
    """Load similarity matrix with multiple attempts"""
    try:
        # First try: Direct joblib load
        return joblib.load(file_path)
    except Exception as e1:
        st.write(f"First attempt failed: {e1}")
        try:
            # Second try: Load as numpy array
            with open(file_path, 'rb') as f:
                return np.load(f, allow_pickle=True)
        except Exception as e2:
            st.write(f"Second attempt failed: {e2}")
            try:
                # Third try: Load with pickle
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e3:
                st.write(f"Third attempt failed: {e3}")
                return None

def load_data():
    try:
        st.write("Attempting to load files...")
        
        # Verify files exist and show their sizes
        movies_path = 'movie_list.pkl'
        similarity_path = 'similarity_compressed.pkl' if os.path.exists('similarity_compressed.pkl') else 'similarity.pkl'
        
        if not (verify_file_size(movies_path) and verify_file_size(similarity_path)):
            return None, None
        
        # Load movies data
        try:
            with open(movies_path, 'rb') as f:
                movies = pickle.load(f)
            st.success("Movies list loaded successfully!")
        except Exception as movies_error:
            st.error(f"Error loading movies data: {movies_error}")
            return None, None
        
        # Load similarity matrix
        st.write(f"Attempting to load similarity matrix from {similarity_path}")
        similarity = load_similarity_matrix(similarity_path)
        
        if similarity is None:
            st.error("Failed to load similarity matrix with all attempts")
            return None, None
        else:
            st.success("Similarity matrix loaded successfully!")

        # Convert to DataFrame if needed
        if isinstance(movies, dict):
            movies = pd.DataFrame(movies)
        elif not isinstance(movies, pd.DataFrame):
            movies = pd.DataFrame(movies)

        # Verify data
        st.write(f"Movies data type: {type(movies)}")
        st.write(f"Number of movies: {len(movies)}")
        st.write("Sample columns:", list(movies.columns)[:5])
        st.write(f"Similarity matrix shape: {similarity.shape}")
        st.write(f"Similarity matrix type: {type(similarity)}")

        return movies, similarity

    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.write("Python version:", sys.version)
        return None, None

def recommend(movie, movies, similarity):
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

# Main Streamlit app
st.header('Movie Recommender System')

# Load data
movies, similarity = load_data()

if movies is not None and similarity is not None:
    # Get movie list
    movie_list = movies['title'].tolist() if isinstance(movies, pd.DataFrame) else []
    
    if movie_list:
        selected_movie = st.selectbox(
            "Type or select a movie from the dropdown",
            movie_list
        )
        
        if st.button('Show Recommendation'):
            with st.spinner('Getting recommendations...'):
                recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)
                if recommended_movie_names and recommended_movie_posters:
                    cols = st.columns(5)
                    for idx, (col, name, poster) in enumerate(zip(cols, recommended_movie_names, recommended_movie_posters)):
                        with col:
                            st.text(name)
                            st.image(poster)
else:
    st.error("Failed to load movie data. Please check your pickle files.")
