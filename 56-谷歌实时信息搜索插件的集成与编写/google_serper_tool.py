#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/8 16:53
@Author  : 1964645988@qq.com
@File    : google_serp_tool.py
"""
import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper

dotenv.load_dotenv()

# 定义工具
google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，使用这个工具。"
        "该工具的输入是搜索查询语句。"
    ),
    api_wrapper=GoogleSerperAPIWrapper(),
)

print(google_serper.invoke("马拉松的世界记录是多少？"))
