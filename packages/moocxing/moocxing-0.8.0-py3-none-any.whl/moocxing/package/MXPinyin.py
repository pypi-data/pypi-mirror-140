from xpinyin import Pinyin

import logging

log = logging.getLogger(__name__)


class MXPinyin:
    def __init__(self):
        self.pinyin = Pinyin()

    def getPinyin(self, text, cut=""):
        """获取拼音"""
        return self.pinyin.get_pinyin(text, cut)


if __name__ == "__main__":
    p = MXPinyin()
    print(p.getPinyin("上海"))
    print(p.getPinyin("上海", cut="-"))
