# -*- coding: utf-8 -*-
"""
我的音乐 · TVBox 音乐源（按歌手分类）
  数据：https://raw.githubusercontent.com/zxsla/yingyue/main/music/music.json
  功能：歌手分类 / 封面显示 / 歌词显示 / MV播放
"""
import json
import sys
sys.path.append('..')
try:
    from base.spider import Spider as BaseSpider
except:
    class BaseSpider: pass

MUSIC_JSON = 'https://raw.githubusercontent.com/zxsla/yingyue/main/music/music.json'

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

    def homeContent(self, filter):
        d = self.load()
        classes = [{'type_id': s['name'], 'type_name': f"🎤{s['name']} ({len(s['songs'])}首)"}
                   for s in d.get('singers', [])]
        return {'class': classes}

    def categoryContent(self, tid, pg, filter, extend):
        d = self.load()
        lst = []
        for s in d.get('singers', []):
            if s['name'] == tid:
                for i, song in enumerate(s['songs']):
                    tag = '🎬MV' if song.get('type') == 'mv' else '🎵'
                    lst.append({
                        'vod_id': f"{tid}@@{i}",
                        'vod_name': f"{tag} {song['name']}",
                        'vod_pic': song.get('pic', ''),
                        'vod_remarks': s['name'],
                    })
                break
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
                # 歌词地址存到 vod_content 供播放器读取
                if song.get('lyric'):
                    vod['vod_content'] += f"\n歌词：{song['lyric']}"
                return {'list': [vod]}
        return {'list': []}

    def searchContent(self, key, quick, pg='1'):
        d = self.load()
        out = []
        for s in d.get('singers', []):
            for i, song in enumerate(s['songs']):
                if key.lower() in song['name'].lower() or key.lower() in s['name'].lower():
                    tag = '🎬MV' if song.get('type') == 'mv' else '🎵'
                    out.append({
                        'vod_id': f"{s['name']}@@{i}",
                        'vod_name': f"{tag} {song['name']} - {s['name']}",
                        'vod_pic': song.get('pic', ''),
                        'vod_remarks': s['name'],
                    })
        return {'list': out}

    def playerContent(self, flag, id, vipFlags):
        # id 是直链，直接播放；YouTube 链接走解析
        if 'youtu.be' in id or 'youtube.com' in id:
            return {'parse': 1, 'url': id}
        return {'parse': 0, 'url': id}

    def isVideoFormat(self, url):
        return True
    def manualVideoCheck(self): pass
    def localProxy(self, param): return None
    def liveContent(self, url): return ''
