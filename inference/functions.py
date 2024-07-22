import json
from training import train as train
import pickle

class Inference(train.Training):
    def __init__(self,
                 knn_search_path = "/app/models/knn_search.pkl",
                 knn_recommender_path = "/app/models/knn_recommender.pkl",
                 request_path = "/app/request/request.json",
                 preprocessed_data_path= "/app/data/preprocessed_data/recommender_data_2024-06-12_full_dataset.csv"
                 ):
        self.knn_search_path = knn_search_path
        self.knn_recommender_path = knn_recommender_path
        self.request_path = request_path
        self.preprocessed_data_path = preprocessed_data_path

    def read_json(self):
        f = open(self.request_path)
        self.json_request = json.load(f)

    # load both models
    def load_models(self):
        #load search model
        self.knn_search = pickle.load(open(self.knn_search_path, 'rb'))
        #load recommender model
        self.knn_recommender = pickle.load(open(self.knn_recommender_path, 'rb'))

    # search engine
    def search_inference(self):
        self.search_results_distances, self.search_results_indices = \
            self.knn_search['knn_search'].kneighbors(self.search_embedding.reshape(1, -1), n_neighbors =
            self.json_request[0]['search_neighbors'])

    # recommendation system
    def recommender_inference(self):
        self.recommender_results_distances, self.recommender_results_indices = \
            self.knn_recommender['knn_recommender'].kneighbors(self.playlist_embedding.reshape(1,-1), n_neighbors=
            self.json_request[0]['recommender_neighbors'])

    # transform user playlist into embeddings for recommender inference
    def playlist_summary(self):
        playlist = self.preprocessed_recommender_data.iloc[self.json_request[0]['playlist']]
        playlist_indexed = playlist.reindex(self.knn_recommender['recommender_features'], axis=1)
        df_playlist_mean = playlist_indexed.mean().to_frame().T
        self.playlist_embedding = df_playlist_mean.values

    # print results
    def print_search_results(self):
        print('Search Results: ')
        for i in range(len(self.search_results_indices[0][:10])):
            print('')
            print('Search Results')
            print('Track:', self.knn_search['track_name'][self.search_results_indices[0][i]])
            print('Artist:', self.knn_search['artist_name'][self.search_results_indices[0][i]])
            print('Genre:', self.knn_search['artist_genre'][self.search_results_indices[0][i]])
            print('Distance', self.search_results_distances[0][i])

    def print_recommender_results(self):
        print('Recommended Playlist: ')
        for i in range(len(self.recommender_results_indices[0][:20])):
            print('')
            print('Recommendation Playlist')
            print('Track:', self.knn_recommender['track_name'][self.recommender_results_indices[0][i]])
            print('Artist:', self.knn_recommender['artist_name'][self.recommender_results_indices[0][i]])
            print('Genre:', self.knn_recommender['artist_genre'][self.recommender_results_indices[0][i]])
            print('Distance', self.recommender_results_distances[0][i])
















