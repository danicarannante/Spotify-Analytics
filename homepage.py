import streamlit as st
import requests
import random
import string
import base64
import urllib.parse
from config import CLIENT_ID, CLIENT_SECRET

# Spotify API credentials
client_id = CLIENT_ID
client_secret = CLIENT_SECRET
redirect_uri = 'https://localhost:8501/callback'  # Your redirect uri

# Generate a random state string
def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

state_key = 'spotify_auth_state'

def main():
    st.title('Spotify Auth with Streamlit')

    if 'state' not in st.session_state:
        st.session_state.state = generate_random_string(16)

    # Login button
    if st.button('Login with Spotify'):
        state = st.session_state.state
        scope = 'user-read-private user-read-email'
        auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode({
            'response_type': 'code',
            'client_id': client_id,
            'scope': scope,
            'redirect_uri': redirect_uri,
            'state': state
        })
        st.markdown(f'[Login to Spotify]({auth_url})')

    # Callback handling
    query_params = st.query_params
    code = query_params.get('code')
    state = query_params.get('state')

    if code and state:
        if state != st.session_state.state:
            st.error('State mismatch. Please try again.')
        else:
            auth_options = {
                'url': 'https://accounts.spotify.com/api/token',
                'data': {
                    'code': code,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code'
                },
                'headers': {
                    'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode()).decode(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            }

            response = requests.post(auth_options['url'], data=auth_options['data'], headers=auth_options['headers'])
            if response.status_code == 200:
                tokens = response.json()
                access_token = tokens['access_token']
                refresh_token = tokens['refresh_token']

                # Get user profile
                headers = {'Authorization': f'Bearer {access_token}'}
                profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
                profile_data = profile_response.json()
                st.write('User profile:', profile_data)

                # Store tokens in session state for later use
                st.session_state.access_token = access_token
                st.session_state.refresh_token = refresh_token

                st.success('Authentication successful!')

    # Refresh token
    if 'access_token' in st.session_state:
        if st.button('Refresh Token'):
            refresh_token = st.session_state.refresh_token
            refresh_options = {
                'url': 'https://accounts.spotify.com/api/token',
                'data': {
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                },
                'headers': {
                    'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode()).decode(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            }

            refresh_response = requests.post(refresh_options['url'], data=refresh_options['data'], headers=refresh_options['headers'])
            if refresh_response.status_code == 200:
                tokens = refresh_response.json()
                st.session_state.access_token = tokens['access_token']
                st.success('Token refreshed successfully!')

if __name__ == '__main__':
    main()
