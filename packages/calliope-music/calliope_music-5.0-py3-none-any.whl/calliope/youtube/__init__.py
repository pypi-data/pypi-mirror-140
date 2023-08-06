# Calliope
# Copyright (C) 2020  Sam Thursfield <sam@afuera.me.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import googleapiclient.discovery
import googleapiclient.errors

import httplib2
import logging
import pathlib

import calliope.cache  # pylint: disable=cyclic-import

log = logging.getLogger(__name__)


class YoutubeContext():
    def __init__(self, config, caching=True):
        self.config = config
        self.caching = caching

    def authenticate(self):
        """Authenticate to access public data.

        To access private data, you need to use OAuth2 rather than API key
        authorisation, using google_auth_oauthlib.

        """
        api_service_name = "youtube"
        api_version = "v3"
        api_key = self.config.get('youtube', 'api-key')

        if self.caching:
            cache_path = calliope.cache.save_cache_path('calliope/youtube')
            http = httplib2.Http(cache=str(cache_path))
        else:
            http = None

        api = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=api_key, http=http)
        return api


def get_channel_id(api, username):
    log.info("Querying channel ID for username %s", username)
    request = api.channels().list(forUsername=username, part='id')
    response = request.execute()
    log.debug("Got response: %s", response)
    return response['items'][0]['id']


def _get_playlists(api, channel_id):
    log.info("Querying playlists for channel %s", channel_id)
    request = api.playlists().list(
        part=['id', 'contentDetails', 'snippet'], channelId=channel_id,
        maxResults=50)
    response = request.execute()
    log.debug("Got response: %s", response)
    return response['items']


def export(api, channel_id):
    playlists = _get_playlists(api, channel_id)
    for playlist in playlists:
        playlist_info = {
            'playlist.title': playlist['snippet']['title'],
            'playlist.image': playlist['snippet']['thumbnails']['default']['url'],
            'playlist.location': 'https://www.youtube.com/playlist?list=' + playlist['id'],
        }
        first_item = True

        expected_tracks = playlist['contentDetails']['itemCount']
        page_token = None
        log.debug("Expecting %i tracks", expected_tracks)
        while True:
            request = api.playlistItems().list(
                part=['contentDetails', 'snippet'],
                maxResults=50,
                playlistId=playlist['id'],
                pageToken=page_token,
            )
            response = request.execute()
            log.debug("Got response: %s", response)

            for item in response['items']:
                item_info = {
                    'title': item['snippet']['title'],
                    'location':'https://www.youtube.com/watch?v=' + item['id'],
                }
                if first_item:
                    item_info.update(playlist_info)
                    first_item = False
                yield item_info

            if 'nextPageToken' in response:
                page_token = response['nextPageToken']
            else:
                break
