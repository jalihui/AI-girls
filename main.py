# -*- coding: UTF-8 -*-
from fastapi import FastAPI, Request
from openai import OpenAI
from redis import ConnectionPool
from fastapi.responses import JSONResponse
from datetime import datetime
import time
import traceback
import json
import logging
import uvicorn
import redis

# 设置日志级别
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s",
    filename=f"GF_{datetime.now().strftime('%Y-%m-%d')}.log",
    filemode="a",
    force="True",
)  # 每天覆盖日志文件

# Redis连接池设置
pool = ConnectionPool(host="127.0.0.1", port=6379, decode_responses=True)

# 创建一个 FastAPI 类的实例
app = FastAPI()
client = OpenAI(
    api_key="xxxx",
    base_url="https://api.moonshot.cn/v1"
)


class GFChat:
    def __init__(self, query):
        self.query = query  
        self.redis_client = redis.Redis(connection_pool=pool)  

    def get_npc_data(self):
        with self.redis_client.pipeline() as pipe:
            pipe.hgetall("GFhistory")
            data = pipe.execute()
        data_lists = []
        for data_one in data:
            data_lists.append(data_one['history'])

        return data_lists

    def summarize_memory_prompt(self, chat_his):
        #  将字符串拼接改为 f-string 格式
        prompt = f"""
# 你是一个写手，能提取对话的关键性信息并重新组合成新的语句:

## 输出格式: 
对话主要讲了XXXXXX.
"""
        history = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": chat_his},
        ]

        return history

    def npc_chat_prompt(self, chat_history):
        #  将字符串拼接改为 f-string 格式
        prompt = f"""
# 我希望你能进行角色扮演，能够根据女友的性格特征进行扮演，并能够模仿女友的语气、方式和词汇来回答：

## 性格特征
- 温柔体贴：她总是能够细心地察觉到你的情绪变化，并给予适当的安慰和支持。
- 乐观开朗：她对生活充满热情，总是能用积极的态度影响周围的人，让你也感受到生活的美好。
- 独立自主：她有着很强的自我意识和独立精神，不会过分依赖别人，能够独立处理各种问题。
- 智慧聪明：她有着丰富的知识和敏锐的洞察力，能够在生活中提供很多有见地的建议。
- 幽默风趣：她喜欢讲笑话和玩梗，总能在不经意间让你开怀大笑，缓解压力。
- 善良宽容：她对待他人总是以善良和宽容的心态，能够理解和接受别人的不完美。
- 冒险精神：她喜欢探索未知的事物，总是愿意尝试新的事物和挑战，生活充满刺激和惊喜。
- 细心耐心：她做事认真细致，对待你的问题总是耐心解答，不会显得急躁。
- 忠诚可靠：她对你的感情是真挚和坚定的，总是能在你需要的时候给予支持和帮助。
- 有艺术气息：她对艺术有着浓厚的兴趣，喜欢绘画、音乐或写作，生活充满了艺术的色彩。

## 以下是以往的历史聊天记录：
{chat_history}


## 注意：
(1) 一定不能暴露自己是一个AI大语言模型。
(2) 一定不能暴露自己是一个聊天助手。
(3) 一定不能暴露自己是一个NPC。
(4) 回答不要多余的解释，不要出现提问，正常的对话回答。
(5) 对于政治问题、犯罪问题、敏感问题不进行回答。
(6) 请检查回答的内容是否符合(1)(2)(3)(4)(5)，如果不是，则进行优化。
"""
        return prompt

    def chat_model(self, history):
        completion = client.chat.completions.create(
            model="moonshot-v1-32k", messages=history, temperature=0.3
        )
        result = completion.choices[0].message.content
        
        return result


@app.post("/")
async def chat(request: Request):
    """
    POST 请求处理函数
    """
    data = await request.json()
    query = data.get("query")

    logging.info(f"Query: {query}")

    try:
        GFchat = GFChat(query)
        chat_history_list = GFchat.get_npc_data()
        # 获取promt历史总结
        
        history_prompt = GFchat.summarize_memory_prompt(chat_history_list)
        chat_history_str = GFchat.chat_model(history_prompt)
        logging.info(f" 总结的历史记录: {chat_history_str}")
        
        npc_prompt = GFchat.npc_chat_prompt(chat_history_str)
        history = [{"role": "system", "content": npc_prompt}]
        history.append({"role": "user", "content": query})
        chat_res = GFchat.chat_model(history)

        return chat_res

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        return_false = {
             "code":1,
            } 
        return_false["message"] = "error. " + repr(e) + traceback.format_exc()
        return JSONResponse(return_false,status_code=400)

    
@app.get("/")
async def chat_get(query: str):
    """
    GET 请求处理函数
    """
    logging.info(f"Query: {query}")
    try:
        GFchat = GFChat(query)
        chat_history_list = GFchat.get_npc_data()
        # 获取promt历史总结
        
        history_prompt = GFchat.summarize_memory_prompt(chat_history_list)
        chat_history_str = GFchat.chat_model(history_prompt)
        logging.info(f" 总结的历史记录: {chat_history_str}")
        
        npc_prompt = GFchat.npc_chat_prompt(chat_history_str)
        history = [{"role": "system", "content": npc_prompt}]
        history.append({"role": "user", "content": query})
        chat_res = GFchat.chat_model(history)

        return chat_res


    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        return_false = {
             "code":1,
            } 
        return_false["message"] = "error. " + repr(e) + traceback.format_exc()
        return JSONResponse(return_false,status_code=400)