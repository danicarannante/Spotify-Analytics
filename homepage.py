import streamlit as st
import requests
import base64
import urllib.parse
from config import CLIENT_ID, CLIENT_SECRET

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
            return tokens['access_token'], tokens['refresh_token']
        else:
            st.error('Failed to get access token.')
            return None, None

    def refresh_access_token(self, refresh_token):
        url = 'https://accounts.spotify.com/api/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        headers = self.get_auth_headers()
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            tokens = response.json()
            return tokens['access_token']
        else:
            st.error('Failed to refresh access token.')
            return None

    def get_api_headers(self, access_token):
        headers = {'Authorization': f'Bearer {access_token}'}
        return headers

    def fetch_user_profile(self, access_token):
        headers = self.get_api_headers(access_token)
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error('Failed to fetch user profile.')
            return None

    
    def get_top_tracks(self, access_token):
        headers = self.get_api_headers(access_token)
        response = requests.get('https://api.spotify.com/v1/me/top/tracks', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error('Failed to get top tracks.')
            return None

    def run(self):
        st.title('Spotify Auth with Streamlit')

        if st.button('Login with Spotify'):
            scope = 'user-read-private user-read-email'
            auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode({
                'response_type': 'code',
                'client_id': self.client_id,
                'scope': scope,
                'redirect_uri': self.redirect_uri,
            })
            st.markdown(f'[Login to Spotify]({auth_url})')

        query_params = st.query_params
        code = query_params.get('code')

        if code:
            access_token, refresh_token = self.get_access_token(code)
            if access_token and refresh_token:

                profile_data = self.fetch_user_profile(access_token)
                if profile_data:
                    print("success")
                    st.write('User profile:', profile_data)

                top = self.get_top_tracks(access_token)
                if top:
                    print("retrieving top tracks..........")
                    st.write(top)
                

                st.session_state.access_token = access_token
                st.session_state.refresh_token = refresh_token

                st.success('Authentication successful!')

        if 'access_token' in st.session_state:
            if st.button('Refresh Token'):
                refresh_token = st.session_state.refresh_token
                access_token = self.refresh_access_token(refresh_token)
                if access_token:
                    st.session_state.access_token = access_token
                    st.success('Token refreshed successfully!')

if __name__ == '__main__':
    SpotifyApp()


