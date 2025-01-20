import pickle
import streamlit as st
import requests
import pandas as pd

# Function to fetch movie poster
def fetch_poster(movie_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US")
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

# Function to recommend movies
def recommend(movie):
    try:
        # Find the index of the movie
        movie_index = movies[movies['title'] == movie].index[0]
        # Get similarity scores
        distances = sorted(list(enumerate(similarity[movie_index])), reverse=True, key=lambda x: x[1])
        
        recommended_movies = []
        recommended_posters = []
        
        # Get top 5 recommendations
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(movie_id))
            
        return recommended_movies, recommended_posters
    except Exception as e:
        st.error(f"Error getting recommendations: {e}")
        return [], []

# Set page config
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)

# Add title and styling
st.title("🎬 Movie Recommender System")
st.markdown("""
    <style>
    .stTitle {
        text-align: center;
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
try:
    # Load movie data
    with open('movie_list.pkl', 'rb') as f:
        movies_dict = pickle.load(f)
    movies = pd.DataFrame(movies_dict)
    
    # Load similarity matrix
    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)
        
    # Create selectbox for movie selection
    selected_movie = st.selectbox(
        "Select a movie you like:",
        movies['title'].values,
        index=None,
        placeholder="Choose a movie..."
    )
    
    # Center the button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button('Get Recommendations'):
            if selected_movie:
                with st.spinner('Finding recommendations...'):
                    names, posters = recommend(selected_movie)
                    
                    if names and posters:
                        # Display recommendations in 5 columns
                        cols = st.columns(5)
                        for i, (col, name, poster) in enumerate(zip(cols, names, posters)):
                            with col:
                                st.image(poster, use_column_width=True)
                                st.markdown(f"<h5 style='text-align: center;'>{name}</h5>", unsafe_allow_html=True)
            else:
                st.warning("Please select a movie first!")
                
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.write("Please ensure 'movie_list.pkl' and 'similarity.pkl' are in the same directory as this script.")

# Add footer
st.markdown("""
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        background-color: #f0f2f6;
    }
    </style>
    <div class="footer">
        Made with ❤️ by Your Name
    </div>
    """, unsafe_allow_html=True)
