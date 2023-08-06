from time import sleep
import wave
import pyaudio
import logging
from threading import Thread
from moocxing.robot import Constants

log = logging.getLogger(__name__)


class MXMedia:

    def __init__(self):
        self._isPlay = False
        self._pause = False
        self._stop = False

    @staticmethod
    def record(RS=4, path=Constants.TEMP_PATH +"back.wav"):
        """录音"""
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        stream.start_stream()
        log.info("* 开始录音<<<<<<")

        frames = []
        for _ in range(int(RATE / CHUNK * RS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()

        wf = wave.open(path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

        wf.close()
        p.terminate()
        log.info("* 结束录音<<<<<<")

    def play(self, path=Constants.TEMP_PATH +"back.wav"):
        """播放"""
        log.info("* 开始播放>>>>>>")
        wf = wave.open( path, 'rb')

        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True)

        stream.start_stream()

        self._pause = False
        self._stop = False
        data = wf.readframes(1024)
        while data and not self._stop:
            if not self._pause:
                stream.write(data)
                data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()
        wf.close()
        p.terminate()

        log.info("* 结束播放>>>>>>")

    def playThread(self, path="back.wav"):
        Thread(target=self.play, args=(path,)).start()

    def stop(self):
        self._stop = True
        sleep(0.1)
        log.info("* 退出播放>>>>>>")

    def pause(self):
        self._pause = True
        log.info("* 暂停播放>>>>>>")

    def unpause(self):
        self._pause = False
        log.info("* 继续播放>>>>>>")
