FROM python:3.11-slim
WORKDIR /app
RUN pip install forge-mcp
EXPOSE 4243
CMD ["forge-server", "--port", "4243"]
