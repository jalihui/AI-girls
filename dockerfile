FROM python:3.10-slim

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口（可根据需要修改）
EXPOSE 80

# 启动服务（请将 main 替换为您的实际文件名，不含 .py）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]