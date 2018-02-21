# 使用一个官方的Python运行时环境作为一个父镜像
FROM python:2.7-slim

# 将工作目录切换到 /app
WORKDIR /app

# 将当前目录的内容拷贝到容器的 /app中
ADD . /app

# 安装requirements.txt中指定的Python packages
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# 将这个容器的端口80暴露出来
EXPOSE 80

# 定义环境变量
ENV NAME World

# 在容器发布的时候，运行app.py
CMD ["python", "app.py"]