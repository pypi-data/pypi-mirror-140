from moocxing.robot import LoadPlugin
from moocxing.robot import Constants
from threading import Thread
import logging

log = logging.getLogger(__name__)


class Brain:
    def __init__(self, MODULE):
        self.plugins, self.chat = LoadPlugin.loadPlugin(MODULE)

    def query(self, text, chat=False):
        for plugin in self.plugins:
            if not plugin.isValid(text):
                continue

            log.info("匹配到" + plugin.SLUG + "技能")
            if plugin.IS_IMMERSIVE:
                Thread(target=plugin.handle, args=(text,)).start()
            else:
                plugin.handle(text)
            return True

        log.info("未匹配到技能")
        if self.chat and chat:
            log.info("已匹配闲聊功能")
            self.chat.handle("chat" + text)

        return False
