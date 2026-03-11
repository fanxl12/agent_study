#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/29 22:36
@Author  : thezehui@gmail.com
@File    : 1.weaviate嵌入向量数据库示例.py
"""
import dotenv
import weaviate
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import Auth
from weaviate.collections.classes.filters import Filter

dotenv.load_dotenv()

# 1.原始文本数据与元数据
texts = [
    "笨笨是一只很喜欢睡觉的猫咪",
    "我喜欢在夜晚听音乐，这让我感到放松。",
    "猫咪在窗台上打盹，看起来非常可爱。",
    "学习新技能是每个人都应该追求的目标。",
    "我最喜欢的食物是意大利面，尤其是番茄酱的那种。",
    "昨晚我做了一个奇怪的梦，梦见自己在太空飞行。",
    "我的手机突然关机了，让我有些焦虑。",
    "阅读是我每天都会做的事情，我觉得很充实。",
    "他们一起计划了一次周末的野餐，希望天气能好。",
    "我的狗喜欢追逐球，看起来非常开心。",
]
metadatas = [
    {"page": 1},
    {"page": 2},
    {"page": 3},
    {"page": 4},
    {"page": 5},
    {"page": 6, "account_id": 1},
    {"page": 7},
    {"page": 8},
    {"page": 9},
    {"page": 10},
]

# 2.创建连接客户端
weaviate_url = 'https://zsnveisws6yjus9bapshka.c0.asia-southeast1.gcp.weaviate.cloud'
weaviate_api_key = 'THZlVEp5UUh5c3lMaWZxZ19DMS8ybzNnQzJUendUMUMvVzA2OGVIcW1JdzFhQUQyV1M3VWY3bjVicm1ZPV92MjAw'

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)
# embedding = OpenAIEmbeddings(model="text-embedding-3-small")
embedding = HuggingFaceEndpointEmbeddings(model="sentence-transformers/all-MiniLM-L12-v2")

# 3.创建LangChain向量数据库实例
db = WeaviateVectorStore(
    client=client,
    index_name="Dataset",
    text_key="text",
    embedding=embedding,
)

# 4.添加数据
# ids = db.add_texts(texts, metadatas)
# print(ids)

# 5.执行相似性搜索
# print(db.similarity_search_with_score("笨笨"))
filters = Filter.by_property("page").greater_or_equal(5)
print(db.similarity_search_with_score("笨笨", filters=filters))
# retriever = db.as_retriever()
# print(retriever.invoke("笨笨"))

client.close()
