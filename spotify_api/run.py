import os
from helper import *
os.chdir('/Users/erickim/PycharmProjects/Spotify')

# batch_size are the number of files per alphabet letter  
# each file contains 50 artists  
batch_size = 50 

def run():
    spotify = SpotifyAPI('6cd187111baa44fb904cc33ff08a2efc', 'd4cb7f7362854984ab8d084e47413c8c')
    spotify.get_token()
    spotify.get_artists(batch_size)
    spotify.get_albums()
    spotify.get_tracks()
    spotify.get_audio_features()

if __name__ == '__main__':
    run()






