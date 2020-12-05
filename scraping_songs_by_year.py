import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from decimal import *
import re
import requests
from bs4 import BeautifulSoup
import json


# access token

client_id = 'your client id'
client_secret = 'your client secret'

auth_url = 'https://accounts.spotify.com/api/token'

auth_re = requests.post(auth_url, {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
})

auth_data = auth_re.json()
access_token = auth_data['access_token']

print('access token =' ,access_token)


# 從 Spotify API 抓取 1901-2021 每個年度 2,000 首歌的資訊

for year in range(1901, 1921):

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    url_search = f'https://api.spotify.com/v1/search/'
    url_features = f'https://api.spotify.com/v1/audio-features/'
    url_artists = f'https://api.spotify.com/v1/artists/'

    # first entry
    # tracks search by year
    payload_search = {
        'q': f'year:{year}',
        'type': 'track',
        'offset': 0,
        'limit': 50}
    re_search = requests.get(url_search, params=payload_search, headers=headers)
    data_search = json.loads(re_search.text)

    df = pd.json_normalize(data_search['tracks']['items'], sep='_', max_level=1)
    df_artists = pd.json_normalize(pd.DataFrame(df['artists'])['artists'].apply(lambda x: x[0]))
    columns = ['artists_' + c for c in df_artists.columns]
    df_artists.columns = columns
    df = pd.concat([df, df_artists], axis=1)
    df_main = df[['name', 'id', 'album_name', 'album_id', 'album_release_date', 'artists_name', 'artists_id', 'popularity']].copy()


    # audio features by track_id
    tracks_id_lst = df_main['id']
    payload_features = {
        'ids': ",".join(tracks_id_lst)}
    re_features = requests.get(url_features, params=payload_features, headers=headers)
    data_features = json.loads(re_features.text)

    df_features = pd.DataFrame(data_features['audio_features'])
    df_main = pd.concat([df_main, df_features], axis=1)


    # artists genres by artists_id
    artists_id_lst = df_main['artists_id']
    payload_artists = {
        'ids': ",".join(artists_id_lst)}
    re_artists = requests.get(url_artists, params=payload_artists, headers=headers)
    data_artists = json.loads(re_artists.text)

    df_artists = pd.DataFrame(data_artists['artists'])
    df_main = pd.concat([df_main, df_artists['genres']], axis=1)

    locals()['df_' + str(year)] = df_main.copy()

    
    for i in range(50, 2000, 50):

        # tracks search by year
        payload_search = {
            'q': f'year:{year}',
            'type': 'track',
            'offset': i,
            'limit': 50}
        re_search = requests.get(url_search, params=payload_search, headers=headers)
        data_search = json.loads(re_search.text)
        
        # 解決歌曲不到 2,000 首時的問題
        try:
            df = pd.json_normalize(data_search['tracks']['items'], sep='_', max_level=1)
            df_artists = pd.json_normalize(pd.DataFrame(df['artists'])['artists'].apply(lambda x: x[0]))
            columns = ['artists_' + c for c in df_artists.columns]
            df_artists.columns = columns
            df = pd.concat([df, df_artists], axis=1)
            df_main = df[['name', 'id', 'album_name', 'album_id', 'album_release_date', 'artists_name', 'artists_id', 'popularity']].copy()


            # audio features by track_id
            tracks_id_lst = df_main['id']
    #         print(tracks_id_lst)
            payload_features = {
                'ids': ",".join(tracks_id_lst)}
            re_features = requests.get(url_features, params=payload_features, headers=headers)
            data_features = json.loads(re_features.text)

            # 解決 api 拿回的資料有空值問題
            none_dic = {'danceability': None, 'energy': None, 'key': None, 'loudness': None, 'mode': None, 
                'speechiness': None, 'acousticness': None, 'instrumentalness': None, 'liveness': None, 
                'valence': None, 'tempo': None, 'type': None, 'id': None, 'uri': None, 
                'track_href': None, 'analysis_url': None, 'duration_ms': None, 'time_signature': None}

            while None in data_features['audio_features']:
                i = data_features['audio_features'].index(None)
                data_features['audio_features'][i] = none_dic        

            df_features = pd.DataFrame(data_features['audio_features'])
            df_main = pd.concat([df_main, df_features], axis=1)


            # artists genres by artists_id
            artists_id_lst = df_main['artists_id']
            payload_artists = {
                'ids': ",".join(artists_id_lst)}
            re_artists = requests.get(url_artists, params=payload_artists, headers=headers)
            data_artists = json.loads(re_artists.text)

            df_artists = pd.DataFrame(data_artists['artists'])
            df_main = pd.concat([df_main, df_artists['genres']], axis=1)

            locals()['df_' + str(year)] = pd.concat([locals()['df_' + str(year)], df_main])
            
        except KeyError as e:
            print('Error Information: ' + str(e))
            break

#         print(f'offset_{i} concated.')

    locals()['df_' + str(year)].reset_index(drop=True)
    locals()['df_' + str(year)].to_csv(f'your path/data-{year}.csv', index=False)
    
    print(f'data-{year} completed.')
