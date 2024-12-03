#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
import math
from collections import Counter
import json
import numpy as np

def save_txt(path,data):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
        f.write('\n')
        f.close()
def save_dict(path,data):
    with open(path, 'w', encoding='utf-8') as f:
        datajson=json.dumps(data)
        json.dump(datajson, f, indent=4,ensure_ascii=False)
        f.write('\n')
        f.close()
def save_json(path,data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4,ensure_ascii=False)
        f.write('\n')
        f.close()

def load_json(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data
def load_txt(path):
    with open(path, 'r', encoding='utf-8') as file:
        all_name_path=[]
        for line in file:
            all_name_path.append(line.strip())
        return all_name_path
def load_dict(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        data_dict=json.loads(data)
        return data_dict


class BM25:
    def __init__(self, docs,docs_names, k1=1.5, b=0.75):
        """
        BM25算法的构造器
        :param docs: 分词后的文档列表，每个文档是一个包含词汇的列表
        :param k1: BM25算法中的调节参数k1
        :param b: BM25算法中的调节参数b
        """
        self.docs = docs
        self.k1 = k1
        self.b = b
        self.doc_len = [len(doc) for doc in docs]  # 计算每个文档的长度
        self.avgdl = sum(self.doc_len) / len(docs)  # 计算所有文档的平均长度
        self.doc_freqs = []  # 存储每个文档的词频
        self.idf = {}  # 存储每个词的逆文档频率
        self.df={}
        self.initialize()
        self.doc_names=docs_names

    def initialize(self):
        """
        初始化方法，计算所有词的逆文档频率
        """
        #df = {}  # 用于存储每个词在多少不同文档中出现
        for doc in self.docs:
            # 为每个文档创建一个词频统计
            self.doc_freqs.append(Counter(doc))
            # 更新df值
            for word in set(doc):
                self.df[word] = self.df.get(word, 0) + 1
        # 计算每个词的IDF值
        for word, freq in self.df.items():
            self.idf[word] = math.log((len(self.docs) - freq + 0.5) / (freq + 0.5) + 1)

    def appendItem(self, doc,doc_name):
        for word in set(doc):
            self.df[word] = self.df.get(word, 0) + 1
        # 计算每个词的IDF值
        for word in set(doc):
            freq=self.df[word]
            self.idf[word] = math.log((len(self.docs) - freq + 0.5) / (freq + 0.5) + 1)
        max_len=len(docs_names)
        self.doc_names[max_len]=doc_name

    def score(self, doc, query):
        """
        计算文档与查询的BM25得分
        :param doc: 文档的索引
        :param query: 查询词列表
        :return: 该文档与查询的相关性得分
        """
        score = 0.0
        for word in query:
            if word in self.doc_freqs[doc]:
                freq = self.doc_freqs[doc][word]  # 词在文档中的频率
                # 应用BM25计算公式
                score += (self.idf[word] * freq * (self.k1 + 1)) / (freq + self.k1 * (1 - self.b + self.b * self.doc_len[doc] / self.avgdl))
        return score

    def get_max(self,query):
        scores = [self.score(i, query) for i in range(len(self.docs))]
        index=np.argmax(scores)
        return index,self.doc_names[index]

# 示例文档集和查询
'''
docs = [["the", "quick", "brown", "fox"],
        ["the", "lazy", "dog"],
        ["the", "quick", "dog"],
        ["the", "quick", "brown", "brown", "fox"]]
query = ["quick", "brown"]
'''

name_en=["ctrip"][0]
data_output_path="corpus/random_walk/"+name_en+"_graph"+"/"
data_unique2all=load_dict(data_output_path+"data_unique2all.json")

docs=[]
docs_names={}
index=0
for key in data_unique2all:
    level_path="/".join(key.split("_")[:-1])+"/"
    with open(data_output_path+level_path+key+"-html.txt", 'r', encoding='utf-8') as f:
        html_code_save=f.readlines()
        print(len(html_code_save))
        docs.append(html_code_save)
    docs_names[index]=key
    index+=1

# 初始化BM25模型并计算得分
bm25 = BM25(docs,docs_names)

key="ctrip0_5_214"
level_path="/".join(key.split("_")[:-1])+"/"
query=[]

with open(data_output_path+level_path+key+"-html.txt", 'r', encoding='utf-8') as f:
    query=f.readlines()
print(len(query))
#scores = [bm25.score(i, query) for i in range(len(docs))]

print(bm25.get_max(query))
## query和文档的相关性得分：
## sores = [1.0192447810666774, 0.0, 0.3919504878447609, 1.2045355839511414]
