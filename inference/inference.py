import os
from inference.functions import *
# from functions import *

def run(feature_dict):
    search_recommender = Inference()
    search_recommender.json_request = feature_dict
    search_recommender.read_in_preprocessed_data()
    search_recommender.load_models()
    search_recommender.search_embedding = Inference.preprocess_text(search_recommender.json_request[0]['search'])
    search_recommender.search_inference()
    search_recommender.print_search_results()

    search_recommender.playlist = search_recommender.preprocessed_recommender_data.iloc[search_recommender.json_request[0]['playlist']]
    search_recommender.playlist_summary()
    search_recommender.recommender_inference()
    search_recommender.print_recommender_results()

    return {
        'recommender_results_distances': search_recommender.recommender_results_distances[0][:10].tolist(), 
        'recommender_results_indices': search_recommender.recommender_results_indices[0][:10].tolist(), 
        'search_results_distances': search_recommender.search_results_distances[0][:10].tolist(),  
        'search_results_indices': search_recommender.search_results_indices[0][:10].tolist()
    }

if __name__ == '__main__':
    run()






