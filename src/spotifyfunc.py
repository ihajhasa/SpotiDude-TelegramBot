import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

redirect_uri = 'http://localhost:8888/callback/'

def create_auth(username, client_id, client_secret):
    scope = "playlist-modify-public"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(username=username,
                                                   client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri='http://localhost:8888/callback/',
                                                   scope=scope))

    return sp


def add_song_to_playlist(sp, username, playlist_id, song_id):
    sp.user_playlist_add_tracks(username, playlist_id, song_id)
    return

def create_playlist(sp, playlist_name):
    user_id = sp.me()['id']

    return sp.user_playlist_create(user_id, playlist_name)