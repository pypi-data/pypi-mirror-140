# pylint: disable=too-many-lines

# Calliope
# Copyright (C) 2018-2020  Sam Thursfield <sam@afuera.me.uk>
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

'''Calliope command line interface.

This module provides the public command line interface for Calliope.

'''

import click
import parsedatetime

import datetime
import functools
import json
import logging
import sys
import time

import calliope   # pylint: disable=cyclic-import


# The CLI is defined using the Click module. Every command is declared
# in this module.
#
# CLI documentation is auto-generated from this module using 'sphinx-click'.
# There is a special flag that can be set to stub out the actual code, which
# exists so that this module can be imported by `sphinx-build` without pulling
# in the rest of Calliope and the many external dependencies that it requires.
# This makes it simple to build and host our documentation on readthedocs.org.


DOC_URL = "https://calliope-music.readthedocs.io/en/latest"


class App:
    def __init__(self, verbosity=logging.WARNING):
        self.verbosity_level = verbosity
        self.config = None


def string_to_datetime(cal, string):
    dt, context = cal.parse(string)

    if context:
        return datetime.datetime.fromtimestamp(time.mktime(dt))
    else:
        raise RuntimeError(f"Unable to parse datetime: {string}")


@click.group()
@click.option('-v', '--verbosity', type=click.IntRange(1, 3),
              default=1)
@click.pass_context
def cli(context, verbosity):
    '''Calliope is a set of tools for processing playlists.'''

    verbosity = [
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
    ][verbosity - 1]

    context.obj = App(verbosity=verbosity)

    context.obj.config = calliope.config.Configuration()

    formatter = logging.Formatter(fmt='%(name)s %(message)s')
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(formatter)
    log = logging.getLogger()
    log.addHandler(handler)
    log.setLevel(context.obj.verbosity_level)


@cli.group(name='bandcamp', help="Query Bandcamp")
@click.option('--user', help="show data for the given Bandcamp user")
@click.pass_context
def bandcamp_cli(context, user):
    if isinstance(calliope.bandcamp, calliope.FailedModule):
        raise calliope.bandcamp.runtime_error()

    context.obj.bandcamp = calliope.bandcamp.BandcampContext(
        context.obj.config, user=user)


@bandcamp_cli.command(name='collection')
@click.pass_context
def cmd_bandcamp_collection(context):
    '''Show all albums in the collection of the given Bandcamp user.'''
    calliope.playlist.write(calliope.bandcamp.collection(context.obj.bandcamp),
                            sys.stdout)


@cli.group(name='beets', help="Query the Beets media database")
@click.pass_context
def beets_cli(context):
    pass


@beets_cli.command(name='albums')
@click.option('--include-tracks', is_flag=True, default=False,
              help="List tracks for each album.")
@click.argument('query', type=str, default='album+')
@click.pass_context
def cmd_beets_albums(context, include_tracks, query):
    '''Show all albums available locally..'''
    calliope.playlist.write(
        calliope.beets.albums(query, include_tracks=include_tracks),
        sys.stdout)


@beets_cli.command(name='artists')
@click.argument('query', type=str, default='artist+')
@click.pass_context
def cmd_beets_artists(context, query):
    '''Show artists stored in Beets database.'''
    calliope.playlist.write(calliope.beets.artists(query), sys.stdout)


@beets_cli.command(name='tracks')
@click.argument('query', type=str, default='artist+ title+')
@click.pass_context
def cmd_beets_tracks(context, query):
    '''Show tracks stored in Beets database.'''
    calliope.playlist.write(calliope.beets.tracks(query), sys.stdout)


#@beets_cli.command(name='resolve-content')
#@click.argument('playlist', type=click.File(mode='r'))
#@click.pass_context
#def cmd_beets_resolve_content(context, playlist):
#    '''Resolve the 'location' field using Beets, if possible.'''
#    output = calliope.beets.resolve_content(calliope.playlist.read(playlist))
#    calliope.playlist.write(output, sys.stdout)



@cli.command(name='diff', help="Compare multiple collections")
@click.option('--scope', 'scope',
              type=click.Choice(['creator', 'album', 'song', 'track']),
              default='track')
@click.argument('playlist1', type=click.File(mode='r'))
@click.argument('playlist2', type=click.File(mode='r'))
@click.pass_context
def cmd_diff(context, scope, playlist1, playlist2):
    equal_function = {
        'creator': calliope.diff.creator_equal,
        'album': calliope.diff.album_equal,
        'song': calliope.diff.song_equal,
        'track': calliope.diff.track_equal,
    }[scope]

    result = calliope.diff.diff(calliope.playlist.read(playlist1),
                                calliope.playlist.read(playlist2),
                                equal_function=equal_function)
    calliope.playlist.write(result, sys.stdout)


