import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from SpotifyAPI import *
import os
class SpotifyAnalyzer:


    def __init__(self, spotify_account_link, client_id, client_secret):
        self.user_id = self.spotify_link_to_account_id(spotify_account_link)
        self.client_id = client_id
        self.client_secret = client_secret
        self.spotify = SpotifyAPI(self.user_id, self.client_id, self.client_secret)

    def spotify_link_to_account_id(self, spotify_link):
        try:
            end_index = spotify_link.rindex("?")
        except ValueError as e:
            try:
                return spotify_link[spotify_link.rindex("/") + 1:]
            except Exception as e1:
                print(e1)
        return spotify_link[spotify_link.rindex("/") + 1:spotify_link.rindex("?")]

    def analyzation_dump(self, folder_path, folder_name=""):
        if folder_name == "":
            folder_name = self.sanitize_text(self.get_display_name() + " Data")

        self.create_folders(folder_path, folder_name)
        print("Folders Created.")
        self.playlist_song_dump(folder_path + folder_name + "/Playlist Dump/")
        print("Playlist Dump Created.")
        self.compile_songs(folder_path + folder_name + "/")
        print("Songs Compiled.")
        self.compile_unique_songs(folder_path + folder_name + "/")
        print("Unique Songs Compiled.")
        self.compile_unique_songs_occurrences(folder_path + folder_name + "/")
        print("Unique Song Occurences Compiled.")
        print("Done!")


        self.compile_user_data(folder_path + folder_name + "/")
        print("Done!")

    def create_folders(self, folder_path, folder_name):
        #creates the folders to store all the information
        try:
            folder_path = folder_path + folder_name
            os.mkdir(folder_path)

            os.mkdir(folder_path + "/Data")
            os.mkdir(folder_path + "/Playlist Dump")
        except FileExistsError:
            print("Directory \"" + folder_path + "\" already exists. Remove it or change the folder path to continue.")

    def playlist_song_dump(self, folder_path):
        # get all playlists' data
        playlists_raw = self.spotify.get_playlists_raw()
        errors = 1
        for playlist_raw in playlists_raw:
            playlist = self.spotify.get_playlist_songs(playlist_raw['id'])
            try:
                link = "" + folder_path + self.sanitize_text(playlist_raw['name']) + ".txt"
                txt_file = open(link,'w')
            except Exception as e:
                txt_file = open("" + folder_path + playlist_raw['id'] + ".txt",'w')
                print(e)
            except Exception as e1:
                txt_file = open("" + folder_path + "ERROR PLAYLIST" + str(errors) + ".txt",'w')
                print(e1)

            for song in playlist:
                try:
                    txt_file.write(song + "\n")
                except Exception as e:
                    print(e)
            txt_file.close()

    def compile_songs(self, folder_path):
        all_songs_compiled_file = open(folder_path + "Data/All Songs Compiled.txt", "w")
        directory_list = os.listdir(folder_path + "Playlist Dump")
        for directory in directory_list:
            if os.path.isfile(folder_path + "Playlist Dump/" + directory):
                file_being_read = open(folder_path + "Playlist Dump/" + directory)
                all_songs_compiled_file.write(file_being_read.read())

        all_songs_compiled_file.close()

    def compile_unique_songs(self, folder_path):
        temp_songs = open(folder_path + "Data/All Songs Compiled.txt","r")
        songs = temp_songs.read().split("\n")
        temp_songs.close()
        unique_songs_file = open(folder_path + "Data/Unique Songs List.txt", "w")
        unique_songs = []

        for song in songs:
            if not self.if_song_exists(song, unique_songs):
                unique_songs.append(song)

        for song in unique_songs:
            unique_songs_file.write(song + "\n")

        unique_songs_file.close()

    def compile_unique_songs_occurrences(self, folder_path):
        temp_unique = open(folder_path + "Data/Unique Songs List.txt", "r")
        unique_songs = temp_unique.read().split("\n")
        temp_unique.close()

        ordered_occurrences_list_file = open(folder_path + "Data/Song Occurrences List.txt", "w")

        temp_all_songs = open(folder_path + "Data/All Songs Compiled.txt","r")
        all_songs_compiled = temp_all_songs.read().split("\n")
        temp_all_songs.close()

        # in the form [ [occurrence, song name] ] example -> [ [5, two feet lies] , [3, two feet maria] ]
        ordered_list = []
        for song in unique_songs:
            ordered_list.append([self.song_occurrences(song, all_songs_compiled), song])
        ordered_list.pop(0)

        # bubble sort algorithm (i know its garbage)
        # okay i optimized it because it took like 8 minutes to get to the end of 1 sort
        # and then i got an error because i didnt cast to a str
        # simple optimization made it take like 5 seconds

        i = 0
        if_swapped = False
        while i < len(ordered_list) - 1:
            if ordered_list[i][0] > ordered_list[i + 1][0]:
                if_swapped = True
                temp = ordered_list[i]
                ordered_list[i] = ordered_list[i + 1]
                ordered_list[i + 1] = temp
                i -= 1
            elif if_swapped:
                i = 0
                if_swapped = False
            else:
                i += 1

        for song in ordered_list:
            ordered_occurrences_list_file.write(str(song[0]) + "\t" + str(song[1]) + "\n")

        ordered_occurrences_list_file.close()



    def compile_user_data(self, folder_path, top_songs_limit = 10):
        # We will only be working in the /Data/ directory
        folder_path = folder_path + "Data/"
        user_data_raw = self.spotify.spotify.user(user=self.user_id)
        user_data_file = open(folder_path + "User Data.txt", "w")

        user_data_file.write("MADE BY NOOKRITZIA - https://open.spotify.com/user/22cs3m4tyj32y3rqx6usl2bqa?si=2bf7e37d734f4a1c\n")
        user_data_file.write("User Display Name: " + str(self.get_display_name()) + "\n")

        user_data_file.write("User Followers: " + str(self.get_user_followers()) + "\n")

        try:
            dump_folder_path = folder_path[:len(folder_path)-5]
            dump_folder_path += "Playlist Dump/"
            user_data_file.write("User Playlists: " + str(len(os.listdir(dump_folder_path))) + "\n")
        except Exception as e:
            print(str(e) + "\n" + "The Playlist Dump directory does not exist")

        try:
            all_songs_file = open(folder_path + "All Songs Compiled.txt", "r")
            user_data_file.write("Songs contained through all playlists: " + str(len(all_songs_file.readlines())) + "\n")
            all_songs_file.close()
        except Exception as e:
            print(str(e) + "\n" + "The Data directory does not exist or does not contain the proper sub-files.")

        try:
            song_occurrences_file = open(folder_path + "Song Occurrences List.txt", "r")
            song_occurrences_data = song_occurrences_file.readlines()
            top_songs_limit = min(len(song_occurrences_data), top_songs_limit)
            user_data_file.write("Unique songs contained through all playlists: " + str(len(song_occurrences_data)) + "\n\nTOP " + str(top_songs_limit) +" SONGS\n")



            for i in range(top_songs_limit):
                song_data = song_occurrences_data[len(song_occurrences_data) - i - 1]
                user_data_file.write(song_data)

            song_occurrences_file.close()
        except Exception as e:
            print(str(e) + "\n" + "The Data directory does not exist or does not contain the proper sub-files.")



        user_data_file.close()





    def get_display_name(self):
        return self.spotify.get_user_data()['display_name']

    def get_user_followers(self):
        return self.spotify.get_user_data()['followers']['total']

    def sanitize_text(self, link):
        bad_chars = "()/?:"
        for char in bad_chars:
            link = link.replace(str(char), '#')
        return link

    def if_song_exists(self, song_name, songs):
        for song in songs:
            if song_name == song:
                return True
        return False

    def song_occurrences(self, song_name, songs):
        occurrences = 0
        for song in songs:
            if song_name == song:
                occurrences += 1
        return occurrences

#example of how to set up class
#analyzer = SpotifyAnalyzer("PUT SPOTIFY ACCOUNT LINK HERE", "SPOTIFY API CLIENT ID", "SPOTIFY API SECRET ID")
#analyzer.analyzation_dump("OUTPUT OF FOLDER")

