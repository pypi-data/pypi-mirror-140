from moocxing.plugins.sdk.AbstractPlugin import AbstractPlugin


class Plugin(AbstractPlugin):
    SLUG = "echo"

    def handle(self, query):
        self.say(query.replace("传话", ""))

    def isValid(self, query):
        return "传话" in query
