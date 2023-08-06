from moocxing.robot import Config
from moocxing.robot.utils import serialUtils
from moocxing.robot.Brain import Brain
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=Config.get("logger/level"), format='[%(levelname).4s - %(filename)s]: %(message)s')

MODULE = {}

class INIT:
    def __init__(self):
        if Config.get("media/isUse"):
            self.media = MODULE["media"] = Media()
        if Config.get("speech/isUse"):
            self.speech = MODULE["speech"] = Speech()
        if Config.get("nlp/isUse"):
           self.nlp =  MODULE["nlp"] = nlp()
        if Config.get("mqtt/isUse"):
            self.mqtt = MODULE["mqtt"] = mqtt()
        if Config.get("serial/isUse"):
            self.serial = MODULE["serial"] = Serial()
        if Config.get("pinyin/isUse"):
            self.pinyin = MODULE["pinyin"] = Pinyin()
        if Config.get("minecraft/isUse"):
            self.minecraft = MODULE["minecraft"] = minecraft()

        log.info("=" * 53)
        log.info(f">>> 模块加载完成 可用模块{list(MODULE.keys())}")
        log.info("=" * 53 + "\n")


         
def BRAIN():
    return Brain(MODULE)


def mqtt():
    from .MXMqtt import MXMqtt
    try:
        log.info("=" * 53)
        log.info(">>> 初始化 MQTT模块")
        log.info(f">>> 服务器IP: {Config.get('mqtt/host')} 端口号: {Config.get('mqtt/post')}")
        return MXMqtt(Config.get("mqtt/host"), Config.get("mqtt/post"))
    except:
        log.warning("--- 初始化 MQTT模块 失败")


def minecraft():
    from mcpi.minecraft import Minecraft
    try:
        log.info("=" * 53)
        log.info(">>> 初始化 Minecraft模块")
        log.info(f">>> 服务器IP: {Config.get('minecraft/host')} 端口号: {Config.get('minecraft/post')}")
        return Minecraft.create(Config.get('minecraft/host'), Config.get('minecraft/post'))
    except:
        log.warning("--- 未检测到Minecraft服务器")


def nlp():
    from .MXNLP import MXNLP
    try:
        log.info("=" * 53)
        log.info(">>> 初始化 自然语言分析模块")
        return MXNLP(Config.get('nlp/API_KEY'), Config.get('nlp/SECRET_KEY'))
    except:
        log.warning("--- 初始化 自然语言分析模块 失败")


def Speech():
    from .MXSpeech import MXSpeech
    try:
        log.info("=" * 53)
        log.info(">>> 初始化 语音识别/合成模块")
        return MXSpeech(Config.get("speech/APP_ID"), Config.get("speech/API_KEY"), Config.get("speech/SECRET_KEY"))
    except:
        log.warning("--- 初始化 语音识别/合成模块 失败")

    return MXSpeech()


def Pinyin():
    from .MXPinyin import MXPinyin
    try:
        log.info("=" * 53)
        log.info(">>> 初始化 拼音模块")
        return MXPinyin()
    except:
        log.warning("--- 初始化 拼音模块 失败")


def Media():
    from .MXMedia import MXMedia
    try:
        log.info("=" * 53)
        log.info(">>> 初始化 播放器模块")
        return MXMedia()
    except:
        log.warning("--- 初始化 播放器模块 失败")


def Serial():
    from .MXSerial import MXSerial
    try:
        log.info("=" * 53)
        log.info(">>> 初始化 串口通信模块")

        if Config.get('serial/com'):
            log.info(f">>> 串口号: {Config.get('serial/com')} 波特率: {Config.get('serial/bps')}")
            return MXSerial(Config.get('serial/com'), Config.get('serial/bps'))
        else:
            log.info(f">>> 串口列表: {serialUtils.getCom()}")
            log.info(f">>> 串口号: {serialUtils.getCom(-1)} 波特率: {Config.get('serial/bps')}")
            return MXSerial(serialUtils.getCom(-1), Config.get('serial/bps'))
    except:
        log.warning("--- 未检测到串口")
