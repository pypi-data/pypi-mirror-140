import ffmpeg
from aip.speech import AipSpeech
from moocxing.robot import Config
from moocxing.robot import Constants
import logging

log = logging.getLogger(__name__)

class MXSpeech:
    def __init__(self,APP_ID,API_KEY, SECRET_KEY):
        self.client = AipSpeech(APP_ID,API_KEY, SECRET_KEY)

    def TTS(self, text):
        """文本转语音"""
        result = self.client.synthesis(text, 'zh', 4, {'vol': 5, 'per': 4, })
        if not isinstance(result, dict):
            with open(Constants.TEMP_PATH + 'back.mp3', 'wb') as f:
                f.write(result)

        ffmpeg.run(ffmpeg.output(ffmpeg.input(Constants.TEMP_PATH + 'back.mp3'), Constants.TEMP_PATH + 'back.wav'), quiet=True, overwrite_output=True)

    def STT(self, fname="back.wav", _print=False):
        """语音转文本"""
        with open(Constants.TEMP_PATH + fname, 'rb') as fp:
            data = fp.read()

        result = self.client.asr(data, 'pcm', 16000, {'dev_pid': 1537, })
        if result['err_no'] == 0:
            if _print:
                log.info(result['result'][0])
            return str(result['result'][0])
        else:
            return ""

