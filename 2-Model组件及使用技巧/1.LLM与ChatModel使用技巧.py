from datetime import datetime

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 加载环境变量（确保 .env 文件中有 OPENAI_API_KEY）
dotenv.load_dotenv()

# 1. 编排prompt（partial 绑定当前时间）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是OpenAI开发的聊天机器人，请回答用户的问题，现在的时间是{now}"),
    ("human", "{query}"),
]).partial(now=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # 优化：格式化时间，更易读

# 2. 创建大语言模型
llm = ChatOpenAI(model="kimi-k2-thinking", temperature=0)  # 新增temperature，控制随机性

# 3. 构建链（核心修复：将prompt和llm串联成链）
chain = prompt | llm

# 4. 调用链（传入查询参数）
ai_message = chain.invoke({"query": "现在是几点，请讲一个程序员的冷笑话"})

# 输出结果
print("消息类型:", ai_message.type)
print("回复内容:\n", ai_message.content)
print("响应元数据:\n", ai_message.response_metadata)
