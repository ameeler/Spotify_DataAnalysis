import requests
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# https://stmorse.github.io/journal/spotify-api.html


# Gets track information for every Twenty One Pilots song
##################################################################################################
CLIENT_ID = "f0b26c5ec3994478a88fe67a7541c37c"
CLIENT_SECRET = "db2f6a7be58a45368bbd76678757970a"
AUTH_URL = 'https://accounts.spotify.com/api/token'


# Grabs access token
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']

# Puts access token into request header
headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# Sets base url and Twenty One Pilots artist ID
BASE_URL = 'https://api.spotify.com/v1/'
top_ID = '3YQKmKGau1PzlVlkL1iodx'

# GET request for artist's album list
results = requests.get(BASE_URL + 'artists/' + top_ID + '/albums',
                       headers=headers,
                       params={'include_groups': 'album', 'limit': 50})


album_data = results.json()
track_info = []
albums = []

# Loops through album list for track info
# Excludes duplicates and unwanted albums
for album in album_data['items']:

    album_name = album['name']

    if (albums.count(album_name) == 0) and ('(' not in album_name) and ('Spotify' not in album_name):

        albums.append(album_name)
        # print(album_name)

        track_results = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks',
                                     headers=headers)

        tracks = track_results.json()['items']

        #print("\n" + album_name + "'s tracks:")

        # Getting audio feature information for each track in each album
        for track in tracks:

            # print(track['name'])

            track_features = requests.get(BASE_URL + 'audio-features/' + track['id'],
                                          headers=headers)
            track_features = track_features.json()

            track_features.update({
                'track_name': track['name'],
                'album_name': album_name,
                'release_date': album['release_date'],
                'album_id': album['id']
            })

            track_info.append(track_features)
##################################################################################################

# Creates a data frame for track info
df = pd.DataFrame(track_info)

df['release_date'] = pd.to_datetime(df['release_date'])
df = df.sort_values(by='release_date')

plt.figure(figsize=(10, 10))
ax = sns.scatterplot(data=df,
                     x='valence',
                     y='release_date',
                     hue='album_name',
                     palette='rainbow',
                     size='duration_ms',
                     sizes=(50, 1000),
                     alpha=0.7)

h, labs = ax.get_legend_handles_labels()
ax.legend(h[1:10], labs[1:10], loc='best', title='none')

plt.show()
