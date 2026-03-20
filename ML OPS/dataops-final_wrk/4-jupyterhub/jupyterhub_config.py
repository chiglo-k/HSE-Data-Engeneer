import os

c = get_config()  # noqa

# Сеть
c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.port = 8000

# Аутентификация
from jupyterhub.auth import DummyAuthenticator
c.JupyterHub.authenticator_class = DummyAuthenticator
c.DummyAuthenticator.password = os.environ.get("JUPYTERHUB_ADMIN_PASSWORD", "admin123")

# Администраторы
c.Authenticator.admin_users = {"admin"}
c.Authenticator.allowed_users = {"admin", "user1", "user2"}

# Spawner
c.JupyterHub.spawner_class = "simple"
c.Spawner.default_url = "/lab"

# Таймауты
c.Spawner.start_timeout = 120
c.Spawner.http_timeout = 60

# Хранение данных
data_dir = os.environ.get("JUPYTERHUB_DATA_DIR", "/data")
c.JupyterHub.db_url = f"sqlite:///{data_dir}/jupyterhub.sqlite"
c.JupyterHub.cookie_secret_file = f"{data_dir}/jupyterhub_cookie_secret"
