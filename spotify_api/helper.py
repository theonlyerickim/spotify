import base64
from requests import post, get
import json
from string import ascii_lowercase as alphabet
import time
import pandas as pd
import glob
import shutil

class SpotifyAPI:
    def __init__(self, client_id, client_secret):

        ## credentials to pull token
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None

    def get_token(self):
        auth_string = self.client_id + ":" + self.client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        self.token = json_result["access_token"]

    # get_artist api service  
    # batch_size are the number of files per alphabet letter
    # each file contains 50 artists
    def get_artists(self, batch_size):
        for letter in alphabet:
            for batch in range(batch_size):

                # avoid api rate limit
                time.sleep(2)
                url = "https://api.spotify.com/v1/search?q="
                headers = {"Authorization": "Bearer " + self.token}
                query = f"{letter}&type=artist&limit=50&offset={batch}"
                query_url = url + query
                result = get(query_url, headers=headers)
                json_result = json.loads(result.content)
                ## lookout for 429's, exceeding rate limit
                print(result)

                artist_search_results = []
                if not (json_result.get('artists') is None):
                    for i in range(len(json_result['artists']['items'])):
                        if not ((json_result['artists']['items'][i].get('name') == 'A') or
                                (json_result['artists']['items'][i].get('name') == 'a') or
                                (json_result['artists']['items'][i].get('name') == 'Â') or
                                (json_result['artists']['items'][i].get('name') == 'Å')):

                            ##artist_name
                            if not (json_result['artists']['items'][i].get('name') is None):
                                artist_name = json_result['artists']['items'][i]['name']
                            else:
                                artist_name = null

                            ##artist_id
                            if not (json_result['artists']['items'][i].get('id') is None):
                                artist_id = json_result['artists']['items'][i]['id']
                            else:
                                artist_id = null

                            ##artist_popularity
                            if not (json_result['artists']['items'][i].get('id') is None):
                                artist_popularity = json_result['artists']['items'][i]['popularity']
                            else:
                                artist_popularity = null

                            ##artist_genre
                            if not (json_result['artists']['items'][i].get('genres') is None):
                                artist_genre = json_result['artists']['items'][i]['genres']
                            else:
                                artist_genre = null

                            artist_search_results.append({'artist_name': artist_name,
                                                          'artist_id': artist_id,
                                                          'artist_popularity': artist_popularity,
                                                          'artist_genre': artist_genre})

                    ## save jsons as csv
                    artist_search_results_df = pd.DataFrame(artist_search_results)
                    artist_search_results_df.to_csv(f'./data/artists/artist_search_results_{letter}_{batch}.csv')

    # album api service
    def pull_and_save_albums(self, artist_id):
        url = "https://api.spotify.com/v1/artists/"
        headers = {"Authorization": "Bearer " + self.token}
        query = f"{artist_id}/albums?include_groups=album&limit=50"

        query_url = url + query
        result = get(query_url, headers=headers)

        json_result = json.loads(result.content)

        albums_by_artist_list = []
        if not (json_result.get('items') is None):
            for i in range(len(json_result['items'])):

                ##artists_id
                if not (json_result['items'][i].get('artists') is None):
                    artist_id_list = []
                    for j in range(len(json_result['items'][i]['artists'])):
                        artist_id_list.append(json_result['items'][i]['artists'][j]['id'])
                else:
                    artist_id_list.append('')

                ##artist_name
                if not (json_result['items'][i].get('artists') is None):
                    artist_name_list = []
                    for j in range(len(json_result['items'][i]['artists'])):
                        artist_name_list.append(json_result['items'][i]['artists'][j]['name'])
                else:
                    artist_name_list.append('')

                    ##artist_id
                    artist_id = artist_id

                ##album_id
                if not (json_result['items'][i].get('id') is None):
                    album_id = json_result['items'][i]['id']
                else:
                    album_id = ''

                ##album_name
                if not (json_result['items'][i].get('name') is None):
                    album_name = json_result['items'][i]['name']
                else:
                    album_name = ''

                ##album_release_date
                if not (json_result['items'][i].get('release_date') is None):
                    album_release_date = json_result['items'][i]['release_date']
                else:
                    album_release_date = ''

                albums_by_artist_list.append({'artist_id': artist_id,
                                              'artists_id': artist_id_list,
                                              'artists_name': artist_name_list,
                                              'album_id': album_id,
                                              'album_name': album_name,
                                              'album_release_date': album_release_date})

        albums_by_artist_df = pd.DataFrame(albums_by_artist_list)
        albums_by_artist_df.to_csv(f'./data/albums/albums_by_artist_df_{artist_id}.csv')
        return result

    def get_albums(self):
        files = glob.glob('./data/artists/*', recursive=True)
        for file in files:
            #avoid api rate limit
            read_in_file = pd.read_csv(file)
            for artist_id in read_in_file['artist_id']:
                time.sleep(2)
                result = self.pull_and_save_albums(artist_id)
                print(result)

            # move completed files to track what is pulled
            if (result.__dict__['status_code'] == 200) or (result.__dict__['status_code'] == 404):
                new_path = file.replace('./data/artists/',
                                        './data/completed/artists/')
                shutil.move(file, new_path)

    def pull_and_save_tracks(self, album_id):
        url = "https://api.spotify.com/v1/albums/"
        headers = {"Authorization": "Bearer " + self.token}
        query = f"{album_id}/tracks?limit=50"

        query_url = url + query
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)

        tracks_by_album_list = []
        if not (json_result.get('items') is None):
            for i in range(len(json_result['items'])):

                ##track_id
                if not (json_result['items'][i].get('id') is None):
                    track_id = json_result['items'][i].get('id')
                else:
                    track_id = ''

                ##track_name
                if not (json_result['items'][i].get('id') is None):
                    track_name = json_result['items'][i].get('name')
                else:
                    track_name = ''

                tracks_by_album_list.append({'album_id': album_id, 'track_id': track_id,
                                             'track_name': track_name})

        tracks_by_album_df = pd.DataFrame(tracks_by_album_list)
        tracks_by_album_df.to_csv(f'./data/tracks/tracks_by_album_df_{album_id}.csv')
        return result

    # get_tracks api service
    def get_tracks(self):
        files = glob.glob('./data/albums/*', recursive=True)
        for file in files:
            #avoid api rate limit
            read_in_file = pd.read_csv(file)
            for album_id in read_in_file['album_id']:
                time.sleep(2)
                result = self.pull_and_save_tracks(album_id)
                print(result)

            # move completed files to track what is pulled
            if (result.__dict__['status_code'] == 200) or (result.__dict__['status_code'] == 404):
                new_path = file.replace('./data/albums/',
                                        './data/completed/albums/')
                shutil.move(file, new_path)

    def pull_and_save_audio_embeddings(self, track_id, album_id):
        query_url = f"https://api.spotify.com/v1/audio-features?ids={track_id}"
        headers = {"Authorization": "Bearer " + self.token}
        result = get(query_url, headers=headers)
        jsonlst = json.loads(result.content)['audio_features']
        audio_features_list = []
        for i in range(len(jsonlst)):
            audio_features = {'id': jsonlst[i]['id'],
                              'danceability': jsonlst[i]['danceability'],
                              'key': jsonlst[i]['key'],
                              'loudness': jsonlst[i]['loudness'],
                              'mode': jsonlst[i]['mode'],
                              'speechiness': jsonlst[i]['speechiness'],
                              'acousticness': jsonlst[i]['acousticness'],
                              'instrumentalness': jsonlst[i]['instrumentalness'],
                              'liveness': jsonlst[i]['liveness'],
                              'tempo': jsonlst[i]['tempo']
                              }

            audio_features_list.append(audio_features)
            audio_features_df = pd.DataFrame(audio_features_list)
            audio_features_df.to_csv(f'./data/audio_features/audio_features_df_{album_id}.csv')
        return result

    # get_audio_features api service
    def get_audio_features(self):
        files = glob.glob('./data/tracks/*', recursive=True)
        for file in files:
            #avoid api rate limit
            time.sleep(2)
            track_id_list = []
            read_in_file = pd.read_csv(file)
            track_ids_list = read_in_file['track_id'].tolist()
            track_ids_string = ','.join(track_ids_list)
            album_id = read_in_file.loc[0,'album_id']
            result = self.pull_and_save_audio_embeddings(track_ids_string, album_id)
            print(result)

            #move completed files to track what is pulled
            if (result.__dict__['status_code'] == 200) or (result.__dict__['status_code'] == 404):
                new_path = file.replace('./data/tracks/',
                                        './data/completed/tracks/')
                shutil.move(file, new_path)

