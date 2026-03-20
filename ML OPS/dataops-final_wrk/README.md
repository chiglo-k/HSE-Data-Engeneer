# DataOps — Итоговое домашнее задание

## Структура проекта

dataops-final_wrk/
- mlflow 
- airflow
- lakefs
- jupyterhub
- ml-service
- monitoring
- kubernetes
- helm
- prompts


## 1. MLflow

```bash
cd 1-mlflow
docker compose up -d --build
```

Веб-интерфейс: http://localhost:5000

Скриншоты:

![MLflow Docker](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/1-1%20mlflow_docker.png)

![MLflow UI](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/1-2%20mlfow_experiment_ui.png)



## 2. Airflow


```bash
cd 2-airflow
docker compose up -d
```

Веб-интерфейс: http://localhost:8081  


Скриншоты:

![Airflow UI](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/2-1%20airflow_ui.png)

![Airflow DAGs](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/2-2%20airflow_dags.png)

![Airflow DAG run](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/2-3%20airflow_test_dag_work.png)



## 3. LakeFS + MinIO

```bash
cd 3-lakefs
docker compose up -d
```

LakeFS: http://localhost:8000  
MinIO:  http://localhost:9001


Скриншоты:

![MinIO](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/3-1%20minIO.png)

![LakeFS](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/3-2%20LakeFS_exemp.png)



## 4. JupyterHub

```bash
cd 4-jupyterhub
docker compose up -d --build
```

Веб-интерфейс: http://localhost:8002  
Пользователи: `admin`, `user1`, `user2`  


Скриншот:

![JupyterLab](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/4.JupyterLab.png)



## 5. ML-сервис (FastAPI)

Сначала запусти мониторинг (этап 6) — он создаёт сеть `monitoring`. Затем:

```bash
cd 5-ml-service
docker compose up -d --build
```

Проверка:

```bash
# Health
curl http://localhost:8004/health

# Предсказание
curl -X POST http://localhost:8004/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1.0, 2.0, 3.0, 4.0]}'

# Метрики Prometheus
curl http://localhost:8004/metrics
```

Swagger UI: http://localhost:8004/docs

![Logs and Prediction](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/5-1%20LogsXPrediction.png)



## 6. Мониторинг (Prometheus + Grafana)

```bash
cd 6-monitoring
docker compose up -d
```

Prometheus: http://localhost:9090  
Grafana:    http://localhost:3000

Grafana: логин `admin`, пароль из `.env` — `GRAFANA_PASSWORD`.  
Datasource и дашборд ML Service подключаются автоматически через provisioning.

Скриншот:

![Grafana + Prometheus](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/6-1%20GrafanaXPrometheus.png)



## 7. Kubernetes

```bash
cd 7-kubernetes
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

kubectl get pods
kubectl get svc
kubectl get ingress
```

Для локального запуска используется Minikube:

```bash
minikube start --driver=docker
```



## 8. Helm

```bash
cd 8-helm

# Установить
helm install ml-release ./ml-service

# Статус
helm status ml-release
```



## 9. MLflow Prompt Storage

MLflow (этап 1) должен быть запущен.

```bash
cd 9-prompts
pip install "mlflow>=2.18.0"
python create_prompts.py
```

Результаты: http://localhost:5000/#/prompts

Скриншот:

![Prompts](https://raw.githubusercontent.com/chiglo-k/HSE-Data-Engeneer/main/ML%20OPS/dataops-final_wrk/attachments/9-1%20prompt.png)
