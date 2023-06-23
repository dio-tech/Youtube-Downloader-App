import requests

#refresh_token = "AQApf1T5eslAt6hFdHnUeK0mP1iYsANbe3SW7YMWGR157INTbM4Ij6yaFJOGce4PUXH2Mj3Btaimxwe0YM4PSb7tVHCl-pbZpd2WWnFqPmhO3yEETN4HkjlvpTCCJ5GKZvg"

import requests
import base64

def get_token():
    clientId = 'b4c4fa029cc94f97b2fe3c5fa7be13c3'
    clientSecret = 'ffc4e5accd434bfaac43129e78cc4994'

    # Step 1 - Authorization 
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}

    # Encode as Base64
    message = f"{clientId}:{clientSecret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')


    headers['Authorization'] = f"Basic {base64Message}"
    data['grant_type'] = "client_credentials"

    r = requests.post(url, headers=headers, data=data)

    token = r.json()['access_token']
    return token


def refresh():
    return get_token()


client_id = 'b4c4fa029cc94f97b2fe3c5fa7be13c3'
client_secret = 'ffc4e5accd434bfaac43129e78cc4994'
token = "Bearer " + str(refresh())


class Spotify:
    def __init__(self):
        self.headers = {"Authorization": token}

    def get_playlist(self, ident):
        # https://api.spotify.com/v1/users/{user_id}/playlists
        url = f"https://api.spotify.com/v1/users/{ident}/playlists"

        response = requests.get(url, headers=self.headers)
        return response.json()['items']

    def get_songs(self, id):
        songs = []
        url = f"https://api.spotify.com/v1/playlists/{id}/tracks"

        response = requests.get(url, headers=self.headers)
        for song in response.json()['items']:
            songs.append(song['track']['name'])
        
        return songs
    
    def check_user(self, ident):
        response = requests.get(f"https://api.spotify.com/v1/users/{str(ident)}", headers=self.headers)
        return response.status_code
    
    def get_playlist_name(self, ident):
        url = f"https://api.spotify.com/v1/playlists/{ident}"

        response = requests.get(url, headers=self.headers)
        return response.json()['name']


