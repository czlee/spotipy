# -*- coding: utf-8 -*-

import os
import pprint
import sys
import unittest

import requests

sys.path.insert(0, os.path.abspath(os.pardir))

from spotipy import (
    CLIENT_CREDS_ENV_VARS as CCEV,
    prompt_for_user_token,
    Spotify,
    SpotifyException,
)


class TestSpotipy(unittest.TestCase):

    """
    These tests require user authentication - provide client credentials using the
    following environment variables

    ::

        'SPOTIPY_CLIENT_USERNAME'
        'SPOTIPY_CLIENT_ID'
        'SPOTIPY_CLIENT_SECRET'
        'SPOTIPY_REDIRECT_URI'
    """

    creep_urn = 'spotify:track:3HfB5hBU0dmBt8T0iCmH42'
    creep_id = '3HfB5hBU0dmBt8T0iCmH42'
    creep_url = 'http://open.spotify.com/track/3HfB5hBU0dmBt8T0iCmH42'
    el_scorcho_urn = 'spotify:track:0Svkvt5I79wficMFgaqEQJ'
    el_scorcho_bad_urn = 'spotify:track:0Svkvt5I79wficMFgaqEQK'
    pinkerton_urn = 'spotify:album:04xe676vyiTeYNXw15o9jT'
    weezer_urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'
    pablo_honey_urn = 'spotify:album:6AZv3m27uyRxi8KyJSfUxL'
    radiohead_urn = 'spotify:artist:4Z8W4fKeB5YxbusRsdQVPb'
    angeles_haydn_urn = 'spotify:album:1vAbqAeuJVWNAe7UR00bdM'


    bad_id = 'BAD_ID'

    @classmethod
    def setUpClass(self):
        missing = filter(lambda var: not os.getenv(CCEV[var]), CCEV)

        if missing:
            raise Exception('Please set the client credentials for the test application using the following environment variables: {}'.format(CCEV.values()))

        self.username = os.getenv(CCEV['client_username'])

        self.scope = 'user-library-read'

        self.token = prompt_for_user_token(self.username, scope=self.scope)

        self.spotify = Spotify(auth=self.token)

    def test_artist_urn(self):
        artist = self.spotify.artist(self.radiohead_urn)
        self.assertTrue(artist['name'] == 'Radiohead')

    def test_artists(self):
        results = self.spotify.artists([self.weezer_urn, self.radiohead_urn])
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']) == 2)

    def test_album_urn(self):
        album = self.spotify.album(self.pinkerton_urn)
        self.assertTrue(album['name'] == 'Pinkerton')

    def test_album_tracks(self):
        results = self.spotify.album_tracks(self.pinkerton_urn)
        self.assertTrue(len(results['items']) == 10)

    def test_album_tracks_many(self):
        results = self.spotify.album_tracks(self.angeles_haydn_urn)
        tracks = results['items']
        total, received = results['total'], len(tracks)
        while received < total:
            results = self.spotify.album_tracks(self.angeles_haydn_urn, offset=received)
            tracks.extend(results['items'])
            received = len(tracks)

        self.assertEqual(received, total)

    def test_albums(self):
        results = self.spotify.albums([self.pinkerton_urn, self.pablo_honey_urn])
        self.assertTrue('albums' in results)
        self.assertTrue(len(results['albums']) == 2)

    def test_track_urn(self):
        track = self.spotify.track(self.creep_urn)
        self.assertTrue(track['name'] == 'Creep')

    def test_track_id(self):
        track = self.spotify.track(self.creep_id)
        self.assertTrue(track['name'] == 'Creep')

    def test_track_url(self):
        track = self.spotify.track(self.creep_url)
        self.assertTrue(track['name'] == 'Creep')

    def test_track_bad_urn(self):
        try:
            track = self.spotify.track(self.el_scorcho_bad_urn)
            self.assertTrue(False)
        except SpotifyException:
            self.assertTrue(True)

    def test_tracks(self):
        results = self.spotify.tracks([self.creep_url, self.el_scorcho_urn])
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']) == 2)

    def test_artist_top_tracks(self):
        results = self.spotify.artist_top_tracks(self.weezer_urn)
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']) == 10)

    def test_artist_related_artists(self):
        results = self.spotify.artist_related_artists(self.weezer_urn)
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']) == 20)
        for artist in results['artists']:
            if artist['name'] == 'Jimmy Eat World':
                found = True
        self.assertTrue(found)

    def test_artist_search(self):
        results = self.spotify.search(q='weezer', type='artist')
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']['items']) > 0)
        self.assertTrue(results['artists']['items'][0]['name'] == 'Weezer')

    def test_artist_search_with_market(self):
        results = self.spotify.search(q='weezer', type='artist', market='GB')
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']['items']) > 0)
        self.assertTrue(results['artists']['items'][0]['name'] == 'Weezer')

    def test_artist_albums(self):
        results = self.spotify.artist_albums(self.weezer_urn)
        self.assertTrue('items' in results)
        self.assertTrue(len(results['items']) > 0)

        found = False
        for album in results['items']:
            if album['name'] == 'Hurley':
                found = True

        self.assertTrue(found)

    def test_search_timeout(self):
        sp = Spotify(auth=self.token, requests_timeout=.1)
        try:
            results = sp.search(q='my*', type='track')
            self.assertTrue(False, 'unexpected search timeout')
        except requests.Timeout:
            self.assertTrue(True, 'expected search timeout')


    def test_album_search(self):
        results = self.spotify.search(q='weezer pinkerton', type='album')
        self.assertTrue('albums' in results)
        self.assertTrue(len(results['albums']['items']) > 0)
        self.assertTrue(results['albums']['items'][0]['name'].find('Pinkerton') >= 0)

    def test_track_search(self):
        results = self.spotify.search(q='el scorcho weezer', type='track')
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']['items']) > 0)
        self.assertTrue(results['tracks']['items'][0]['name'] == 'El Scorcho')

    def test_user(self):
        user = self.spotify.user(user='plamere')
        self.assertTrue(user['uri'] == 'spotify:user:plamere')

    def test_track_bad_id(self):
        try:
            track = self.spotify.track(self.bad_id)
            self.assertTrue(False)
        except SpotifyException:
            self.assertTrue(True)

    def test_track_bad_id(self):
        try:
            track = self.spotify.track(self.bad_id)
            self.assertTrue(False)
        except SpotifyException:
            self.assertTrue(True)

    def test_unauthenticated_post_fails(self):
        with self.assertRaises(SpotifyException) as cm:
            self.spotify.user_playlist_create("spotify", "Best hits of the 90s")
        self.assertTrue(cm.exception.http_status == 401 or
            cm.exception.http_status == 403)

    def test_custom_requests_session(self):
        sess = requests.Session()
        sess.headers["user-agent"] = "spotipy-test"
        with_custom_session = Spotify(auth=self.token, requests_session=sess)
        self.assertTrue(with_custom_session.user(user="akx")["uri"] == "spotify:user:akx")

    def test_force_no_requests_session(self):
        with_no_session = Spotify(auth=self.token, requests_session=False)
        self.assertFalse(isinstance(with_no_session._session, requests.Session))
        self.assertTrue(with_no_session.user(user="akx")["uri"] == "spotify:user:akx")


'''
    Need tests for:

        - next
        - previous
'''

if __name__ == '__main__':

    unittest.main()
