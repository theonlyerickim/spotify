import pandas as pd
import glob
from datetime import date, datetime
from sklearn.neighbors import NearestNeighbors
import pickle
import spacy
nlp = spacy.load('en_core_web_lg')
import numpy as np

class Preprocess:
    def __init__(
            self, audio_features_path = "../data/audio_features/*", tracks_path = "../data/tracks/*",
            completed_tracks_path = "../data/completed/tracks/*", albums_path = "../data/albums/*",
            completed_albums_path = "../data/completed/albums/*", artists_path = "../data/artists/*",
            completed_artists_path = "../data/completed/artists/*"
    ):
        self.audio_features_path = audio_features_path
        self.tracks_path_list = [tracks_path, completed_tracks_path]
        self.albums_path_list = [albums_path, completed_albums_path]
        self.artists_path_list = [artists_path, completed_artists_path]
        self.audio_features = pd.DataFrame()
        self.tracks = pd.DataFrame()
        self.albums = pd.DataFrame()
        self.artists = pd.DataFrame()
        self.volume_minimum = 0.01


    def compile_audio_features(self):
        # compile audio features from csv files
        files = glob.glob(self.audio_features_path)
        for file in files:
            df = pd.read_csv(file, index_col=0)
            self.audio_features = pd.concat([self.audio_features, df], axis=0)

    def compile_tracks(self):
        # compile tracks from two locations
        for path in self.tracks_path_list:
            files = glob.glob(path)
            for file in files:
                df = pd.read_csv(file, index_col=0)
                self.tracks = pd.concat([self.tracks, df], axis=0)

    def compile_albums(self):
        #compile albums from two locations
        for path in self.albums_path_list:
            files = glob.glob(path)
            for file in files:
                df = pd.read_csv(file, index_col=0)
                self.albums = pd.concat([self.albums, df], axis=0)

    def compile_artists(self):
        # compile artists from two locations
        for path in self.artists_path_list:
            files = glob.glob(path)
            for file in files:
                df = pd.read_csv(file, index_col=0)
                self.artists = pd.concat([self.artists, df], axis=0)

    # merge files into a single dataframe
    def merge_artists_albums_tracks_audio_features(self):    
        self.compiled_data = self.audio_features.merge(self.tracks, how='inner', left_on='id', right_on='track_id')
        self.compiled_data = self.compiled_data.merge(self.albums, how='inner', on='album_id')
        self.compiled_data = self.compiled_data.merge(self.artists, how='inner', on='artist_id')

    # remove unwanted characters from genre column and one hot encode
    def preprocess_artist_genre_features(self):
        self.processed = self.compiled_data.copy()
        self.processed['artist_genre'] = self.compiled_data['artist_genre'].str.replace("\[", "", regex=True)
        self.processed['artist_genre'] = self.processed['artist_genre'].str.replace("]", "", regex=True)
        self.processed['artist_genre'] = self.processed['artist_genre'].str.replace("\'", "", regex=True)
        self.processed['artist_genre'] = self.processed['artist_genre'].str.replace("\"", "", regex=True)
        self.processed['artist_genre'] = self.processed['artist_genre'].str.replace(" ", "", regex=True)
        artist_genre_ohe = self.processed.artist_genre.str.get_dummies(sep=',')
        artist_genre_ohe = self.drop_duplicate_columns_and_low_volume_dummies(artist_genre_ohe, self.volume_minimum)
        self.processed = pd.concat([self.processed, artist_genre_ohe], axis=1)

    # min/max standardization for audio features
    def preprocess_audio_features(self):
        self.processed['danceability'] = self.standardize(self.processed['danceability'])
        self.processed['key'] = self.standardize(self.processed['key'])
        self.processed['loudness'] = self.standardize(self.processed['loudness'])
        self.processed['mode'] = self.standardize(self.processed['mode'])
        self.processed['speechiness'] = self.standardize(self.processed['speechiness'])
        self.processed['acousticness'] = self.standardize(self.processed['acousticness'])
        self.processed['instrumentalness'] = self.standardize(self.processed['instrumentalness'])
        self.processed['liveness'] = self.standardize(self.processed['liveness'])
        self.processed['tempo'] = self.standardize(self.processed['tempo'])

    # process recency feature 
    def preprocess_recency_feature(self):
        self.processed['album_release_date'] = self.processed['album_release_date'].apply(pd.to_datetime)
        self.processed['day_difference'] = datetime.today() - self.processed['album_release_date']
        self.processed['day_difference'] = self.processed['day_difference'].dt.days
        self.processed['day_difference'] = self.standardize(self.processed['day_difference'])

    @staticmethod
    def tidy_up(df):
        df.dropna(how='any', axis=0, inplace=True)
        df.drop_duplicates(inplace=True)
        df.reset_index(inplace=True, drop=True)
        df.drop(['id'], axis=1, inplace=True)
        return df

    @staticmethod
    def standardize(column):
        column = (column - column.min()) / (column.max() - column.min())
        return column

    @staticmethod
    def export(df, filename):
        df.to_csv(f'../data/preprocessed_data/{filename}_{date.today()}.csv')

    @staticmethod
    def drop_duplicate_columns_and_low_volume_dummies(df, volume_factor):
        volume_threshold = (volume_factor * len(df))
        df.reset_index(inplace=True, drop=True)
        df = df[df.columns[abs(df).sum() > volume_threshold]]
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.fillna(value=0)
        return df

