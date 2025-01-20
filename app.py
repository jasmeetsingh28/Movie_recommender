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

# Modified loading function with error handling
def load_data():
    try:
        # Try loading with different pickle protocols
        for encoding in ['ascii', 'bytes', 'latin1']:
            try:
                # Load movies data
                with open('movie_list.pkl', 'rb') as f:
                    movies = pickle.load(f, encoding=encoding)
                
                # Load similarity matrix
                with open('similarity.pkl', 'rb') as f:
                    similarity = pickle.load(f, encoding=encoding)
                
                # Convert to DataFrame if needed
                if isinstance(movies, dict):
                    movies = pd.DataFrame(movies)
                
                return movies, similarity
            except Exception as e:
                continue
        
        raise Exception("Could not load data with any encoding")
    except Exception as e:
        st.error(f"Error loading data: {e}")
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
