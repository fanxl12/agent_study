#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/4 8:06
@Author  : thezehui@gmail.com
@File    : 3.最大边际相关性示例.py
"""
import dotenv
import weaviate
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import Auth

dotenv.load_dotenv()

# 1.构建加载器与分割器
# loader = UnstructuredMarkdownLoader("./项目API文档.md")
# text_splitter = RecursiveCharacterTextSplitter(
#     separators=[r"\n\n", r"\n", r"。|！|？", r"\.\s|\!\s|\?\s", r"；|;\s", r"，|,\s", r" ", r""],
#     is_separator_regex=True,
#     chunk_size=500,
#     chunk_overlap=50,
#     add_start_index=True,
# )

# 2.加载文档并分割
# documents = loader.load()
# chunks = text_splitter.split_documents(documents)

weaviate_url = 'https://zsnveisws6yjus9bapshka.c0.asia-southeast1.gcp.weaviate.cloud'
weaviate_api_key = 'THZlVEp5UUh5c3lMaWZxZ19DMS8ybzNnQzJUendUMUMvVzA2OGVIcW1JdzFhQUQyV1M3VWY3bjVicm1ZPV92MjAw'

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)

# 3.将数据存储到向量数据库
db = WeaviateVectorStore(
    client=client,
    index_name="DatasetDemo",
    text_key="text",
    # embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    embedding=HuggingFaceEndpointEmbeddings(model="sentence-transformers/all-MiniLM-L12-v2"),
)

# 4.执行最大边际相关性搜索
# search_documents = db.similarity_search("关于应用配置的接口有哪些？")
search_documents = db.max_marginal_relevance_search("关于应用配置的接口有哪些？")

# 5.打印搜索的结果
# print(list(document.page_content[:100] for document in search_documents))
for document in search_documents:
    print(document.page_content[:100])
    print("===========")

client.close()
