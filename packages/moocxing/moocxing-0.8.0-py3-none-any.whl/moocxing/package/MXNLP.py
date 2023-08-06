import requests
import json
from moocxing.robot import Config
import logging

log = logging.getLogger(__name__)


class MXNLP:
    def __init__(self, API_KEY, SECRET_KEY):
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.token = self.__getToken()

    def __getToken(self):
        """获取token"""
        url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + \
              self.API_KEY + '&client_secret=' + self.SECRET_KEY
        response = requests.get(url)

        if response:
            return response.json()["access_token"]

    def getInfo(self, text):
        """获取词法分析结果"""
        url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer?charset=UTF-8&access_token=" + self.token
        header = {"Content-Type": "application/json"}
        data = json.dumps({"text": text})

        res = requests.post(url, headers=header, data=data)
        return res.json()["items"]

    def getCity(self, text):
        """获取城市名称"""
        for item in self.getInfo(text):
            if item["ne"] == "LOC":
                return item["item"]

    def getMusicName(self, text):
        """获取歌曲名称"""
        items = self.getInfo(text)
        results = ""
        for i, item in enumerate(items):
            if any(key in item["item"] for key in ["听", "首", "放"]):
                for it in items[i + 1:]:
                    results += it["item"]

        return results.replace("。", "")


if __name__ == "__main__":
    import time

    APP_ID = '19745053'
    API_KEY = 'UnBq5gNtiZnReCKts31GiPlS'
    SECRET_KEY = 'Ip2YLBAkGgbCp4xSv7TXjXojihipjFku'
    nlp = MXNLP(APP_ID, API_KEY)

    # print(nlp.getMusicName("播放一首播放陈奕迅的富士山下"))
    # print(nlp.getMusicName("播放一首同一首歌"))

    # time.sleep(0.5)
    # print(nlp.getMusicName("一首陈奕迅的富士山下"))
    # print(nlp.getMusicName("一首同一首歌"))

    # time.sleep(0.5)
    # print(nlp.getMusicName("播放陈奕迅的富士山下"))
    # print(nlp.getMusicName("播放同一首歌"))
