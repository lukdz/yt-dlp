import math
import re

from .common import InfoExtractor
from ..compat import (
    compat_urllib_parse_urlparse,
    compat_parse_qs,
)
from ..utils import (
    format_field,
    InAdvancePagedList,
    traverse_obj,
    unified_timestamp,
    ExtractorError,
)
from ..networking.exceptions import HTTPError


class BanByeBaseIE(InfoExtractor):
    _API_BASE = 'https://api.banbye.com'
    _CDN_BASE = 'https://cdn.banbye.com'
    _TC2_BASE = 'https://tc2.banbye.com:31001'
    _VIDEO_BASE = 'https://banbye.com/watch'

    @staticmethod
    def _extract_playlist_id(url, param='playlist'):
        return compat_parse_qs(
            compat_urllib_parse_urlparse(url).query).get(param, [None])[0]

    def _extract_playlist(self, playlist_id):
        data = self._download_json(f'{self._API_BASE}/playlists/{playlist_id}', playlist_id)
        return self.playlist_result([
            self.url_result(f'{self._VIDEO_BASE}/{video_id}', BanByeIE)
            for video_id in data['videoIds']], playlist_id, data.get('name'))


class BanByeIE(BanByeBaseIE):
    _VALID_URL = r'https?://(?:www\.)?banbye\.com/(?:en/)?watch/(?P<id>[\w-]+)'
    _TESTS = [{
        'url': 'https://banbye.com/watch/v_ytfmvkVYLE8T',
        'md5': '2f4ea15c5ca259a73d909b2cfd558eb5',
        'info_dict': {
            'id': 'v_ytfmvkVYLE8T',
            'ext': 'mp4',
            'title': 'md5:5ec098f88a0d796f987648de6322ba0f',
            'description': 'md5:4d94836e73396bc18ef1fa0f43e5a63a',
            'uploader': 'wRealu24',
            'channel_id': 'ch_wrealu24',
            'channel_url': 'https://banbye.com/channel/ch_wrealu24',
            'timestamp': 1647604800,
            'upload_date': '20220318',
            'duration': 1931,
            'thumbnail': r're:https?://.*\.webp',
            'tags': 'count:5',
            'like_count': int,
            'dislike_count': int,
            'view_count': int,
            'comment_count': int,
        },
    }, {
        'url': 'https://banbye.com/watch/v_2JjQtqjKUE_F?playlistId=p_Ld82N6gBw_OJ',
        'info_dict': {
            'title': 'Krzysztof Karoń',
            'id': 'p_Ld82N6gBw_OJ',
        },
        'playlist_mincount': 9,
    }, {
        'url': 'https://banbye.com/watch/v_kb6_o1Kyq-CD',
        'info_dict': {
            'id': 'v_kb6_o1Kyq-CD',
            'ext': 'mp4',
            'title': 'Co tak naprawdę dzieje się we Francji?! Czy Warszawa a potem cała Polska będzie drugim Paryżem?!🤔🇵🇱',
            'description': 'md5:82be4c0e13eae8ea1ca8b9f2e07226a8',
            'uploader': 'Marcin Rola - MOIM ZDANIEM!🇵🇱',
            'channel_id': 'ch_QgWnHvDG2fo5',
            'channel_url': 'https://banbye.com/channel/ch_QgWnHvDG2fo5',
            'duration': 597,
            'timestamp': 1688642656,
            'upload_date': '20230706',
            'thumbnail': 'https://cdn.banbye.com/video/v_kb6_o1Kyq-CD/96.webp',
            'tags': ['Paryż', 'Francja', 'Polska', 'Imigranci', 'Morawiecki', 'Tusk'],
            'like_count': int,
            'dislike_count': int,
            'view_count': int,
            'comment_count': int,
        },
    }, {
        'url': 'https://banbye.com/watch/v_scCsSgH5SAVx',
        'info_dict': {
            'id': 'v_scCsSgH5SAVx',
            'ext': 'mp4',
            'title': 'Braun OSTRO u Roli o wpychaniu Polski w wojnę, Hołowni, Tusku, Putinie, Rolnikach, Zełenskim i Konfie?! TELEFONY NA ŻYWO',
            'description': 'md5:27608a0f8ebba7eea9bdda4058221570',
            'uploader': 'wRealu24',
            'channel_id': 'ch_wrealu24',
            'channel_url': 'https://banbye.com/channel/ch_wrealu24',
            'duration': 4320.000000000072,
            'timestamp': 1709306481,
            'upload_date': '20240301',
            'thumbnail': 'https://cdn.banbye.com/video/v_scCsSgH5SAVx/96.webp',
            'tags': ['braun', 'tusk', 'zalenski', 'putin', 'konfederacja', 'rola'],
            'like_count': int,
            'dislike_count': int,
            'view_count': int,
            'comment_count': int,
        },
    }, {
        'url': 'https://banbye.com/watch/v_y6ZwvWi4vpyy',
        'info_dict': {
            'id': 'v_y6ZwvWi4vpyy',
            'ext': 'mp4',
            'title': 'Najbardziej zapomniany polski pisarz? Przywracamy pamięć o nim!',
            'description': 'md5:acb14057105ab4029f69fd3e175d36ec',
            'uploader': 'Multibook.pl - księgarnia inna niż wszystkie!',
            'channel_id': 'ch__ViawXqgYNgT',
            'channel_url': 'https://banbye.com/channel/ch__ViawXqgYNgT',
            'duration': 893,
            'timestamp': 1709108848,
            'upload_date': '20240228',
            'thumbnail': 'https://cdn.banbye.com/video/v_y6ZwvWi4vpyy/96.webp',
            'tags': ['pisarz', 'zapomniany', 'jeske', 'multibookpl', 'XXwiek'],
            'like_count': int,
            'dislike_count': int,
            'view_count': int,
            'comment_count': int,
        },
    }, {
        'url': 'https://banbye.com/watch/v_07E6K63jqwJh',
        'info_dict': {
            'id': 'v_07E6K63jqwJh',
            'ext': 'mp4',
            'title': 'Afera w Niemczech - Rosjanie podsłuchiwali Luftwaffe - komentuje kpt. Maciej Lisowski | Najważniejsze Pytania',
            'description': None,
            'uploader': 'TVMN',
            'channel_id': 'ch_orZUyrBUJn0p',
            'channel_url': 'https://banbye.com/channel/ch_orZUyrBUJn0p',
            'duration': 1226,
            'timestamp': 1709566006,
            'upload_date': '20240304',
            'thumbnail': 'https://cdn.banbye.com/video/v_07E6K63jqwJh/96.webp',
            'tags': ['niemcy', 'scholz', 'rosja', 'putin', 'podsłuch', 'ukraina'],
            'like_count': int,
            'dislike_count': int,
            'view_count': int,
            'comment_count': int,
        },
    }, {
        'url': 'https://banbye.com/watch/v_n9NLZTijHIy9',
        'info_dict': {
            'id': 'v_n9NLZTijHIy9',
            'ext': 'mp4',
            'title': 'Banderyzacja i drożyzna - PRAWDZIWA twarz UŚMIECHNIĘTEJ POLSKI! Dominik Cwikła vlog',
            'description': 'md5:2db15f461aabf74ae7c9ad63450085a8',
            'uploader': 'wRealu24',
            'channel_id': 'ch_wrealu24',
            'channel_url': 'https://banbye.com/channel/ch_wrealu24',
            'duration': 653,
            'timestamp': 1709578811,
            'upload_date': '20240304',
            'thumbnail': 'https://cdn.banbye.com/video/v_n9NLZTijHIy9/96.webp',
            'tags': ['polska', 'banderyzacja', 'drozyzna', 'zukowska', 'ukraina', 'cwikla'],
            'like_count': int,
            'dislike_count': int,
            'view_count': int,
            'comment_count': int,
        },
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        playlist_id = self._extract_playlist_id(url, 'playlistId')

        if self._yes_playlist(playlist_id, video_id):
            return self._extract_playlist(playlist_id)

        data = self._download_json(f'{self._API_BASE}/videos/{video_id}', video_id)

        pattern_list = [
            r'livestreamId:"(?P<id>[^"]+)"',
            r'{video:{_id:"(?P<id>[^"]+)"',
        ]
        webpage_content = self._download_webpage(url, video_id)
        for pattern in pattern_list:
            match_obj = re.search(pattern, webpage_content)
            if match_obj:
                m3u8_id = match_obj.groupdict().get('id')
                break

        url_functions = [
            lambda quality: f'{self._TC2_BASE}/live/hls/{m3u8_id}_{quality}/index.m3u8',
            lambda quality: f'{self._TC2_BASE}/edge/video/{m3u8_id}/v/index_{quality}/index.m3u8',
        ]
        for function in url_functions:
            try:
                url = function(data['quality'][0])
                self._download_webpage(url, video_id, note="Checking " + url)
            except ExtractorError as err:
                if isinstance(err.cause, HTTPError) and (err.cause.status == 404):
                    self.to_screen('%s, switching to next format' % err.cause.reason)
                else:
                    raise
            else:
                self.to_screen("Found")
                url_function = function
                protocol = 'm3u8_native'
                break
        else:
            url_function = lambda quality: f'{self._CDN_BASE}/video/{video_id}/{quality}.mp4'
            protocol = 'https'

        thumbnails = [{
            'id': f'{quality}p',
            'url': f'{self._CDN_BASE}/video/{video_id}/{quality}.webp',
        } for quality in [48, 96, 144, 240, 512, 1080]]
        formats = [{
            'format_id': f'http-{quality}p',
            'quality': quality,
            'url': url_function(quality),
            'protocol': protocol,
            'ext': 'mp4',
        } for quality in data['quality']]

        return {
            'id': video_id,
            'title': data.get('title'),
            'description': data.get('desc'),
            'uploader': traverse_obj(data, ('channel', 'name')),
            'channel_id': data.get('channelId'),
            'channel_url': format_field(data, 'channelId', 'https://banbye.com/channel/%s'),
            'timestamp': unified_timestamp(data.get('publishedAt')),
            'duration': data.get('duration'),
            'tags': data.get('tags'),
            'formats': formats,
            'thumbnails': thumbnails,
            'like_count': data.get('likes'),
            'dislike_count': data.get('dislikes'),
            'view_count': data.get('views'),
            'comment_count': data.get('commentCount'),
        }


class BanByeChannelIE(BanByeBaseIE):
    _VALID_URL = r'https?://(?:www\.)?banbye\.com/(?:en/)?channel/(?P<id>\w+)'
    _TESTS = [{
        'url': 'https://banbye.com/channel/ch_wrealu24',
        'info_dict': {
            'title': 'wRealu24',
            'id': 'ch_wrealu24',
            'description': 'md5:da54e48416b74dfdde20a04867c0c2f6',
        },
        'playlist_mincount': 791,
    }, {
        'url': 'https://banbye.com/channel/ch_wrealu24?playlist=p_Ld82N6gBw_OJ',
        'info_dict': {
            'title': 'Krzysztof Karoń',
            'id': 'p_Ld82N6gBw_OJ',
        },
        'playlist_count': 9,
    }]
    _PAGE_SIZE = 100

    def _real_extract(self, url):
        channel_id = self._match_id(url)
        playlist_id = self._extract_playlist_id(url)

        if playlist_id:
            return self._extract_playlist(playlist_id)

        def page_func(page_num):
            data = self._download_json(f'{self._API_BASE}/videos', channel_id, query={
                'channelId': channel_id,
                'sort': 'new',
                'limit': self._PAGE_SIZE,
                'offset': page_num * self._PAGE_SIZE,
            }, note=f'Downloading page {page_num + 1}')
            return [
                self.url_result(f"{self._VIDEO_BASE}/{video['_id']}", BanByeIE)
                for video in data['items']
            ]

        channel_data = self._download_json(f'{self._API_BASE}/channels/{channel_id}', channel_id)
        entries = InAdvancePagedList(
            page_func,
            math.ceil(channel_data['videoCount'] / self._PAGE_SIZE),
            self._PAGE_SIZE)

        return self.playlist_result(
            entries, channel_id, channel_data.get('name'), channel_data.get('description'))
