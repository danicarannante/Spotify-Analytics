import streamlit as st
import requests
import base64
import urllib.parse
from config import CLIENT_ID, CLIENT_SECRET
import webbrowser
import datetime
import time

class SpotifyApp:
    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.redirect_uri = 'http://localhost:8501'
        self.state_key = 'spotify_auth_state'
        self.run()


    def get_auth_headers(self):
        auth_header = base64.b64encode((self.client_id + ':' + self.client_secret).encode()).decode()
        headers = {
            'Authorization': 'Basic ' + auth_header,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        return headers

    def get_access_token(self, code):
        url = 'https://accounts.spotify.com/api/token'
        data = {
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        headers = self.get_auth_headers()
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            st.session_state.access_token = tokens['access_token']
            st.session_state['expires'] = tokens['expires_in']
            st.success("successfully logged in")
            return tokens['access_token']
            
        else:
            st.error(response.status_code)
            st.error('Failed to get access token.')
            return None

    def get_api_headers(self, access_token): # resource header
        headers = {'Authorization': f'Bearer {access_token}'}
        return headers

    def get_user_profile(self, access_token):
        headers = self.get_api_headers(access_token)
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error('Failed to fetch user profile.')
            st.error(response.status_code)
        return None

    def get_tracks(self,artist_id):
        response = requests.get('https://api.spotify.com/v1/artists/{artist_id}/top-tracks')
        if response.status_code != 200:
            st.error('Failed to get top tracks.')
            return
        tracks = response.json()['items']
        st.write(tracks)
        return


    
    def get_top_tracks(self, access_token):
        headers = self.get_api_headers(access_token)
        response = requests.get('https://api.spotify.com/v1/me/top/tracks', headers=headers)
        if response.status_code != 200:
            st.error('Failed to get top tracks.')
            return
        tracks = response.json()['items']
        #st.write(response.json())
        st.write("TOP 5 SONGS:")
        for index, item in enumerate(tracks[:5]):
            st.write(f'{index + 1}. {item["name"]} by {item["artists"][0]["name"]}')
        return tracks     
            
    def get_top_artists(self, access_token):
        headers = self.get_api_headers(access_token)
        response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers)
        if response.status_code != 200:
            st.error('Failed to get top artists.')
            return
        artists = response.json()['items']
        st.write("TOP 5 ARTISTS:")
        for index, item in enumerate(artists[:5]):
            st.write(f'{index + 1}. {item["name"]}')
            #st.write(f'ARTIST ID : {item["id"]}')
            #st.button(f'View top tracks for {item["name"]}', on_click = self.get_tracks(item['id']))

        return artists

            
    def login(self):
        scope = 'user-read-private user-read-email user-top-read user-follow-read'
        auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode({
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': scope,
            'redirect_uri': self.redirect_uri,
        })

        if st.session_state.login == True:
            st.sidebar.write(f"[Click here to authenticate with Spotify]({auth_url})")
        query_params = st.query_params
        code = query_params.get('code')
        if code:
            access_token= self.get_access_token(code)
            if access_token:
                st.session_state.access_token = access_token
                st.success('Authentication successful!')
                st.sidebar.write('Logged In')
                return 1 # success
            else:
                st.error('Authentication Failed')
        return 0 # failure


    def run(self):
        st.title('Spotify Analytics Dashboard')
        if 'login' not in st.session_state:
            st.session_state.login = True
            self.login()
        elif st.session_state.login == False:
            st.session_state.login = True
            self.login()

        #profile = self.get_user_profile(st.session_state.access_token)
    
        top_tracks_button = st.sidebar.button('Get Top Tracks')
        if top_tracks_button:
            self.get_top_tracks(st.session_state.access_token)

            
        top_artists_button = st.sidebar.button('Get Top Artists')
        if top_artists_button:
            self.get_top_artists(st.session_state.access_token)






if __name__ == '__main__':
    SpotifyApp()
