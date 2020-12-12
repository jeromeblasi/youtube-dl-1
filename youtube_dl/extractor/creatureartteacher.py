# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from .vimeo import VimeoIE
from ..utils import (
    unsmuggle_url,
    unescapeHTML,
    std_headers,
    merge_dicts
)
import re
import json


class CreatureArtTeacherIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?creatureartteacher\.com/course/(?P<playlist_id>[0-9a-z-]+)'
    url_node = "https://creatureartteacher.com/lesson/%s"

    _TEST = {
        'url': 'https://creatureartteacher.com/course/sculpting-in-zbrush-with-tony-cipriano-streaming/',
        # 'md5': 'TODO: md5 sum of the first 10241 bytes of the video file (use --test)',
        'info_dict': {
            'id': 'sculpting-in-zbrush-with-tony-cipriano-streaming',
            'ext': 'mp4',
            'title': 'sculpting-in-zbrush-with-tony-cipriano-streaming',
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
        playlist_id = mobj.group('playlist_id')
        webpage = self._download_webpage(url, playlist_id)
        # playlist info
        playlist_lessons_infos = []
        for playlist_lesson_infos in re.finditer(r'<header class="lesson-title".*\s*.*<h2>.*\s*.*<a.*\s*.*href=\"(?P<lesson_url>.*)\".*\s.*title=\"(?P<lesson_title>.*)\"', webpage):
            lesson_title = playlist_lesson_infos.group('lesson_title')
            lesson_url = playlist_lesson_infos.group('lesson_url')
            playlist_lessons_infos.append({
                'url': lesson_url,
                'id': lesson_title,
                'title': lesson_title
            })

        # lessons urls (vimeo)
        lessons_vids_urls = []

        for lesson in playlist_lessons_infos:
            lesson_url = lesson['url']
            lesson_title = lesson['title']
            # TODO check if this actually do the job : vimeo_urls = VimeoIE._extract_urls(lesson_url, lesson_webpage)
            lesson_webpage = self._download_webpage(lesson_url, playlist_id)
            reg = r'<iframe[^>]+?src=["|\'](?P<url_base>.*?\/\/player\.vimeo\.com\/video\/)(?P<player_video_id>\d+)'
            # note for reg : url is valid with or without 'http'

            player_video_url_base = self._html_search_regex(reg, lesson_webpage, 'player_video_url_base', group='url_base').strip()

            # ID extract from vimeo URL
            player_video_url_id = self._html_search_regex(reg, lesson_webpage, 'player_video_url_id', group='player_video_id').strip()
            player_video_url = player_video_url_base + player_video_url_id

            # TODO check usefulness of this block
            player_video_url_id, data = unsmuggle_url(player_video_url_id, {})
            headers = std_headers.copy()
            if 'http_headers' in data:
                headers.update(data['http_headers'])

            # webpage extract (embeded video) from url (vimeo)
            embedded_video_webpage, urlh = self._download_webpage_handle(player_video_url, player_video_url_id, headers=headers)

            # config extraction
            self.report_extraction(player_video_url_id)
            config_re = [r' = {config:({.+?}),assets:', r'(?:[abc])=({.+?});']
            config_re.append(r'\bvar\s+r\s*=\s*({.+?})\s*;')
            config_re.append(r'\bconfig\s*=\s*({.+?})\s*;')
            config = self._search_regex(config_re, embedded_video_webpage, 'info section',
                                        flags=re.DOTALL)
            config = json.loads(config)
            config = VimeoIE._parse_config(self, config, player_video_url_id)

            # building list of config (dict)
            lessons_vids_urls.append(config)

        return self.playlist_result(lessons_vids_urls, playlist_id)

        # direct

        # find .mp4 from embedded webpage
        #     directURLs = {}
        #     for itemid in re.finditer(r'(?P<directURL>https:\/\/vod.*?\.mp4)".*?quality":"(?P<quality>[0-9]+).*?id":"(?P<vid_id>.*?)"', embedded_video_webpage):
        #         directURL = itemid.group('directURL')
        #         quality = int(itemid.group('quality'))
        #         directURLs.update({directURL: quality})
        #     best_quality_URL = max(directURLs, key=directURLs.get)

        #     lessons_vids_urls.append({
        #         'url_player': player_video_url,
        #         'id': player_video_url_id,
        #         'url': player_video_url,  # best_quality_URL,
        #         'playlist_id': playlist_id,
        #         'title': lesson_title,
        #         'lesson_url': lesson_url
        #     })
        # return self.playlist_result(lessons_vids_urls, playlist_id)

        # lesson_vids_urls.append(VimeoIE._smuggle_referrer(unescapeHTML(item.group('url')), lesson_url))

        # for item in re.finditer(r'<iframe[^>]+?src=(["\'])(?P<url_base>(?:https?:)?\/\/player\.vimeo\.com\/video\/)(?P<video_player_id>\d+.*?)\1', lesson_webpage):
        #player_video_url = item.group('url_base') + item.group('video_player_id')

        # video_player_id = item.group('video_player_id')  # self._match_id(lesson_url_player)
