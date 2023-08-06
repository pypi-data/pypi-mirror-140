from moocxing.plugins.sdk.AbstractPlugin import AbstractPlugin
from moocxing.robot import Config
import requests
import logging

log = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    SLUG = "chat"

    def __init__(self, SKILL):
        super().__init__(SKILL)
        self.url = "https://api.naixing.vip/anonymous/wordManage/answers/"

        self.data = {
            "question": "",
            "robotId": 0,
            "deviceId": ""
        }

    def handle(self, query):
        if Config.get("naixing/robotId") and query != "":
            self.data["robotId"] = Config.get("naixing/robotId")
            self.data["question"] = query.replace("chat", "")

            info = requests.post(url=self.url, json=self.data).json()
            self.data["deviceId"] = info["data"]["deviceId"]

            log.info(f"answers: {info['data']['answers']}")
            self.say(info['data']['answers'])

    def isValid(self, query):
        return "chat" in query
