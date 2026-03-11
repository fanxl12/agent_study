#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/8 15:00
@Author  : thezehui@gmail.com
@File    : gaode_weather_tool.py
"""
import os
from typing import Any, Type

import dotenv
import requests
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

dotenv.load_dotenv()


class GaodeIPArgsSchema(BaseModel):
    ip: str = Field(description="需要查询定位城市的IP地址，例如：117.154.100.144")


class GaodeIPTool(BaseTool):
    """根据传入的IP地址查询对应城市"""
    name: str = "gaode_ip"
    description: str = "当你想查询IP对应城市或者根据IP定位城市的时候可以使用该工具"
    args_schema: Type[BaseModel] = GaodeIPArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """根据传入的IP运行调用api获取对应的城市信息"""
        try:
            # 1.获取高德API秘钥，如果没有创建的话，则抛出错误
            gaode_api_key = os.getenv("GAODE_API_KEY")
            if not gaode_api_key:
                return f"高德开放平台API未配置"

            # 2.从参数中获取ip地址
            ip = kwargs.get("ip", "")
            api_domain = "https://restapi.amap.com/v3"
            session = requests.session()

            # 3.发起IP信息转换为地理位置信息，根据ip获取ad_code
            ip_response = session.request(
                method="GET",
                url=f"{api_domain}/ip?key={gaode_api_key}&ip={ip}",
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            ip_response.raise_for_status()
            ip_data = ip_response.json()
            print(ip_data)
            if ip_data.get("info") == "OK":
                if ip_data.get('province') == '局域网':
                    return f"{ip}为局域网IP，无法定位城市"
                elif isinstance(ip_data.get('city'), list) and len(ip_data.get('city')) == 0:
                    return f"{ip}对应的城市信息为空"
                return ip_data.get("city")
            return f"获取{ip}对应的城市信息失败:{ip_data.get('info')}"
        except Exception as e:
            return f"获取{kwargs.get('ip', '')}转换为城市信息失败"


gaode_weather = GaodeIPTool()

# print(gaode_weather.invoke({"ip": "117.154.100.144"}))
print(gaode_weather.invoke({"ip": "114.247.50.2"}))
# print(gaode_weather.invoke({"ip": "117.154.100.253"}))
# print(gaode_weather.invoke({"ip": "192.168.10.100"}))