EXPORT_FORMATS = ['cue', 'm3u', 'jspf', 'xspf']


@cli.command(name='export')
@click.option('-f', '--format', 'format_', type=click.Choice(EXPORT_FORMATS),
              default='xspf')
@click.option('-t', '--title', type=str,
              help="Set title of playlist")
@click.argument('playlist', nargs=1, type=click.File('r'))
@click.pass_context
def cmd_export(context, format_, title, playlist):
    '''Convert to a different playlist format'''

    format_id = calliope.export.get_format_id(format_)
    result = calliope.export.export_single_playlist(
        calliope.playlist.read(playlist),
        format_id, title=title)
    sys.stdout.write(result)


@cli.command(name='export-split')
@click.option('-f', '--format', 'format_', type=click.Choice(EXPORT_FORMATS),
              default='xspf')
@click.argument('stream', nargs=1, type=click.File('r'))
@click.argument('output_path', nargs=1,
                type=click.Path(file_okay=False, dir_okay=True))
@click.pass_context
def cmd_export_split(context, format_, stream, output_path):
    '''Export multiple playlists from a stream based on `playlist.title`.'''

    format_id = calliope.export.get_format_id(format_)
    calliope.export.export_many_playlists(
        calliope.playlist.split(calliope.playlist.read(stream)),
        format_id, output_path)


@cli.command(name='import')
@click.argument('playlist', nargs=1, type=click.File('r'))
@click.pass_context
def cmd_import(context, playlist):
    """Import playlists from other formats

    Supported formats:

        * pls: Common INI-based playlist format
        * xspf: The XML Shareable Playlist Format
        * jspf: JSON variant of xspf

    """

    text = playlist.read()
    try:
        playlist = calliope.import_.import_(text)
        calliope.playlist.write(playlist, sys.stdout)
    except RuntimeError as e:
        raise RuntimeError(f"{playlist.name}: {e.args[0]}") from e


@cli.group(name='lastfm', help="Interface to the Last.fm music database")
@click.option('--user', metavar='NAME',
              help="show data for the given Last.fm user")
@click.pass_context
def lastfm_cli(context, user):
    if isinstance(calliope.lastfm, calliope.FailedModule):
        raise calliope.lastfm.runtime_error()

    context.obj.lastfm = calliope.lastfm.LastfmContext(config=context.obj.config, user=user)


@lastfm_cli.command(name='annotate-tags')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def lastfm_annotate_tags(context, playlist):
    '''Annotate playlist with tags from Last.fm'''

    context.obj.lastfm.authenticate()
    result_generator = calliope.lastfm.annotate_tags(
        context.obj.lastfm, calliope.playlist.read(playlist))
    calliope.playlist.write(result_generator, sys.stdout)


