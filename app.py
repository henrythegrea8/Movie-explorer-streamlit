import requests
import pandas as pd
import streamlit as st

# --- API CONFIG ---
API_KEY = "b7e45a4161d65f0fd60bfd9566f176a7"
BASE_URL = "https://api.themoviedb.org/3"

# --- FETCH TRENDING MOVIES ---
def fetch_trending_movies():
    url = f"{BASE_URL}/trending/movie/day?api_key={API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["results"]
        df = pd.DataFrame(data)[["id", "title", "release_date", "vote_average", "overview", "poster_path"]]
        df["poster_url"] = "https://image.tmdb.org/t/p/w500" + df["poster_path"].astype(str)
        return df
    else:
        return pd.DataFrame()

# --- SEARCH MOVIE ---
def search_movie(query):
    url = f"{BASE_URL}/search/movie?api_key={API_KEY}&language=en-US&query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["results"]
        if data:
            df = pd.DataFrame(data)[["id", "title", "release_date", "vote_average", "overview", "poster_path"]]
            df["poster_url"] = "https://image.tmdb.org/t/p/w500" + df["poster_path"].astype(str)
            return df
        else:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

# --- FETCH WATCH PROVIDERS ---
def fetch_watch_providers(movie_id, region="US"):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        providers = response.json().get("results", {})
        if region in providers:
            return providers[region]
        else:
            return None
    else:
        return None

# --- FETCH GENRES ---
def fetch_genres():
    url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["genres"]
    else:
        return []

# --- FETCH MOVIES BY GENRE ---
def fetch_movies_by_genre(genre_id):
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={genre_id}&sort_by=popularity.desc"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["results"][:5]  # only top 5
        df = pd.DataFrame(data)[["id", "title", "release_date", "vote_average", "overview", "poster_path"]]
        df["poster_url"] = "https://image.tmdb.org/t/p/w500" + df["poster_path"].astype(str)
        return df
    else:
        return pd.DataFrame()

# --- STREAMLIT UI ---
st.title("🎬 Movie Explorer")
st.write("Discover Trending Movies, Search Globally, or Explore by Genre!")

# Sidebar navigation
menu = st.sidebar.radio("📌 Choose an option:", ["🔥 Trending", "🔍 Search", "🎭 Genres"])

# --- TRENDING ---
if menu == "🔥 Trending":
    st.header("Today's Trending Movies")
    movies_df = fetch_trending_movies()
    if not movies_df.empty:
        for _, row in movies_df.iterrows():
            st.subheader(row["title"])
            st.image(row["poster_url"])
            st.write(f"Release Date: {row['release_date']}")
            st.write(f"Rating: {row['vote_average']}")
            st.write(row["overview"])

            # Streaming providers
            providers = fetch_watch_providers(row["id"])
            if providers:
                st.markdown(f"**Available here:** [Watch Link]({providers['link']})")
            else:
                st.write("No streaming info available.")
            st.markdown("---")

# --- SEARCH ---
elif menu == "🔍 Search":
    search_query = st.text_input("Enter a movie name:")
    if search_query:
        search_results = search_movie(search_query)
        if not search_results.empty:
            for _, row in search_results.iterrows():
                st.subheader(row["title"])
                st.image(row["poster_url"])
                st.write(f"Release Date: {row['release_date']}")
                st.write(f"Rating: {row['vote_average']}")
                st.write(row["overview"])

                # Streaming providers
                providers = fetch_watch_providers(row["id"])
                if providers:
                    st.markdown(f"**Available here:** [Watch Link]({providers['link']})")
                else:
                    st.write("No streaming info available.")
                st.markdown("---")
        else:
            st.warning("No results found.")

# --- GENRES ---
elif menu == "🎭 Genres":
    st.header("Explore by Genre")
    genres = fetch_genres()
    genre_dict = {g["name"]: g["id"] for g in genres}
    selected_genre = st.selectbox("Select a Genre:", list(genre_dict.keys()))
    
    if selected_genre:
        st.subheader(f"Top 5 in {selected_genre}")
        genre_movies = fetch_movies_by_genre(genre_dict[selected_genre])
        if not genre_movies.empty:
            for _, row in genre_movies.iterrows():
                st.subheader(row["title"])
                st.image(row["poster_url"])
                st.write(f"Release Date: {row['release_date']}")
                st.write(f"Rating: {row['vote_average']}")
                st.write(row["overview"])

                # Streaming providers
                providers = fetch_watch_providers(row["id"])
                if providers:
                    st.markdown(f"**Available here:** [Watch Link]({providers['link']})")
                else:
                    st.write("No streaming info available.")
                st.markdown("---")
