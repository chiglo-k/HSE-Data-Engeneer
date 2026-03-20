FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    jupyterhub==4.1.5 \
    jupyterlab \
    notebook \
    oauthenticator \
    dockerspawner

RUN npm install -g configurable-http-proxy

# Создаём системного пользователя admin для PAM-аутентификации
# Пароль задаётся через ARG при сборке: docker compose build --build-arg ADMIN_PASSWORD=secret
ARG ADMIN_PASSWORD=admin123
RUN useradd -m -s /bin/bash admin && \
    echo "admin:${ADMIN_PASSWORD}" | chpasswd

WORKDIR /srv/jupyterhub

COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py

EXPOSE 8000

CMD ["jupyterhub", "--config", "/srv/jupyterhub/jupyterhub_config.py"]
