# -*- coding: utf-8 -*-
"""
我的音乐 · TVBox 音乐源（全部歌曲单列表）
  数据：https://raw.githubusercontent.com/zxsla/yingyue/main/music.json
  功能：单列表 / 封面显示 / 歌词显示 / MV播放 / 搜索
"""
import sys
try:
    from base.spider import Spider as BaseSpider
except:
    class BaseSpider: pass

MUSIC_JSON = 'https://raw.githubusercontent.com/zxsla/yingyue/main/music.json'

class Spider(BaseSpider):
    def getName(self):
        return '我的音乐'

    def init(self, extend=''):
        self.data = None

    def load(self):
        if self.data is None:
            try:
                r = self.fetch(MUSIC_JSON, timeout=15)
                self.data = r.json()
            except Exception:
                self.data = {'singers': []}
        return self.data

    def all_songs(self):
        d = self.load()
        out = []
        for s in d.get('singers', []):
            for i, song in enumerate(s['songs']):
                out.append((s['name'], i, song))
        return out

    def homeContent(self, filter):
        total = len(self.all_songs())
        return {'class': [{'type_id': 'all', 'type_name': f'🎵全部歌曲({total}首)'}]}

    def categoryContent(self, tid, pg, filter, extend):
        lst = []
        for singer, i, song in self.all_songs():
            tag = '🎬' if song.get('type') == 'mv' else '🎵'
            lst.append({
                'vod_id': f'{singer}@@{i}',
                'vod_name': f'{tag} {song["name"]}',
                'vod_pic': song.get('pic', ''),
                'vod_remarks': singer,
            })
        return {'list': lst, 'page': 1, 'pagecount': 1, 'limit': 99, 'total': len(lst)}

    def detailContent(self, ids):
        tid, idx = ids[0].split('@@')
        d = self.load()
        for s in d.get('singers', []):
            if s['name'] == tid:
                song = s['songs'][int(idx)]
                vod = {
                    'vod_id': ids[0],
                    'vod_name': song['name'],
                    'vod_pic': song.get('pic', ''),
                    'vod_remarks': s['name'],
                    'vod_content': f"歌手：{s['name']}",
                    'vod_play_from': '播放',
                    'vod_play_url': f"播放${song['url']}",
                }
                if song.get('lyric'):
                    vod['vod_content'] += f"\n歌词：{song['lyric']}"
                return {'list': [vod]}
        return {'list': []}

    def searchContent(self, key, quick, pg='1'):
        out = []
        for singer, i, song in self.all_songs():
            if key.lower() in song['name'].lower() or key.lower() in singer.lower():
                tag = '🎬' if song.get('type') == 'mv' else '🎵'
                out.append({
                    'vod_id': f'{singer}@@{i}',
                    'vod_name': f'{tag} {song["name"]} - {singer}',
                    'vod_pic': song.get('pic', ''),
                    'vod_remarks': singer,
                })
        return {'list': out}

    def playerContent(self, flag, id, vipFlags):
        if 'youtu.be' in id or 'youtube.com' in id:
            return {'parse': 1, 'url': id}
        return {'parse': 0, 'url': id}

    def isVideoFormat(self, url):
        return True
    def manualVideoCheck(self): pass
    def localProxy(self, param): return None
    def liveContent(self, url): return ''
