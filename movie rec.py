import pickle
import streamlit as st
import requests
import time

def fetch_poster(movie_id):
    # Add retry mechanism
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
            data = requests.get(url, timeout=10)  # Add timeout
            data = data.json()
            poster_path = data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < max_retries - 1:
                st.warning(f"Connection error, retrying in {retry_delay} seconds... (Attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                # Increase delay for next retry
                retry_delay *= 2
            else:
                st.error(f"Failed to fetch poster after {max_retries} attempts: {str(e)}")
                # Return a placeholder image URL instead of failing
                return "https://via.placeholder.com/500x750?text=No+Poster+Available"
        except Exception as e:
            st.error(f"Error fetching poster: {str(e)}")
            return "https://via.placeholder.com/500x750?text=No+Poster+Available"

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []
        
        for i in distances[1:6]:
            # fetch the movie poster
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)
            
        return recommended_movie_names, recommended_movie_posters
    except Exception as e:
        st.error(f"Error in recommendation: {str(e)}")
        # Return empty lists in case of error
        return [], []

st.header('Movie Recommender System')

# Load data with error handling
try:
    movies = pickle.load(open('movie_list.pkl','rb'))
    similarity = pickle.load(open('similarity.pkl','rb'))
    
    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list
    )
    
    if st.button('Show Recommendation'):
        with st.spinner('Getting recommendations...'):
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
            
            if recommended_movie_names and recommended_movie_posters:
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.text(recommended_movie_names[0])
                    st.image(recommended_movie_posters[0])
                with col2:
                    st.text(recommended_movie_names[1])
                    st.image(recommended_movie_posters[1])
                with col3:
                    st.text(recommended_movie_names[2])
                    st.image(recommended_movie_posters[2])
                with col4:
                    st.text(recommended_movie_names[3])
                    st.image(recommended_movie_posters[3])
                with col5:
                    st.text(recommended_movie_names[4])
                    st.image(recommended_movie_posters[4])
            else:
                st.error("Couldn't generate recommendations. Please try another movie.")
except Exception as e:
    st.error(f"Failed to load necessary data: {str(e)}")
    st.info("Please ensure movie_list.pkl and similarity.pkl files are in the same directory as your app.")
