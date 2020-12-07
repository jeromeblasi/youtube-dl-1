# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
import re


class CreatureArtTeacherIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?creatureartteacher\.com/lesson/(?P<id>[0-9a-z-]+)'
    # https://creatureartteacher.com/lesson/01-getting-started-in-zbrush-streaming/
    #_VALID_URL = r'https?://(?:www\.)?creatureartteacher\.com/course/(?P<id>[0-9a-z-]+)'
    # r'https?://(?:www\.)?creatureartteacher\.com/course/page/[0-9]+'
    # https://creatureartteacher.com/course/page/1
    _TEST = {
        'url': 'https://creatureartteacher.com/lesson/',
        # 'md5': 'TODO: md5 sum of the first 10241 bytes of the video file (use --test)',
        'info_dict': {
            'id': '01-getting-started-in-zbrush-streaming',
            'ext': 'mp4',
            'title': '01-getting-started-in-zbrush-streaming',
            # 'thumbnail': r're:^https?://.*\.jpg$',
            # TODO more properties, either as:
            # * A value
            # * MD5 checksum; start the string with md5:
            # * A regular expression; start the string with re:
            # * Any Python type (for example int or float)
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        webpage = self._download_webpage(url, video_id)

        # TODO more code goes here, for example ...
        title = self._html_search_regex(r'<title>(.+?)</title>', webpage, 'title')

        return {
            'id': video_id,
            'title': title,
            # 'description': self._og_search_description(webpage),
            # 'uploader': self._search_regex(r'<div[^>]+id="uploader"[^>]*>([^<]+)<', webpage, 'uploader', fatal=False),
            # TODO more properties (see youtube_dl/extractor/common.py)
        }
