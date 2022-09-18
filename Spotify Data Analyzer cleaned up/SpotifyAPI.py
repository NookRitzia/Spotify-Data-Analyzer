# written by eddy so long ago
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
class SpotifyAPI:
    def __init__(self, user_id, client_id, client_secret):
        self.user_id = user_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret))

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_data(self):
        return self.spotify.user(user=self.user_id)

    def get_playlists_raw(self, offset=0, limit=50):
        playlists = []

        if_hit_end = False


        #print(self.spotify.user_playlists(user=self.user_id, offset=offset)['items'])
        while (not self.spotify.user_playlists(user=self.user_id, offset=offset, limit=limit)['next'] == None) or (not if_hit_end):
            if self.spotify.user_playlists(user=self.user_id, offset=offset, limit=limit)['next'] == None:
                if_hit_end = True
            playlists.extend(self.spotify.user_playlists(user=self.user_id, offset=offset, limit=limit)['items'])
            offset += limit
        return playlists
        #return self.spotify.user_playlists(user=self.user_id, offset=offset)['items']

    #


    #




    def get_playlist_id(self, playlist, max_playlists=500):
        for i in range(max_playlists // 50):
            playlists = self.get_playlists_raw(offset=i*50)
            for p in playlists:
                if (p['name'] == playlist):
                    return p['id']

        return None

    def get_playlist_length(self, playlist):
        playlist_id = self.get_playlist_id(playlist)
        return self.spotify.playlist_items(playlist_id=playlist_id)['total']

    def get_playlist_length_by_id(self, id):
        return self.spotify.playlist_items(playlist_id=id)['total']
    def get_song_details_raw_by_name(self, playlist):
        playlist_id = self.get_playlist_id(playlist)
        total_songs = self.get_playlist_length(playlist)
        songs = []
        for i in range(total_songs // 100):
            clump = self.spotify.playlist_items(playlist_id=playlist_id, offset=100 * i)['items']
            for song in clump:
                songs.append(song)
        clump = self.spotify.playlist_items(playlist_id=playlist_id, offset=100 * (total_songs // 100))['items']

        for song in clump:
            songs.append(song)
        return songs

    def get_song_details_raw_by_id(self, id):
        total_songs = self.get_playlist_length_by_id(id)
        songs = []
        for i in range(total_songs // 100):
            clump = self.spotify.playlist_items(playlist_id=id, offset=100 * i)['items']
            for song in clump:
                songs.append(song)
        clump = self.spotify.playlist_items(playlist_id=id, offset= 100 * (total_songs // 100))['items']

        for song in clump:
            songs.append(song)
        return songs

    def get_playlist_songs(self, playlist_id):
        songs = self.get_song_details_raw_by_id(playlist_id)
        title = []
        for s in songs:
            try:
                title.append(s['track']['artists'][0]['name'] + ' - ' + s['track']['name'])
            except:
                pass
        return title