@lastfm_cli.command(name='similar-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
@click.argument('ARTIST')
def cmd_lastfm_similar_artists(context, count, artist):
    '''Return similar artists for a given artist name.'''

    output = calliope.lastfm.similar_artists(context.obj.lastfm, count,
                                             artist)
    calliope.playlist.write(output, sys.stdout)


@lastfm_cli.command(name='similar-tracks')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of tracks to return")
@click.argument('ARTIST')
@click.argument('TRACK')
def cmd_lastfm_similar_tracks(context, count, artist, track):
    '''Return similar tracks for a given track.'''

    output = calliope.lastfm.similar_tracks(context.obj.lastfm, count,
                                            artist, track)
    calliope.playlist.write(output, sys.stdout)


@lastfm_cli.command(name='top-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
@click.option('--time-range', default='overall',
              type=click.Choice(['overall', '7day', '1month', '3month',
                                 '6month', '12month']))
@click.option('--include', '-i', type=click.Choice(['images']), multiple=True)
def cmd_lastfm_top_artists(context, count, time_range, include):
    '''Return user's top artists.'''

    context.obj.lastfm.authenticate()
    result = calliope.lastfm.top_artists(context.obj.lastfm, count, time_range,
                                         include)
    calliope.playlist.write(result, sys.stdout)


@cli.group(name='lastfm-history',
           help="Scrape and query user's LastFM listening history")
@click.option('--sync/--no-sync', default=True,
              help="update the local copy of the LastFM history")
@click.option('--user', metavar='NAME',
              help="show data for the given Last.fm user")
@click.option('--server', default='last.fm',
              help="Server to fetch track info from, default is last.fm")
@click.option('--retry-on-error/--no-retry-on-error', default=True,
              help="try again if a network error occurs.")
@click.pass_context
def lastfm_history_cli(context, sync, user, server, retry_on_error):
    if not user:
        user = context.obj.config.get('lastfm', 'user')
    if not user:
        raise RuntimeError("Please specify a user. For example: \n\n"
                           "    cpe lastfm-history --user=example COMMAND")

    lastfm_history = calliope.lastfm.history.load(user, server=server,
                                                  retry_on_error=retry_on_error)

    context.obj.lastfm_history = lastfm_history

    if sync:
        sync_operation = lastfm_history.prepare_sync()
        context.obj.maybe_sync = functools.partial(
            sync_operation.run,
            progressbar_stream = sys.stderr,
            progressbar_label = "Updating listens from last.fm server"
        )
    else:
        context.obj.maybe_sync = lambda: None


@lastfm_history_cli.command(name='annotate',
                            help="Annotate a playlist with lastfm listening "
                                 "stats for a user")
@click.argument('playlist', nargs=1, type=click.File('r'))
@click.pass_context
def cmd_lastfm_history_annotate(context, playlist):
    lastfm_history = context.obj.lastfm_history
    context.obj.maybe_sync()

    for item in calliope.playlist.read(playlist):
        result = lastfm_history.annotate(item)
        calliope.playlist.write([result], sys.stdout)


@lastfm_history_cli.command(name='artists',
                            help="Query artists from the listening history")
@click.option('--first-play-before', metavar='DATE',
              help="show artists that were first played before DATE")
@click.option('--first-play-since', metavar='DATE',
              help="show artists that were first played on or after DATE")
@click.option('--last-play-before', metavar='DATE',
              help="show artists that were last played before DATE")
@click.option('--last-play-since', metavar='DATE',
              help="show artists that were last played on or after DATE")
@click.option('--min-listens', default=1, metavar='N',
              help="show only artists that were played N times")
@click.option('--show-listens-since', metavar='DATE',
              help="query the number of listens since the given date")
@click.pass_context
def cmd_lastfm_history_artists(context, first_play_before, first_play_since,
                               last_play_before, last_play_since, min_listens,
                               show_listens_since):
    lastfm_history = context.obj.lastfm_history
    context.obj.maybe_sync()

    cal = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)

    if first_play_before is not None:
        first_play_before = string_to_datetime(cal, first_play_before)
    if first_play_since is not None:
        first_play_since = string_to_datetime(cal, first_play_since)
    if last_play_before is not None:
        last_play_before = string_to_datetime(cal, last_play_before)
    if last_play_since is not None:
        last_play_since = string_to_datetime(cal, last_play_since)

    if show_listens_since is not None:
        show_listens_since = string_to_datetime(cal, show_listens_since)

    artists = lastfm_history.artists(
        first_play_before=first_play_before,
        first_play_since=first_play_since,
        last_play_before=last_play_before,
        last_play_since=last_play_since,
        min_listens=min_listens,
        show_listens_since=show_listens_since)
    calliope.playlist.write(artists, sys.stdout)


@lastfm_history_cli.command(name='listens',
                            help="Export individual listens as a playlist")
@click.pass_context
def cmd_lastfm_history_listens(context):
    lastfm_history = context.obj.lastfm_history
    context.obj.maybe_sync()
    tracks = lastfm_history.listens()
    calliope.playlist.write(tracks, sys.stdout)


@lastfm_history_cli.command(name='scrobbles',
                            help="Export individual listens as a playlist")
@click.pass_context
def cmd_lastfm_history_scrobbles(context):
    cmd_lastfm_history_listens(context)


@lastfm_history_cli.command(name='tracks',
                            help="Query tracks from the listening history")
@click.option('--first-play-before', metavar='DATE',
              help="show tracks that were first played before DATE")
@click.option('--first-play-since', metavar='DATE',
              help="show tracks that were first played on or after DATE")
@click.option('--last-play-before', metavar='DATE',
              help="show tracks that were last played before DATE")
@click.option('--last-play-since', metavar='DATE',
              help="show tracks that were last played on or after DATE")
@click.option('--min-listens', default=1, metavar='N',
              help="show only tracks that were played N times")
@click.option('--show-listens-since', metavar='DATE',
              help="query the number of listens since the given date")
@click.pass_context
def cmd_lastfm_history_tracks(context, first_play_before, first_play_since,
                              last_play_before, last_play_since, min_listens,
                              show_listens_since):
    lastfm_history = context.obj.lastfm_history
    context.obj.maybe_sync()

    cal = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)

    if first_play_before is not None:
        first_play_before = string_to_datetime(cal, first_play_before)
    if first_play_since is not None:
        first_play_since = string_to_datetime(cal, first_play_since)
    if last_play_before is not None:
        last_play_before = string_to_datetime(cal, last_play_before)
    if last_play_since is not None:
        last_play_since = string_to_datetime(cal, last_play_since)

    if show_listens_since is not None:
        show_listens_since = string_to_datetime(cal, show_listens_since)

    tracks = lastfm_history.tracks(
        first_play_before=first_play_before,
        first_play_since=first_play_since,
        last_play_before=last_play_before,
        last_play_since=last_play_since,
        min_listens=min_listens,
        show_listens_since=show_listens_since)
    calliope.playlist.write(tracks, sys.stdout)


