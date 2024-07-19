from flask import Flask
import joblib


# Initialize App
app = Flask(__name__)

# Load models
knn_searcher = joblib.load('models/knn_search.pkl')
knn_recommender = joblib.load('models/knn_recommender.pkl')
