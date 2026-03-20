FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    mlflow==2.21.0 \
    psycopg2-binary \
    boto3

EXPOSE 5000

CMD ["sh", "-c", "mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri ${MLFLOW_BACKEND_URI} --default-artifact-root ${MLFLOW_ARTIFACT_ROOT}"]
