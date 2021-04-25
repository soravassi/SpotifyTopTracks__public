import time
import os

from flask import Flask, render_template, redirect, request, session, make_response,session,redirect
import spotipy
import spotipy.util as util
from creds import *

import requests
app = Flask(__name__)

app.secret_key = SECRET_KEY

API_BASE = 'https://accounts.spotify.com'

REDIRECT_URI = "http://localhost:5000/callback"

SCOPE = 'playlist-modify-private,playlist-modify-public,user-top-read'

SHOW_DIALOG = True


@app.route("/")
def verify():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLIENT_ID, client_secret = SECRET_KEY, redirect_uri = CALLBACK, scope = SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

@app.route("/index")
def index():
    return redirect("go")

@app.route("/callback")
def callback():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLIENT_ID, client_secret = SECRET_KEY, redirect_uri = CALLBACK, scope = SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    session["token_info"] = token_info


    return redirect("index")


# Spotify returns requested data
@app.route("/go")
def go():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')
    #data = request.form
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    response = sp.current_user_top_tracks(time_range="short_term", limit=5)
    ids = []
    for item in response['items']:
        ids.append(str(item['id']))
    response = sp.current_user_top_tracks(time_range="medium_term", limit=5)
    ids_medium = []
    for item in response['items']:
        ids_medium.append(str(item['id']))
    response = sp.current_user_top_tracks(time_range="long_term", limit=5)
    ids_long = []
    for item in response['items']:
        ids_long.append(str(item['id']))
    os.remove(".cache")
    session.clear()
    # print(json.dumps(response))
    return render_template("results.html", track_ids = ids, track_ids_medium = ids_medium, track_ids_long = ids_long)

def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    if (is_token_expired):
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLIENT_ID, client_secret = SECRET_KEY, redirect_uri = CALLBACK, scope = SCOPE)
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

if __name__ == "__main__":
    app.run(debug=True)


