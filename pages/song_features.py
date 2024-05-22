import streamlit as st 
from spotify_client import *
from config import CLIENT_ID,CLIENT_SECRET
import pandas as pd
import altair as alt


client_id = CLIENT_ID
client_secret = CLIENT_SECRET


Types_of_Features = ("acousticness", "danceability", "energy", "instrumentalness", "liveness", "loudness", "speechiness", "tempo", "valence")

st.title("Spotify Features App")
Name_of_Artist = st.sidebar.text_input("Artist Name")
Name_of_Feat = st.sidebar.selectbox("Feature", Types_of_Features)
button_clicked = st.sidebar.button("OK")


spotify = SpotifyAPI(client_id, client_secret)

Data = spotify.search({"artist": f"{Name_of_Artist}"}, search_type="track")

need = []
for i, item in enumerate(Data['tracks']['items']):
    track = item['album']
    track_id = item['id']
    song_name = item['name']
    popularity = item['popularity']
    need.append((i, track['artists'][0]['name'], track['name'], track_id, song_name, track['release_date'], popularity))
 
track_df = pd.DataFrame(need, index=None, columns=('Item', 'Artist', 'Album Name', 'Id', 'Song Name', 'Release Date', 'Popularity'))

access_token = spotify.access_token

headers = {
    "Authorization": f"Bearer {access_token}"
}

endpoint = "https://api.spotify.com/v1/audio-features/"

f_dfs = []
for track_id in track_df['Id']:
    lookup_url = f"{endpoint}{track_id}"
    ra = requests.get(lookup_url, headers=headers)
    audio_feat = ra.json()
    f_temp_df = pd.DataFrame(audio_feat, index=[0])
    f_dfs.append(f_temp_df)
feature_df = pd.concat(f_dfs, ignore_index=True)


full_data = track_df.merge(feature_df, left_on="Id", right_on="id")
#st.write(full_data)

sort_df = full_data.sort_values(by=['Popularity'], ascending=False)
chart_df = sort_df[['Artist', 'Album Name', 'Song Name', 'Release Date', 'Popularity', f'{Name_of_Feat}']]

# Streamlit Chart
feat_header = Name_of_Feat.capitalize()

st.header(f'{feat_header}' " vs. Popularity")
c = alt.Chart(chart_df).mark_circle().encode(
    alt.X('Popularity', scale=alt.Scale(zero=False)), y=f'{Name_of_Feat}', color=alt.Color('Popularity', scale=alt.Scale(zero=False)), 
    size=alt.value(200), tooltip=['Popularity', f'{Name_of_Feat}', 'Song Name', 'Album Name'])

st.altair_chart(c, use_container_width=True)

st.header("Table of Attributes")
st.table(chart_df)


# st.write("Information about features is from:  https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/")