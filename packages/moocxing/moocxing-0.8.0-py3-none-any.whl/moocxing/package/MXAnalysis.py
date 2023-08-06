import re
import csv
import time
import json

print("*** 初始化数据分析模块")


class MXAnalysis:
    def __init__(self, paths=None, datas=None, nlp=None):
        self.paths = paths
        self.fileData = datas

        self.nlp = nlp

        self.keys, self.values, self.items = [], [], []
        self.data, self.nodes, self.links = [], [], []

        self.allData = []
        self.__getAllData()

    # list去重
    @staticmethod
    def __setli(li):
        name = [l["name"] for l in li]
        newli = []
        for i, n in enumerate(name):
            if n not in newli:
                newli.append(n)
            else:
                del li[i]
        return li

    # 读取文件
    def __readFile(self, path):
        with open(path, "r") as f:
            self.fileData = ""
            for d in f.readlines():
                self.fileData += d

    # 正则数据
    def __regexData(self, key="内容"):
        if key == "内容":
            return re.findall(f'[\d][.,，、.](.*?)\n', self.fileData + "\n")
        else:
            return re.findall(f'{key}[:：](.*?)\n', self.fileData + "\n")[0]

    def getData(self):
        name = self.__regexData("学生姓名")
        contents = self.__regexData("内容")

        if self.nlp is not None:
            data = self.nlp.getInfo(contents)
            time.sleep(0.4)
            contents = []
            for d in data:
                if "nz" in (d["pos"], d["ne"]):
                    contents.append(d["item"].lower())

        self.allData.append({name: contents})

    # 获取全部数据
    def __getAllData(self):
        if self.fileData is None:
            for path in self.paths:
                self.__readFile(path)
                self.getData()
        else:
            self.getData()

    # 数据预处理
    def __initData(self):
        self.keys, self.values, self.items = [], [], []
        for data in self.allData:
            self.keys += data.keys()
            self.values += data.values()
            self.items += data.items()

    # 保存数据
    def saveData(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f)

    # 获取知识图谱数据
    def getGraphData(self, save=False):
        self.__initData()
        for item in self.items:
            for value in list(set(item[1])):
                self.links.append({"source": item[0], "target": value})

        self.values = list(set(sum(self.values, [])))
        for key in self.keys:
            self.nodes.append({"name": key, "symbolSize": 60, "itemStyle": {"normal": {"color": "#CC3333"}}})
        for value in self.values:
            self.nodes.append({"name": value, "itemStyle": {"normal": {"color": "#3399CC"}}})

        if save:
            self.saveData("nodes.json", self.nodes)
            self.saveData("links.json", self.links)
        return self.nodes, self.links

    # 获取词云数据
    def getWordData(self, save=False):
        self.__initData()
        self.values = sum(self.values, [])
        for value in list(set(self.values)):
            self.data.append((value, self.values.count(value)))

        if save:
            self.saveData("data.json", self.data)
        return self.data

    # 获取个人知识图谱
    def perGraphData(self):
        self.getGraphData()
        self.getWordData()

        self.links = []
        f0, f1 = [], []
        titles = ("构造", "电路", "编程", "智能", "设计", "整合", "创新")
        contents = (("3D打印", "激光切割", "CNC加工"),
                    ("基础电路", "Arduino", "树莓派"),
                    ("积木图形化编程", "Python", "我的世界", "Opencv图像处理"),
                    ("App Inventor", "机器学习", "人工智能"),
                    ("盲人水杯", "设计思维", "智能家居"),
                    ("创客工程师", "机器人战队", "火星探索"),
                    ("入门赛事集训", "创新科赛集训", "发明专利国际赛事"))

        for f in csv.reader(open("sign.csv", "r")):
            f0.append(f[0])
            f1.append(f[1])

        for d in self.data:
            i = f0.index(d[0])
            self.links.append({'source': f0[i], 'target': f1[i]})

        for title in titles:
            self.links.append({'source': self.nodes[0]["name"], 'target': title})
            self.nodes.append({'name': title, 'symbolSize': 40, "itemStyle": {"normal": {"color": "#CC6633"}}})
        for i, content in enumerate(contents):
            for c in content:
                self.nodes.append({'name': c, 'symbolSize': 20, "itemStyle": {"normal": {"color": "#FFCC66"}}})
                self.links.append({'source': titles[i], 'target': c})

        return self.__setli(self.nodes), self.links