@cli.group(name='listenbrainz', help='Query playlists from ListenBrainz')
@click.option('--user', metavar='NAME',
              help="show playlists for the given ListenBrainz user")
@click.pass_context
def listenbrainz_cli(context, user):
    if isinstance(calliope.listenbrainz, calliope.FailedModule):
        raise calliope.listenbrainz.runtime_error()

    if not user:
        user = context.obj.config.get('listenbrainz', 'user')
    if not user:
        raise RuntimeError("Please specify a user. For example: \n\n"
                           "    cpe listenbrainz --user=example COMMAND")
    context.obj.user = user


@listenbrainz_cli.command(name='export')
@click.option('--kind',
              type=click.Choice(['created_by', 'collaborator', 'created_for']),
              default='created_by')
@click.pass_context
def cmd_listenbrainz_export(
    context, kind
):
    '''Export playlists from Listenbrainz.'''
    if kind == 'created_by':
        kind = calliope.listenbrainz.PlaylistQueryType.CREATED_BY
    elif kind == 'collaborator':
        kind = calliope.listenbrainz.PlaylistQueryType.COLLABORATOR
    elif kind == 'created_for':
        kind = calliope.listenbrainz.PlaylistQueryType.CREATED_FOR
    result = calliope.listenbrainz.playlists(
        user=context.obj.user, kind=kind,
    )
    calliope.playlist.write(result, stream=sys.stdout)


@cli.group(name='listenbrainz-history',
           help='Sync and query listen history from ListenBrainz')
@click.option('--sync/--no-sync', default=True,
              help="update the local copy of the ListenBrainz listen history")
@click.option('--user', metavar='NAME',
              help="show listens for the given ListenBrainz user")
@click.pass_context
def listenbrainz_history_cli(context, sync, user):
    if isinstance(calliope.listenbrainz, calliope.FailedModule):
        raise calliope.listenbrainz.runtime_error()

    if not user:
        user = context.obj.config.get('listenbrainz', 'user')
    if not user:
        raise RuntimeError("Please specify a user. For example: \n\n"
                           "    cpe listenbrainz --user=example COMMAND")

    context.obj.history = calliope.listenbrainz.listens.load(user)

    if sync:
        sync_operation = context.obj.history.prepare_sync()
        context.obj.maybe_sync = functools.partial(
            sync_operation.run,
            progressbar_stream = sys.stderr,
            progressbar_label = "Updating listens from Listenbrainz server"
        )
    else:
        context.obj.maybe_sync = lambda: None


@listenbrainz_history_cli.command(name='annotate',
                                  help="Annotate a playlist with Listenbrainz "
                                  "listening stats for a user")
@click.argument('playlist', nargs=1, type=click.File('r'))
@click.pass_context
def cmd_listenbrainz_history_annotate(context, playlist):
    history = context.obj.history
    context.obj.maybe_sync()

    for item in calliope.playlist.read(playlist):
        result = history.annotate(item)
        calliope.playlist.write([result], sys.stdout)


@listenbrainz_history_cli.command(name='artists',
                                  help="Query artists from the listening history")
@click.option('--first-play-before', metavar='DATE',
              help="show artists that were first played before DATE")
@click.option('--first-play-since', metavar='DATE',
              help="show artists that were first played on or after DATE")
@click.option('--last-play-before', metavar='DATE',
              help="show artists that were last played before DATE")
@click.option('--last-play-since', metavar='DATE',
              help="show artists that were last played on or after DATE")
@click.option('--min-listens', default=1, metavar='N',
              help="show only artists that were played N times")
@click.option('--show-listens-since', metavar='DATE',
              help="query the number of listens since the given date")
