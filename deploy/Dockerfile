# macaujc-predictor 容器镜像
# 纯 Python 标准库, 无 pip 依赖; 容器内监听 8000, 由 compose 映射到宿主 8787
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 TZ=Asia/Shanghai

# 仅拷贝运行必需物(构建上下文 = 项目根)
COPY app/ /app/app/
COPY web/ /app/web/
COPY rules/ /app/rules/

# 数据目录由卷挂载持久化 SQLite(compose 挂 /app/data)
EXPOSE 8000

HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/api/status',timeout=4)"

CMD ["python", "-u", "/app/app/server.py"]
