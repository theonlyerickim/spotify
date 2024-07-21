# spotify
Build a search engine and recommender using K-neigherest Neighbors (KNN) alogrithm using Spotify data

# Project
This project is to develop a search engine and recommendation systems using metadata pulled from the Spotify API.  There are four classes in the Spotify project: 

* SpotifyAPI - The SpotifyAPI class in the helper.py file in the spotify_api folder pulls metadata from the Spotify api.  
* Preprocess - The Preprocess class in the train.py file in the training folder preprocesses the metadata pulled from the Spotify API.  
* Training - The Training class in the train.py file in the training folder trains the proprocessed data using K-neigherest Neighbors (KNN). 
* Inference - The Inference class in the function.py file uses a search query and playlist to return relevant tracknames and recommended playlist.   