@click.pass_context
def cmd_listenbrainz_history_artists(
    context, first_play_before, first_play_since, last_play_before,
    last_play_since, min_listens, show_listens_since
):
    history = context.obj.history
    context.obj.maybe_sync()

    cal = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)

    if first_play_before is not None:
        first_play_before = string_to_datetime(cal, first_play_before)
    if first_play_since is not None:
        first_play_since = string_to_datetime(cal, first_play_since)
    if last_play_before is not None:
        last_play_before = string_to_datetime(cal, last_play_before)
    if last_play_since is not None:
        last_play_since = string_to_datetime(cal, last_play_since)

    if show_listens_since is not None:
        show_listens_since = string_to_datetime(cal, show_listens_since)

    artists = history.artists(
        first_play_before=first_play_before,
        first_play_since=first_play_since,
        last_play_before=last_play_before,
        last_play_since=last_play_since,
        min_listens=min_listens,
        show_listens_since=show_listens_since
    )
    calliope.playlist.write(artists, sys.stdout)


@listenbrainz_history_cli.command(name='histogram')
@click.option('--bucket', type=click.Choice(['day', 'week', 'month', 'year']))
@click.pass_context
def cmd_listenbrainz_history_histogram(context, bucket):
    '''Export a histogram of listens.'''
    history = context.obj.history
    context.obj.maybe_sync()

    json.dump(history.histogram(bucket), sys.stdout)



@listenbrainz_history_cli.command(name='listens')
@click.pass_context
def cmd_listenbrainz_history_listens(
    context
):
    '''Export individual listens as a playlist'''
    history = context.obj.history
    context.obj.maybe_sync()

    calliope.playlist.write(history.listens(), sys.stdout)


@listenbrainz_history_cli.command(name='tracks',
                                  help="Query tracks from the listening history")
@click.option('--first-play-before', metavar='DATE',
              help="show tracks that were first played before DATE")
@click.option('--first-play-since', metavar='DATE',
              help="show tracks that were first played on or after DATE")
@click.option('--last-play-before', metavar='DATE',
              help="show tracks that were last played before DATE")
@click.option('--last-play-since', metavar='DATE',
              help="show tracks that were last played on or after DATE")
@click.option('--min-listens', default=1, metavar='N',
              help="show only tracks that were played N times")
@click.option('--show-listens-since', metavar='DATE',
              help="query the number of listens since the given date")
@click.pass_context
def cmd_listenbrainz_history_tracks(
    context, first_play_before, first_play_since, last_play_before,
    last_play_since, min_listens, show_listens_since
):
    history = context.obj.history
    context.obj.maybe_sync()

    cal = parsedatetime.Calendar(version=parsedatetime.VERSION_CONTEXT_STYLE)

    if first_play_before is not None:
        first_play_before = string_to_datetime(cal, first_play_before)
    if first_play_since is not None:
        first_play_since = string_to_datetime(cal, first_play_since)
    if last_play_before is not None:
        last_play_before = string_to_datetime(cal, last_play_before)
    if last_play_since is not None:
        last_play_since = string_to_datetime(cal, last_play_since)

    if show_listens_since is not None:
        show_listens_since = string_to_datetime(cal, show_listens_since)

    tracks = history.tracks(
        first_play_before=first_play_before,
        first_play_since=first_play_since,
        last_play_before=last_play_before,
        last_play_since=last_play_since,
        min_listens=min_listens,
        show_listens_since=show_listens_since
    )
    calliope.playlist.write(tracks, sys.stdout)


@cli.group(name='musicbrainz', help='Query data from Musicbrainz')
@click.pass_context
def musicbrainz_cli(context):
    if isinstance(calliope.musicbrainz, calliope.FailedModule):
        raise calliope.musicbrainz.runtime_error()

    context.obj.musicbrainz = calliope.musicbrainz.MusicbrainzContext(
        context.obj.config
    )