class Training(Preprocess):
    def __init__(
            self, preprocessed_data_path='../data/preprocessed_data/recommender_data_2024-06-12_full_dataset.csv',
                 ):
        self.preprocessed_data_path = preprocessed_data_path
        self.knn_recommender = NearestNeighbors(metric='cosine', algorithm='brute')
        self.knn_search = NearestNeighbors(metric='cosine', algorithm='brute')

    # read in preprocessed data, drop columns for training
    def read_in_preprocessed_data(self):
        self.preprocessed_data = pd.read_csv(self.preprocessed_data_path, index_col=0)
        self.preprocessed_data.drop_duplicates(subset=['track_name'], inplace=True)
        self.preprocessed_data.reset_index(inplace=True)
        # self.preprocessed_data.to_csv('../data/preprocessed_data/recommender_data_2024-06-12_full_dataset_deduped.csv')
        self.preprocessed_search_data = self.preprocessed_data[
            ['track_name', 'artist_name', 'artist_genre']]
        self.preprocessed_recommender_data = self.preprocessed_data.drop([
                                                    'album_id', 'track_id', 'track_name',
                                                    'artist_id', 'artists_id', 'artists_name',
                                                    'album_name', 'album_release_date', 'artist_name',
                                                    'artist_genre'], axis=1)


    # transform audio features to embeddings for recommendation
    def transform_to_embeddings(self):
        self.vector_embedding = self.preprocessed_recommender_data.values

    # transform track names into embeddings for search
    def transform_track_name_to_embeddings(self):
        search_embedding = []
        for i in range(len(self.preprocessed_search_data)):
            search_embedding.append(self.preprocess_text(self.preprocessed_search_data.loc[i, 'track_name']))
        self.search_embedding = np.stack(search_embedding, axis=0)

    # save recommender feature labels
    def save_features(self):
        self.recommender_features = self.preprocessed_recommender_data.columns

    # train recommender
    def train_recommender(self):
        self.knn_recommender.fit(self.vector_embedding)

    # train search engine
    def train_search(self):
        self.knn_search.fit(self.search_embedding)

    # save recommender model and metadata
    def save_recommender_model(self):
        Models = dict()
        Models['knn_recommender'] = self.knn_recommender
        Models['recommender_features'] = self.recommender_features
        Models['track_name'] = dict(zip(self.preprocessed_data.index, self.preprocessed_data['track_name']))
        Models['artist_name'] = dict(zip(self.preprocessed_data.index, self.preprocessed_data['artist_name']))
        Models['artist_genre'] = dict(zip(self.preprocessed_data.index, self.preprocessed_data['artist_genre']))
        with open("../models/knn_recommender.pkl", "wb") as f:
            pickle.dump(Models, f)

    # save search model and metadata
    def save_search_model(self):
        Models = dict()
        Models['knn_search'] = self.knn_search
        Models['track_name'] = dict(zip(self.preprocessed_search_data.index, self.preprocessed_search_data['track_name']))
        Models['artist_name'] = dict(zip(self.preprocessed_search_data.index, self.preprocessed_search_data['artist_name']))
        Models['artist_genre'] = dict(zip(self.preprocessed_search_data.index, self.preprocessed_search_data['artist_genre']))
        with open("../models/knn_search.pkl", "wb") as f:
            pickle.dump(Models, f)

    @staticmethod
    def preprocess_text(text):
        doc = nlp(text)

        processed_text_list = []
        for token in doc:

            if token.is_punct:
                continue

            processed_text_list.append(token.lemma_.lower())

            processed_text = ' '.join(processed_text_list)
            processed_text = nlp(processed_text).vector
        return processed_text

if __name__ == '__main__':
    data = Preprocess()
    data.compile_audio_features()
    data.compile_tracks()
    data.compile_albums()
    data.compile_artists()
    data.merge_artists_albums_tracks_audio_features()
    data.preprocess_artist_genre_features()
    data.preprocess_audio_features()
    data.preprocess_recency_feature()
    data.processed = data.tidy_up(data.processed)
    # data.export(data.processed, 'recommender_data')

    recommender_search_model = Training()
    recommender_search_model.read_in_preprocessed_data()

    #recommendation system
    recommender_search_model.save_features()
    recommender_search_model.transform_to_embeddings()
    recommender_search_model.train_recommender()
    recommender_search_model.save_recommender_model()


    #search engine
    recommender_search_model.transform_track_name_to_embeddings()
    recommender_search_model.train_search()
    recommender_search_model.save_search_model()












