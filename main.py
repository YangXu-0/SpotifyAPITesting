import requests as rq
import base64
import datetime
from urllib.parse import urlencode
from bs4 import BeautifulSoup as bs
from pathlib import Path
import os


def save_token(token, expire_time):
    if not Path("auth_token.txt").is_file():
        f = open("auth_token.txt", 'x')
        f.write(f"[{token}, {expire_time}]")
        f.close()
    else:
        os.remove("auth_token.txt")
        save_token(token, expire_time)


def api_token(url, data, header):   # Function used to obtain api token
    token_response = rq.post(url, data=data, headers=header)

    valid_request = token_response.status_code in range(200, 299)
    if not valid_request:
        raise Exception(f'error status code: {token_response.status_code}')

    token_response_data = token_response.json()

    now = datetime.datetime.now()
    access_token = token_response_data['access_token']
    expire_time = token_response_data['expires_in']
    expires = now + datetime.timedelta(seconds=expire_time)
    save_token(access_token, expires)


client_id =    # Client id
client_secret =    # Client secret
client_creds = f"{client_id}:{client_secret}"
client_creds_b64 = base64.b64encode(client_creds.encode())

token_url = "https://accounts.spotify.com/api/token"
method = "POST"

token_data = {
    "grant_type": "client_credentials"
}
token_header = {
    "Authorization": f"Basic {client_creds_b64.decode()}"
}

if not Path("auth_token.txt").is_file():
    api_token(token_url, token_data, token_header)
else:
    token_txt = open("auth_token.txt", 'r')
    l_token_txt = token_txt.read().strip('][').split(', ')

    if not(datetime.datetime.now() < datetime.datetime.strptime(l_token_txt[1], '%Y-%m-%d %H:%M:%S.%f')):
        token_txt.close()
        api_token(token_url, token_data, token_header)
    else:
        token_txt.close()

token_txt = open("auth_token.txt", 'r')
l_token_txt = token_txt.read().strip('][').split(', ')

access_token = l_token_txt[0]
expires = datetime.datetime.strptime(l_token_txt[1], '%Y-%m-%d %H:%M:%S.%f')
valid_token = datetime.datetime.now() < expires
token_txt.close()

print(access_token, datetime.datetime.now(), expires)

while valid_token:
    print("Enter type of data (album, playlist) or 'exit' to quit")
    search_type = input()

    if search_type == 'exit':
        exit()

    print("Enter name")
    search_name = input()

    search_header = {
        "Authorization": f"Bearer {access_token}"
    }
    endpoint = "https://api.spotify.com/v1/search"
    data = urlencode({"q": search_name, "type": search_type})
    lookup = f"{endpoint}?{data}"
    search_data = rq.get(lookup, headers=search_header)

    if not(search_data.status_code == 200):
        raise Exception(f"error {search_data.status_code}")

    search_json = search_data.json()
    print(search_json)

    total_tracks = search_json['playlists']['items'][0]['tracks']['total']   # int
    transfer_page = rq.get(f"{search_json['playlists']['items'][0]['tracks']['href']}", headers=search_header)
    full_search_json = transfer_page.json()

    list_tracks = []
    for i in range(len(full_search_json['items'])):
        list_tracks.append(full_search_json['items'][i]['track']['id'])

    track_endpoint = f"https://api.spotify.com/v1/tracks/{list_tracks[0]}"
    tracks_info = bs(rq.get(track_endpoint, headers=search_header).content, 'html.parser')
    print(tracks_info)

    valid_token = datetime.datetime.now() < expires
    if not valid_token:
        access_token, expires = api_token(token_url, token_data, token_header)

print("while loop broke")