@musicbrainz_cli.command(name='annotate')
@click.argument('playlist', type=click.File(mode='r'))
@click.option('--output', type=click.File(mode='w'), default='-')
@click.option(
    '--include', '-i', type=click.Choice(['areas', 'release', 'urls']), multiple=True
)
@click.option('--update/--no-update', default=False, help='Overwrite track metadata')
@click.option(
    '--interactive/--no-interactive',
    default=False,
    help='Prompt for user input if no perfect matches are found',
)
@click.pass_context
def cmd_musicbrainz_annotate(
    context, playlist, output, include, update, interactive
):
    '''Annotate playlists with data from Musicbrainz'''

    if interactive:
        if getattr(playlist, 'name', '<stdin>') == '<stdin>':
            raise ValueError("No playlist file given (required in interactive mode)")
        if getattr(output, 'name', '<stdout>') == '<stdout>':
            raise ValueError("No --ouput file given (required in interactive mode)")
        select_fun = calliope.resolvers.select_interactive
    else:
        select_fun = calliope.resolvers.select_best

    result_generator = calliope.musicbrainz.annotate(
        context.obj.musicbrainz,
        calliope.playlist.read(playlist),
        include,
        select_fun=select_fun,
        update=update,
    )
    calliope.playlist.write(result_generator, output)


@musicbrainz_cli.command(name='resolve-image')
@click.argument('playlist', type=click.File(mode='r'))
@click.option(
    '--max-size',
    '-s',
    type=click.Choice(['250', '500', 'none']),
    default='250',
    help='set a size limit in pixels for the returned image',
)
@click.pass_context
def cmd_musicbrainz_resolve_image(context, playlist, max_size):
    '''Resolve the 'image' property using the Cover Art API.'''

    result_generator = calliope.musicbrainz.resolve_image(
        context.obj.musicbrainz, calliope.playlist.read(playlist), max_size
    )
    calliope.playlist.write(result_generator, sys.stdout)


@cli.command(name='play')
@click.option('-o', '--output', type=click.Path(), required=True)
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_play(context, output, playlist):
    '''Render a Calliope playlist to an audio file'''

    if isinstance(calliope.play, calliope.FailedModule):
        raise calliope.play.runtime_error_gobject_introspection()

    output_playlist = calliope.play.play(calliope.playlist.read(playlist),
                                         output)

    if output_playlist is not None:
        calliope.playlist.write(output_playlist, sys.stdout)


@cli.command(name='select')
@click.option('--constraint', 'constraints_list', type=str, multiple=True,
              help="A single constraint.")
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_select(context, constraints_list, playlist):
    '''Select tracks from input playlist following a set of constraints.

    Each constraint is defined by a key/value string. Here are some examples:

    \b
       * --constraint=type:playlist-duration,vmin:60m,vmax:120m
       * --constraint=type:fraction-global,prop:tags,values:rock;punk,fraction:0.5

    '''
    if isinstance(calliope.select, calliope.FailedModule):
        raise calliope.select.runtime_error()

    constraints = [calliope.select.constraint_from_string(c)
                   for c in constraints_list]

    try:
        output = calliope.select.select(calliope.playlist.read(playlist), constraints)
    except calliope.select.SelectError as e:
        raise RuntimeError(e) from e
    calliope.playlist.write(output, sys.stdout)


@cli.command(name='shuffle')
@click.option('--count', '-c', type=int, default=None,
              help="number of songs to output")
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_shuffle(context, count, playlist):
    '''Shuffle a playlist or collection.'''

    output = calliope.shuffle.shuffle(calliope.playlist.read(playlist), count)
    calliope.playlist.write(output, sys.stdout)


@cli.group(name='spotify',
           help=f"""
           Interface to the Spotify online streaming service

           \b
           You will need an API key to access Spotify.
           See <{DOC_URL}/getting-data/api-keys.html#spotify>.
           """)
@click.pass_context
def spotify_cli(context):
    if isinstance(calliope.spotify, calliope.FailedModule):
        raise calliope.spotify.runtime_error()

    context.obj.spotify = calliope.spotify.SpotifyContext(context.obj.config)


@spotify_cli.command(name="export")
@click.option(
    "--library",
    type=click.Choice(["track", "album", "artist"]),
    default=None,
    help="Export user library items",
)
@click.pass_context
def cmd_spotify_export(context, library):
    '''Query Spotify authenticated user's playlists'''
    context.obj.spotify.authenticate()
    if library == "track":
        calliope.spotify.export_library_tracks(context.obj.spotify)
    elif library == "album":
        calliope.spotify.export_library_albums(context.obj.spotify)
    elif library == "artist":
        calliope.spotify.export_library_artists(context.obj.spotify)
    elif library is None:
        calliope.spotify.export(context.obj.spotify)
    else:
        raise NotImplementedError(library)


@spotify_cli.command(name="import")
@click.argument("playlist", type=click.File(mode="r"))
@click.option("--library/--no-library", default=False, help="Add items to library")
@click.pass_context
def cmd_spotify_import(context, playlist, library):
    '''Upload one or more playlists to Spotify as authenticated user'''
    context.obj.spotify.authenticate()
    if library:
        calliope.spotify.import_library(
            context.obj.spotify, calliope.playlist.read(playlist)
        )
    else:
        calliope.spotify.import_(context.obj.spotify, calliope.playlist.read(playlist))


