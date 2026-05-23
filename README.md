以下是根据您的代码和上下文编写的 `README.md` 文件，包含项目简介、环境配置、本地运行、Docker 部署及 API 使用说明。

```markdown
# AI 女友聊天机器人 (GF Chat)

基于 FastAPI + Moonshot AI (Kimi) + Redis 构建的角色扮演对话服务。模拟具有温柔、幽默、独立等性格特征的虚拟女友，能够根据历史聊天记录生成个性化回复。

## 功能特性

- 支持 POST / GET 两种请求方式，传入用户消息 `query`
- 自动从 Redis 中读取历史对话（Hash: `GFhistory`，字段 `history`）
- 调用 Moonshot 大模型对历史记录进行摘要总结
- 使用角色扮演提示词，让模型模仿“女友”的语气和性格
- 完整日志记录，按天分割日志文件
- 可通过 Docker 一键部署

## 技术栈

- Python 3.9+
- FastAPI
- Redis (用于存储对话历史)
- Moonshot AI API (兼容 OpenAI SDK)
- Uvicorn

## 准备工作

1. **注册 Moonshot AI** 并获取 API Key： [https://moonshot.cn](https://moonshot.cn)
2. **安装 Redis** 并确保服务可用（默认 `127.0.0.1:6379`）
3. 在 Redis 中初始化历史记录（可选）：
   ```bash
   redis-cli HSET GFhistory history "用户：你好 女友：嗨，今天过得怎么样？"
   ```

## 本地运行

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 修改配置
编辑代码文件（例如 `main.py`），替换以下配置：
- `api_key = "xxxx"` → 填入你的 Moonshot API Key
- 如果 Redis 不在本机，修改 `host="127.0.0.1"` 为正确地址

### 4. 启动服务
```bash
uvicorn main:app --host 0.0.0.0 --port 80 --reload
```
服务启动后访问： `http://localhost:80?query=你好`

## Docker 部署

### 1. 构建镜像
确保项目目录包含：`Dockerfile`, `requirements.txt`, `main.py`
```bash
docker build -t gf-chat .
```

### 2. 运行容器
```bash
docker run -d --name gf-chat -p 8080:80 \
  -e REDIS_HOST=你的Redis地址 \
  gf-chat
```
> **注意**：代码中 Redis 地址目前写死为 `127.0.0.1`，若 Redis 运行在独立容器或宿主机，建议修改代码支持环境变量，或使用 `--network host` 模式。

### 3. 测试
```bash
curl "http://localhost:8080/?query=今天想你了"
```

## API 文档

### POST `/`
**请求体** (JSON):
```json
{
  "query": "今天心情不太好"
}
```

**响应**:
- 成功：直接返回女友回复的文本字符串
- 失败：返回 JSON 错误信息，状态码 400
```json
{
  "code": 1,
  "message": "错误详情"
}
```

### GET `/`
**请求参数**:
- `query` (string, required): 用户输入的消息

**示例**:
```
GET /?query=晚上一起看电影吗？
```

**响应**：同 POST，返回纯文本或错误 JSON。

## 环境变量建议（改进版）

当前代码中 Redis 和 API Key 硬编码，建议后续改进为从环境变量读取。例如：
```python
import os
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
API_KEY = os.getenv("MOONSHOT_API_KEY", "xxxx")
```

## 日志文件

服务会在当前目录生成 `GF_YYYY-MM-DD.log` 文件，记录每次请求的 query、历史摘要及错误信息。

## 注意事项

1. **Redis 数据结构**：代码中 `get_npc_data` 从 Hash `GFhistory` 读取所有字段，并假设每个字段都有 `history` 键。请确保存储格式正确。
2. **历史写入缺失**：本服务只读取历史，不自动保存新对话。需要外部程序将每次交互追加到 Redis 中（例如另建一个服务保存 `用户问题`+`女友回答`）。
3. **模型成本**：每次请求会调用两次 Moonshot API（一次总结历史，一次生成回复），注意控制请求频率。
4. **安全**：不要将 API Key 提交到公开仓库，建议使用环境变量或密钥管理服务。

## 项目结构

```
.
├── main.py               # 主程序代码
├── requirements.txt      # Python 依赖
├── Dockerfile            # Docker 构建文件
└── README.md             # 本文件
```

## 常见问题

**Q: 启动时报错 `ConnectionRefusedError` 连接到 Redis**  
A: 检查 Redis 是否运行：`redis-cli ping`，并确认 host/port 配置正确。

**Q: 返回内容为空或重复**  
A: 查看日志文件，确认 Moonshot API Key 有效且账户余额充足。

**Q: 如何保存聊天历史？**  
A: 可以在 `chat_model` 返回后，调用 `redis_client.hset("GFhistory", timestamp, json.dumps({"user": query, "bot": chat_res}))`，并修改 `get_npc_data` 读取所有历史记录。

---

如有问题，请提 Issue 或联系项目维护者。
```

你可以直接将上述内容保存为 `README.md`，并根据实际代码文件名（如 `main.py`）调整命令中的模块名。如果需要添加更详细的 Redis 历史写入示例，我可以进一步补充。
