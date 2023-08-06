from moocxing.plugins.sdk.AbstractPlugin import AbstractPlugin


class Plugin(AbstractPlugin):
    SLUG = "play"

    def handle(self, query):
        if "暂停" in query:
            self.media.pause()
        elif "停止" in query:
            self.media.stop()
        elif "继续" in query:
            self.media.unpause()

    def isValid(self, query):
        return any(word in query for word in ["暂停", "停止", "继续"])