@spotify_cli.command(name='resolve')
@click.argument('playlist', type=click.File(mode='r'))
@click.option('--output', type=click.File(mode='w'), default='-')
@click.option('--update/--no-update', default=False, help='Overwrite track metadata')
@click.option(
    '--interactive/--no-interactive',
    default=False,
    help='Prompt for user input if no perfect matches are found',
)
@click.pass_context
def cmd_spotify_resolve(context, playlist, output, update, interactive):
    '''Add Spotify-specific information to tracks in a playlist.'''

    if interactive:
        if getattr(playlist, 'name', '<stdin>') == '<stdin>':
            raise ValueError("No playlist file given (required in interactive mode)")
        if getattr(output, 'name', '<stdout>') == '<stdout>':
            raise ValueError("No --ouput file given (required in interactive mode)")
        select_func = calliope.resolvers.select_interactive
    else:
        select_func = calliope.resolvers.select_best

    context.obj.spotify.authenticate()
    api = context.obj.spotify.api
    result_generator = calliope.spotify.resolve(api,
                                          calliope.playlist.read(playlist),
                                          select_func=select_func,
                                          update=update)
    calliope.playlist.write(result_generator, output)


@spotify_cli.command(name='top-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
@click.option('--time-range', default='long_term',
              type=click.Choice(['short_term', 'medium_term', 'long_term']))
def cmd_spotify_top_artists(context, count, time_range):
    '''Return authenticated user's top artists.'''
    context.obj.spotify.authenticate()
    result = calliope.spotify.top_artists(context.obj.spotify, count, time_range)

    calliope.playlist.write(result, sys.stdout)


@cli.command(name='stat')
@click.option('--size', '-s', is_flag=True,
              help="show the total size on disk of the playlist contents")
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_stat(context, size, playlist):
    '''Information about the contents of a playlist'''

    input_playlist = list(calliope.playlist.read(playlist))

    if size:
        calliope.stat.measure_size(input_playlist)
    else:
        print("Please select a mode.")


@cli.group(name='suggest', help="Suggest items or annotations")
@click.pass_context
def suggest_cli(context):
    pass


@suggest_cli.command(name='tracks')
@click.option('--from', 'from_', required=True, type=click.File(mode='r'),
              help="playlist from which tracks should be suggested")
@click.option('--count', type=int, default=10,
              help="number of track suggestions to generate")
@click.option('--training-input', multiple=True,
              type=(click.File(mode='r'), float),
              help="a playlist used to train the recommender. "
                   "A training input requires two arguments, the first is the "
                   "path to the file, the second is how it should weight the "
                   "training. Weight should be a value between -1.0 and 1.0, "
                   "where 1.0 is the most positive weighting and -1.0 the "
                   "most negative.")
@click.pass_context
def cmd_suggest_tracks(context, from_, count, training_input):
    '''Suggest tracks from a collection based on the given training inputs.'''

    # First we need a 'user-item' interaction matrix. Each 'item' is a track in
    # the input collection. Each 'user' is one of the input playlists.

    corpus_playlist = calliope.playlist.read(from_)
    calliope.suggest.suggest_tracks(corpus_playlist, count, training_input)


@cli.command(name='sync')
@click.option('--dry-run', is_flag=True,
              help="don't execute commands, only print what would be done")
@click.option('--target', '-t', type=click.Path(exists=True, file_okay=False),
              required=True,
              help="path to target device's filesystem")
@click.option('--allow-formats', '-f', type=click.Choice(['all', 'mp3']),
              multiple=True, default=[],
              help="specify formats that the target device can read; "
                   "transcoding can be done if needed.")
@click.option('--album-per-dir', is_flag=True,
              help="organise the files on the target device so each album is "
                   "in its own directory")
@click.option('--number-dirs', is_flag=True,
              help="ensure directory sort order matches desired playback "
                   "order")
@click.option('--number-files', is_flag=True,
              help="ensure filename sort order matches desired playback order")
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_sync(context, dry_run, target, allow_formats, album_per_dir,
             number_dirs, number_files, playlist):
    '''Copy playlists & collections between devices'''
    calliope.sync.sync(dry_run, target, allow_formats, album_per_dir,
                       number_files, number_files,
                       calliope.playlist.read(playlist))


@cli.group(name='tracker', help="Query the Tracker media database")
@click.option('--http-endpoint',
              help="Connect to Tracker Miner FS database over HTTP."
                   "Example: http://my.local.server:8080/sparql")
@click.pass_context
def tracker_cli(context, http_endpoint):
    if isinstance(calliope.tracker, calliope.FailedModule):
        raise calliope.tracker.runtime_error_gobject_introspection()

    context.obj.tracker = calliope.tracker.TrackerClient(
        http_endpoint=http_endpoint
    )


@tracker_cli.command(name='annotate-images')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_tracker_annotate_images(context, playlist):
    '''Add images from the local media-art cache.'''
    output = calliope.tracker.annotate_images(context.obj.tracker, calliope.playlist.read(playlist))
    calliope.playlist.write(output, sys.stdout)


@tracker_cli.command(name='expand-tracks')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_tracker_expand_tracks(context, playlist):
    '''Convert any 'artist' or 'album' type playlist items into 'track' items'''
    result = calliope.tracker.expand_tracks(context.obj.tracker, calliope.playlist.read(playlist))
    calliope.playlist.write(result, sys.stdout)


@tracker_cli.command(name='albums')
@click.option('--artist', nargs=1, type=str,
              help="Limit to albums by the given artist")
@click.option('--include-tracks', is_flag=True, default=False,
              help="List tracks for each album.")
@click.pass_context
def cmd_tracker_albums(context, artist, include_tracks):
    '''Show all albums available locally.'''
    tracker = context.obj.tracker
    if include_tracks:
        result = tracker.tracks_grouped_by_album(filter_artist_name=artist)
    else:
        result = tracker.albums(filter_artist_name=artist)
    calliope.playlist.write(result, sys.stdout)


@tracker_cli.command(name='artists')
@click.pass_context
def cmd_tracker_artists(context):
    '''Show all artists whose music is available locally.'''
    tracker = context.obj.tracker
    calliope.playlist.write(tracker.artists(), sys.stdout)


@tracker_cli.command(name='tracks')
@click.pass_context
def cmd_tracker_tracks(context):
    '''Show all tracks available locally.'''
    tracker = context.obj.tracker
    calliope.playlist.write(tracker.tracks(), sys.stdout)


@tracker_cli.command(name='resolve-content')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_tracker_resolve_content(context, playlist):
    '''Resolve the 'location' field using Tracker, if possible.'''
    output = calliope.tracker.resolve_content(context.obj.tracker, calliope.playlist.read(playlist))
    calliope.playlist.write(output, sys.stdout)


@tracker_cli.command(name='resolve-image')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_tracker_resolve_image(context, playlist):
    '''Resolve 'image' property using the local media-art cache.'''
    output = calliope.tracker.resolve_image(context.obj.tracker, calliope.playlist.read(playlist))
    calliope.playlist.write(output, sys.stdout)


@tracker_cli.command(name='search')
@click.argument('text', nargs=1, type=str)
@click.pass_context
def cmd_tracker_search(context, text):
    '''Search for tracks in the Tracker database matching 'text'.

    Append '*' to enable partial matching of a search term.'''
    tracker = context.obj.tracker
    calliope.playlist.write(tracker.search(search_text=text), sys.stdout)


@tracker_cli.command(name='top-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
def cmd_tracker_top_artists(context, count):
    '''Query the top artists in a Tracker database'''
    tracker = context.obj.tracker
    result = list(tracker.artists_by_number_of_songs(limit=count))
    calliope.playlist.write(result, sys.stdout)


@cli.command(name='validate')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_validate(context, playlist):
    '''Validate a Calliope playlist stream.'''
    for item in calliope.playlist.read(playlist):
        calliope.validate.validate(item)
        calliope.playlist.write([item], sys.stdout)


@cli.group(name='youtube',
           help="Interface to the Youtube online streaming service")
@click.option('--client-secrets', type=click.File(mode='r'),
              help="Credentials file from Google developer console")
@click.pass_context
def youtube_cli(context, client_secrets):
    if isinstance(calliope.youtube, calliope.FailedModule):
        raise calliope.youtube.runtime_error()

    context.obj.youtube = calliope.youtube.YoutubeContext(
        config=context.obj.config)


@youtube_cli.command(name='export')
@click.argument('username', type=str)
@click.pass_context
def cmd_youtube_export(context, username):
    '''Query user playlists from Youtube'''
    api = context.obj.youtube.authenticate()
    channel_id = calliope.youtube.get_channel_id(api, username)
    result = calliope.youtube.export(api, channel_id)
    calliope.playlist.write(result, sys.stdout)
