#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/29 10:33
@Author : 1964645988@qq.com
@File   : quickstart_check_readiness.py
"""
import weaviate
from weaviate.classes.init import Auth

# Best practice: store your credentials in environment variables
weaviate_url = 'https://zsnveisws6yjus9bapshka.c0.asia-southeast1.gcp.weaviate.cloud'
weaviate_api_key = 'THZlVEp5UUh5c3lMaWZxZ19DMS8ybzNnQzJUendUMUMvVzA2OGVIcW1JdzFhQUQyV1M3VWY3bjVicm1ZPV92MjAw'

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)

print(client.is_ready())  # Should print: `True`

client.close()  # Free up resources
