# Spotify
This project uses Spotify data to build a search engine and recommendation system using K-Nearest Neighbors (KNN) alogrithm. 

# Project
This project is to develop a search engine and recommendation systems using metadata pulled from the Spotify API.  There are four classes in the Spotify project: 

* SpotifyAPI - The SpotifyAPI class in the helper.py file in the spotify_api folder pulls metadata from the Spotify api.  
* Preprocess - The Preprocess class in the train.py file in the training folder preprocesses the metadata pulled from the Spotify API.  
* Training - The Training class in the train.py file in the training folder trains the proprocessed data using K-neigherest Neighbors (KNN). 
* Inference - The Inference class in the function.py file uses a search query and playlist to return relevant tracknames and recommended playlist.   

## SpotifyAPI Class
The Spotify API class pulls data from multiple services and does the following: 
* Get token to pull from their API using the get_token method.
* Pulls artist information using the get_artist method.
* Pulls album information using the get_albums method.
* Pull track information using the get_tracks method.
* Pulls audio features/embeddings using the pull_and_save_audio_embeddings method.
The current methods are configured to pull a limited amount of data.  To pull a more comprehensive set of data from the SpotifyAPI, increase the batch_size parameter in the get_artist method. 

## Preprocess Class
The Preprocess class compiles the data all the difference services, merges the data, and preproceses into a dataframe for training.  Preprocesses entails the following:
* Standardizing audio features using a min_max approach for the audio features.  Features such as genre, recency, danceability, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, and tempo are standardized and transformed into audio embeddings.  The audio embedding are numerical vectors that are used in the recommender.  
* Genres are converted to dummy variables.  Genres with low sample size are removed through a method called drop_duplicate_columns_and_low_volume_dummies to prevent over dimensionality.

## Training Class
The Training class uses K-Nearest Neighbors to build a search engine and recommendation system.  The models are prototypes, so only search track name terms.  This can be expanded to include artists.  The training process includes the following: 
* Tracknames are tokenized and lemmitized prior to converting into embeddings.  
* Tracknames are transformed into numeric vectors using Spacy's tok2vec transformer (https://spacy.io/usage/embeddings-transformers).  This is for the search engine. 
* Audio features for the recommendation system is transformed into embeddings
* Two models are trained and saved in the models folder, one for the search engine (knn_search.pkl) and one for the playlist recommendation (knn_recommender.pkl).
* Models are trained using cosine distances

## Inference Class
The Inference class loads the knn_search.pkl and knn_recommender.pkl files and uses a json file (request.json) to perform inference
* The request.json file contains a search term, a playlist, and the number of nearest neighbors for both models.  
* The search engine uses the search term in the json file and returns track names most similar based on cosine distances.  
* The playlist is an example of a user playlist, which the recommender uses to provide recommended songs based on audio embedding features.  This also uses cosine distances.  

## Example of the json request

```
[
  {
    "search": "money",
    "playlist": [
      509,
      637,
      6911,
      9165, 
      13250,
      935, 
      970
    ],
    "recommender_neighbors": 10000, 
    "search_neighbors": 20
  }
]
```

## Search Engine Response
```
Search Term: money
***********************************************

SEARCH RESULTS BASED ON SEARCH TERM ONLY...
Track: Money
Artist: Yes
Genre: ['album rock', 'art rock', 'classic rock', 'hard rock', 'progressive rock', 'rock', 'soft rock', 'symphonic rock']
Distance (Cosine Similarity): 0.0

Track: Money
Artist: Lil Baby
Genre: ['atl hip hop', 'atl trap', 'rap', 'trap']
Distance (Cosine Similarity): 0.0

Track: Money Forever
Artist: Lil Baby
Genre: ['atl hip hop', 'atl trap', 'rap', 'trap']
Distance (Cosine Similarity): 0.09612805

Track: Money Maker
Artist: Mozzy
Genre: ['cali rap', 'sacramento hip hop']
Distance (Cosine Similarity): 0.18696684

Track: Lies & Money
Artist: Wood & Wire
Genre: ['neo-traditional bluegrass', 'progressive bluegrass']
Distance (Cosine Similarity): 0.19788003

```

## Example of User Playlist
```
USER PLAYLIST...
track name: Heatin Up (feat. Gunna)
artist name: Lil Baby
artist genre: ['atl hip hop', 'atl trap', 'rap', 'trap']

track name: Que Bonito Que Bonito
artist name: Ramon Ayala Y Sus Bravos Del Norte
artist genre: ['musica mexicana', 'norteno']

track name: Tic Tac
artist name: Lil Uzi Vert
artist genre: ['hip hop', 'melodic rap', 'philly rap', 'rage rap', 'rap', 'trap']

track name: Moment of Clarity
artist name: Lil Uzi Vert
artist genre: ['hip hop', 'melodic rap', 'philly rap', 'rage rap', 'rap', 'trap']

track name: Patek
artist name: Lil Uzi Vert
artist genre: ['hip hop', 'melodic rap', 'philly rap', 'rage rap', 'rap', 'trap']

track name: Large
artist name: Lil Baby
artist genre: ['atl hip hop', 'atl trap', 'rap', 'trap']

track name: My Drip
artist name: Lil Baby
artist genre: ['atl hip hop', 'atl trap', 'rap', 'trap']
```

## Recommendation Response based on User Playlist
```
USER PLAYLIST...
track name: Heatin Up (feat. Gunna)
artist name: Lil Baby
artist genre: ['atl hip hop', 'atl trap', 'rap', 'trap']

track name: Que Bonito Que Bonito
artist name: Ramon Ayala Y Sus Bravos Del Norte
artist genre: ['musica mexicana', 'norteno']

track name: Tic Tac
artist name: Lil Uzi Vert
artist genre: ['hip hop', 'melodic rap', 'philly rap', 'rage rap', 'rap', 'trap']

track name: Moment of Clarity
artist name: Lil Uzi Vert
artist genre: ['hip hop', 'melodic rap', 'philly rap', 'rage rap', 'rap', 'trap']

track name: Patek
artist name: Lil Uzi Vert
artist genre: ['hip hop', 'melodic rap', 'philly rap', 'rage rap', 'rap', 'trap']

track name: Large
artist name: Lil Baby
artist genre: ['atl hip hop', 'atl trap', 'rap', 'trap']

track name: My Drip
artist name: Lil Baby
artist genre: ['atl hip hop', 'atl trap', 'rap', 'trap']

```

## Docker
The search engine and recommendation system is setup to run on Docker.    
* The docker container includes Flask webserver 
* To build a docker image and run a container, execute the following commands: 
```
docker build .
docker run -p 8000:8000 <image ID>

```
* Run the following curl command to run inference
```
curl -d @request.json -H "Content-Type: application/json" -X POST http://0.0.0.0:8000/predict

```

