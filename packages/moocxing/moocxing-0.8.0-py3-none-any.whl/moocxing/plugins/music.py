import requests
import os
import random
import ffmpeg

from moocxing.robot import Constants
from moocxing.plugins.sdk.AbstractPlugin import AbstractPlugin
from moocxing.robot import Config

class Plugin(AbstractPlugin):
    SLUG = "music"

    def _getMusicId(self, keyword):
        url = f"{Config.get('netease/baseUrl')}/search?keywords={keyword}"
        res = requests.get(url)
        return res.json()["result"]["songs"][0]["id"]

    def getMusicRankings(self):
        url = f"{Config.get('netease/baseUrl')}/personalized/newsong"
        res = requests.get(url)
        return res.json()["result"][random.randint(0, 9)]["id"]

    def getMusicUrl(self, keyword):
        url = f"{Config.get('netease/baseUrl')}/song/url?id={self._getMusicId(keyword)}" 
        res = requests.get(url)
        return res.json()["data"][0]["url"]

    def downMusic(self, keyword):
        try:
            if keyword == "":
                keyword = self.getMusicRankings()
            musicUrl = self.getMusicUrl(keyword)
        except:
            keyword = self.getMusicRankings()
            musicUrl = self.getMusicUrl(keyword)

        os.system(f"curl -so  {Constants.TEMP_PATH}music.mp3 {musicUrl}")

        ffmpeg.run(ffmpeg.output(ffmpeg.input(Constants.TEMP_PATH + 'music.mp3'), Constants.TEMP_PATH + 'music.wav'), quiet=True, overwrite_output=True)

    def handle(self, query):
        try:
            musicName = self.nlp.getMusicName(query)
            self.say(f"正在为你准备{musicName}")
            self.downMusic(musicName)
            self.playThread("music.wav")
        except:
            pass

    def isValid(self, query):
        return any(word in query for word in ["听", "播放", "首", "歌"])
