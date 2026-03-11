import dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# 加载环境变量（确保 .env 文件中有 OPENAI_API_KEY）
dotenv.load_dotenv()

chat = ChatOpenAI(
    model="ernie-4.0-8k",  # 使用千帆modelbuilder上的deepseek-v3
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="bce-v3/ALTAK-xzJzYoNjuRqm9reJqlL86/eef4586b757caeef08e42a163a6901d309b2270c",
    # 你的api-key，在这里创建：https://console.bce.baidu.com/iam/#/iam/apikey/list
    base_url="https://qianfan.baidubce.com/v2/",  # 千帆modelbuilder 的base_url
)

messages = [HumanMessage(content="你是谁?")]
ai_message = chat.invoke(messages)

# 输出结果
print("消息类型:", ai_message.type)
print("回复内容:\n", ai_message.content)
print("响应元数据:\n", ai_message.response_metadata)
