#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/9 17:53
@Author  : 1964645988@qq.com
@File    : 1.GPT模型绑定函数.py
"""
import asyncio
import json
import os
from typing import Type, Any

import dotenv
import requests
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

dotenv.load_dotenv()


class GaodeWeatherArgsSchema(BaseModel):
    city: str = Field(description="需要查询天气预报的目标城市，例如：广州")


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class GaodeWeatherTool(BaseTool):
    """根据传入的城市名查询天气"""
    name: str = "gaode_weather"
    description: str = "当你想询问天气或与天气相关的问题时的工具。"
    args_schema: Type[BaseModel] = GaodeWeatherArgsSchema

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """运行工具获取对应城市的天气预报"""
        try:
            # 1.获取高德API秘钥，如果没有则抛出错误
            gaode_api_key = os.getenv("GAODE_API_KEY")
            if not gaode_api_key:
                return f"高德开放平台API秘钥未配置"

            # 2.提取传递的城市名字并查询行政编码
            city = kwargs.get("city", "")
            session = requests.session()
            api_domain = "https://restapi.amap.com/v3"
            city_response = session.request(
                method="GET",
                url=f"{api_domain}/config/district?keywords={city}&subdistrict=0&extensions=all&key={gaode_api_key}",
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            city_response.raise_for_status()
            city_data = city_response.json()

            # 3.提取行政编码调用天气预报查询接口
            if city_data.get("info") == "OK":
                if len(city_data.get("districts")) > 0:
                    ad_code = city_data["districts"][0]["adcode"]

                    weather_response = session.request(
                        method="GET",
                        url=f"{api_domain}/weather/weatherInfo?city={ad_code}&extensions=all&key={gaode_api_key}&output=json",
                        headers={"Content-Type": "application/json; charset=utf-8"},
                    )
                    weather_response.raise_for_status()
                    weather_data = weather_response.json()
                    if weather_data.get("info") == "OK":
                        return json.dumps(weather_data)

            session.close()
            return f"获取{kwargs.get('city')}天气预报信息失败"
            # 4.整合天气预报信息并返回
        except Exception as e:
            return f"获取{kwargs.get('city')}天气预报信息失败"


async def main():
    # 1.定义工具列表
    gaode_weather = GaodeWeatherTool()
    google_serper = GoogleSerperRun(
        name="google_serper",
        description=(
            "一个低成本的谷歌搜索API。"
            "当你需要回答有关时事的问题时，可以调用该工具。"
            "该工具的输入是搜索查询语句。"
        ),
        args_schema=GoogleSerperArgsSchema,
        api_wrapper=GoogleSerperAPIWrapper(),
    )
    tool_dict = {
        # gaode_weather.name: gaode_weather,
        google_serper.name: google_serper,
    }
    tools = [tool for tool in tool_dict.values()]

    # 3.定义mcp客户端
    client = MultiServerMCPClient(
        {
            "weather": {
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            }
        }
    )

    mcp_tools: list[BaseTool] = await client.get_tools()
    for tool in mcp_tools:
        tool_dict[tool.name] = tool
        tools.append(tool)

    # 2.创建Prompt
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "你是由OpenAI开发的聊天机器人，可以帮助用户回答问题，必要时刻请调用工具帮助用户解答，如果问题需要多个工具回答，请一次性调用所有工具，不要分步调用"
        ),
        ("human", "{query}"),
    ])

    # 3.创建大语言模型并绑定工具
    llm = ChatOpenAI(model="gpt-4o")
    llm_with_tool = llm.bind_tools(tools=tools)

    # 4.创建链应用
    chain = {"query": RunnablePassthrough()} | prompt | llm_with_tool

    # 5.调用链应用，并获取输出响应
    # query = "上海现在天气怎样，并且请用谷歌搜索工具查询一下2024年巴黎奥运会中国代表团共获得几枚金牌？"
    query = "今天上海的天气怎样?"
    ai_message = chain.invoke(query)
    tool_calls = ai_message.tool_calls
    # 6.判断是工具调用还是正常输出结果
    if len(tool_calls) <= 0:
        print("生成内容: ", ai_message.content)
    else:
        # 7.将历史的系统消息、人类消息、AI消息组合
        messages = prompt.invoke(query).to_messages()
        messages.append(ai_message)

        steps = []  # 用于记录计算步骤
        final_answer = None  # 最终答案

        if hasattr(ai_message, "additional_kwargs") and "tool_calls" in ai_message.additional_kwargs:
            # 提取工具调用信息
            tool_calls = ai_message.additional_kwargs["tool_calls"]
            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]
                steps.append(f"调用工具: {tool_name}({tool_args})")
        elif hasattr(ai_message, "tool_calls"):
            for tool_call in tool_calls:
                tool = tool_dict.get(tool_call.get("name"))  # 获取需要执行的工具
                steps.append(f"正在执行functon call工具: {tool.name}")
                content = tool.invoke(tool_call.get("args"))  # 工具执行的内容/结果
                steps.append(f"functon call工具返回结果: {content}")
                tool_call_id = tool_call.get("id")
                messages.append(ToolMessage(
                    content=content,
                    tool_call_id=tool_call_id,
                ))
            end_content = llm.invoke(messages).content
            steps.append(f"调用function call最终输出内容: {end_content}")
        elif ai_message.type == "tool":
            # 提取工具执行结果
            tool_name = ai_message.name
            tool_result = ai_message.content
            steps.append(f"{tool_name} 的结果是: {tool_result}")
        elif ai_message.type == "ai":
            # 提取最终答案
            final_answer = ai_message.content

        # 打印优化后的结果
        print("\n调用过程:")
        for step in steps:
            print(f"- {step}")
        if final_answer:
            print(f"\n最终答案: {final_answer}")


if __name__ == "__main__":
    asyncio.run(main())
