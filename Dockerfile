FROM python:3.12-slim
WORKDIR /app
COPY src /app/src
COPY module.yaml catalog.json /app/
ENV PYTHONPATH=/app/src
USER 65532:65532
EXPOSE 8080
CMD ["python", "-m", "flow_semantic.api", "--host", "0.0.0.0", "--port", "8080"]
