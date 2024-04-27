from transformers import BertModel, BertTokenizer
import torch
from torch.nn.functional import cosine_similarity
import re
from gensim import models

import numpy as np
#word2vec
#model = models.keyedvectors.load_word2vec_format(r'G:\学习\IOT\HAWatcher复现--已知自动化规则\GoogleNews-vectors-negative300.bin.gz', binary=True)
# 初始化tokenizer和模型
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')


# 编写一个函数来获取文本的BERT嵌入
def get_bert_embedding(text, tokenizer, model):
    # 编码文本
    inputs = tokenizer(text, return_tensors="pt")
    # 获取输出
    outputs = model(**inputs)
    # 提取[CLS]令牌的最后一层输出
    last_hidden_state = outputs.last_hidden_state
    cls_embedding = last_hidden_state[:, 0, :]  # [CLS]是每个序列的第一个令牌
    return cls_embedding


#计算余弦相似度
def compute_similarity(text1, text2, tokenizer, model):
    # 获取文本嵌入
    embedding1 = get_bert_embedding(text1, tokenizer, model)
    embedding2 = get_bert_embedding(text2, tokenizer, model)

    # 计算余弦相似度
    similarity = cosine_similarity(embedding1, embedding2)
    return similarity.item()
# def compute_similarity(text1, text2, model):
#     # 将文本分割成单词
#     words1 = text1.split()
#     words2 = re.findall(r'\w+', text2)
#
#     #
#     # # 计算每个文本的平均向量
#     # vector1 = np.mean([model[word] for word in words1 if word in model], axis=0)
#     # vector2 = np.mean([model[word] for word in words2 if word in model], axis=0)
#     similarity=model.n_similarity(words1,words2)
#     # 计算余弦相似度
#     return similarity

def most_similar_capability(lists,capabilities):
    result=['']*len(lists)
    for index,item in enumerate(lists):
        print(f"{item}:")
        max_value=-1
        for capa in capabilities:
            similarity = compute_similarity(item, capa, tokenizer, model)
            #similarity=compute_similarity(item,capa,model)
            print(f"{capa}:{similarity}")
            if similarity>max_value:
                max_value=similarity
                result[index]=capa
        print()
    return result


