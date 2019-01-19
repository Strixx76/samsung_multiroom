"""DLNA service player."""
from ..player import Player
from ..player import Track
from ..player import init_track_kwargs


class DlnaPlayer(Player):
    """Controls player in WIFI+DLNA mode."""

    def __init__(self, api):
        self._api = api

    def play(self, playlist):
        """
        Enqueue and play a playlist.

        Playlist items must be an object with following attributes:
        - object_id - object id
        - object_type - must be 'dlna_audio'
        - title - track title
        - artist - track artist
        - thumbnail_url - thumbnail URL
        - device_udn - DLNA device UDN

        :param playlist: Iterable returning player combatible objects
        :returns: True if playlist was accepted, False otherwise
        """
        items = []
        for track in playlist:
            if track.object_type not in ['dlna_audio']:
                continue

            items.append({
                'object_id': track.object_id,
                'title': track.title,
                'artist': track.artist,
                'thumbnail': track.thumbnail_url,
                'device_udn': track.device_udn,
            })

        if items:
            self._api.set_playlist_playback_control(items)
            return True

        return False

    def jump(self, time):
        """
        Advance current playback to specific time.

        :param time: Time from the beginning of the track in seconds
        """
        self._api.set_search_time(time)

    def resume(self):
        """Play/resume current track."""
        self._api.set_playback_control('resume')

    def stop(self):
        """Stop current track and reset position to the beginning."""
        raise NotImplementedError()

    def pause(self):
        """Pause current track and retain position."""
        self._api.set_playback_control('pause')

    def next(self):
        """Play next track in the queue."""
        self._api.set_trick_mode('next')

    def previous(self):
        """Play previous track in the queue."""
        self._api.set_trick_mode('previous')

    def get_current_track(self):
        """
        Get current track info.

        :returns: Track instance, or None if unavailable
        """
        music_info = self._api.get_music_info()

        track_kwargs = init_track_kwargs('dlna_audio')

        if 'title' in music_info:
            track_kwargs['title'] = music_info['title']
        if 'artist' in music_info:
            track_kwargs['artist'] = music_info['artist']
        if 'album' in music_info:
            track_kwargs['album'] = music_info['album']
        if 'thumbnail' in music_info and 'http' in music_info['thumbnail']:
            track_kwargs['thumbnail_url'] = music_info['thumbnail']
        if 'timelength' in music_info and music_info['timelength'] is not None:
            (hours, minutes, seconds) = music_info['timelength'].split(':')
            track_kwargs['duration'] = int(hours) * 3600 + int(minutes) * 60 + int(float(seconds))
        if 'playtime' in music_info:
            track_kwargs['position'] = int(int(music_info['playtime']) / 1000)
        if 'device_udn' in music_info:
            track_kwargs['metadata']['device_udn'] = music_info['device_udn']
        if 'objectid' in music_info:
            track_kwargs['metadata']['object_id'] = music_info['objectid']

        return Track(**track_kwargs)

    def is_supported(self, function, submode=None):
        """
        Check if this player supports function/submode.

        :returns: Boolean True if function/submode is supported
        """
        return function == 'wifi' and submode == 'dlna'