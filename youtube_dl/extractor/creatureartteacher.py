# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from .vimeo import VimeoIE
from ..utils import (
    unsmuggle_url,
    std_headers,
)
import re
import json


class CreatureArtTeacherIE(InfoExtractor):
    # subscription mandatory : use --cookies FILE option for authentication
    _VALID_URL = r'https?://(?:www\.)?creatureartteacher\.com/course/(?P<playlist_id>[0-9a-z-]+)'
    _TEST = {
        'url': 'https://creatureartteacher.com/course/sculpting-in-zbrush-with-tony-cipriano-streaming/',
        'info_dict': {
            'url': r're:https://vod.*?\.mp4',
            'id': '452840422',
            'title': '01 Lets get Started in ZBrush',
            'uploader': 'Aaron Blaise',
            'uploader_id': 'aaronblaiseart',
            'ext': 'mp4'
        },
        'params': {
            'skip_download': True,
            'cookiefile': '/',  # /PATH/cookies.txt'
            'format': 'http-1080p',
            'allsubtitles': True,
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        playlist_id = mobj.group('playlist_id')
        webpage = self._download_webpage(url, playlist_id)
        # playlist info
        playlist_lessons_infos = []
        for playlist_lesson_infos in re.finditer(r'<header class=["\']lesson-title["\'].*\s*<h2>.*\s*<a[^>]+href=["\'](?P<lesson_url>[^"\']+)', webpage):
            lesson_url = playlist_lesson_infos.group('lesson_url')
            playlist_lessons_infos.append({
                'url': lesson_url,
            })

        # lessons urls (vimeo)
        lessons_vids_urls = []

        for lesson in playlist_lessons_infos:
            lesson_webpage = self._download_webpage(lesson.get('url'), playlist_id)

            # Extract url
            vimeo_url = VimeoIE._extract_urls(lesson_url, lesson_webpage)
            player_video_url = vimeo_url[0]
            vimeo_url_unsmuggle, data = unsmuggle_url(player_video_url, {})
            player_video_url = vimeo_url_unsmuggle

            # ID extract from vimeo URL
            player_video_url_id = self._search_regex(r'\/\/player\.vimeo\.com\/video\/(?P<player_video_id>\d+)', player_video_url, 'player_video_url_id', group='player_video_id').strip()

            # Headers referer checking
            headers = std_headers.copy()
            if 'Referer' not in headers:
                headers['Referer'] = "https://creatureartteacher.com"

            # webpage extract (embeded video) from url (vimeo)
            embedded_video_webpage, urlh = self._download_webpage_handle(player_video_url, player_video_url_id, headers=headers)

            # config extraction
            config = self._search_regex(r'\bconfig\s*=\s*({.+?})\s*;', embedded_video_webpage, 'info section')
            config = json.loads(config)
            config = VimeoIE._parse_config(self, config, player_video_url_id)

            # building list of config (dict)
            lessons_vids_urls.append(config)

        return self.playlist_result(lessons_vids_urls, playlist_id)
