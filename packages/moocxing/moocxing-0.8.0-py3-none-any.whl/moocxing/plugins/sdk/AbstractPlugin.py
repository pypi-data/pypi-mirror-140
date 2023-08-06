from abc import ABCMeta, abstractmethod


class AbstractPlugin(metaclass=ABCMeta):
    IS_IMMERSIVE = False

    def __init__(self, MODULE):
        self.media = MODULE.get("media")
        self.speech = MODULE.get("speech")
        self.nlp = MODULE.get("nlp")
        self.mqtt = MODULE.get("mqtt")
        self.serial = MODULE.get("serial")
        self.pinyin = MODULE.get("pinyin")
        self.minecraft = MODULE.get("minecraft")

    def say(self, text):
        self.speech.TTS(text)
        self.media.play()

    def play(self, path):
        self.media.play(path)

    def sayThread(self, text):
        self.speech.TTS(text)
        self.media.playThread()

    def playThread(self, path):
        self.media.playThread(path)

    @abstractmethod
    def isValid(self, query):
        return False

    @abstractmethod
    def handle(self, query):
        return None
