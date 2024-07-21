# Spotify
Build a search engine and recommender using K-neigherest Neighbors (KNN) alogrithm using Spotify data

# Project
This project is to develop a search engine and recommendation systems using metadata pulled from the Spotify API.  There are four classes in the Spotify project: 

* SpotifyAPI - The SpotifyAPI class in the helper.py file in the spotify_api folder pulls metadata from the Spotify api.  
* Preprocess - The Preprocess class in the train.py file in the training folder preprocesses the metadata pulled from the Spotify API.  
* Training - The Training class in the train.py file in the training folder trains the proprocessed data using K-neigherest Neighbors (KNN). 
* Inference - The Inference class in the function.py file uses a search query and playlist to return relevant tracknames and recommended playlist.   

## SpotifyAPI Class
The Spotify API class pulls data from multiple services and does the following: 
* Get token to pull from their API using the get_token method
* Pulls artist information using the get_artist method
* Pulls album information using the get_albums method
* Pull track information using the get_tracks method
* Pulls audio features/embeddings using the pull_and_save_audio_embeddings method
The current methods are configured to pull a limited amount of data.  To pull a more comprehensive set of data from the SpotifyAPI, increase the batch_size parameter in the get_artist method. 

## Preprocess Class
The Preprocess class compiles the data all the difference services, merges the data, and preproceses into a dataframe for training.  Preprocesses entails the following:
* Standardizing audio features using a min_max approach for the audio features.  Features such as genre, recency, danceability, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, and tempo are standardized and transformed into audio embeddings.  The audio embedding are numerical vectors that are used in the recommender.  
* Genres are converted to dummy variables.  Obscure genres with low sample size are removed through a method called drop_duplicate_columns_and_low_volume_dummies to prevent over dimensionality.
* Tracknames are transformed into 300 length vectors using tok2vec transformer (https://spacy.io/usage/embeddings-transformers).  This transformation is for the search engine


