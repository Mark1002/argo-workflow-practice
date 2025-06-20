import os

from hera.shared import global_config

ARGO_SERVER = os.getenv("ARGO_SERVER", "http://localhost:2746")
ARGO_TOKEN = os.getenv("ARGO_TOKEN")


global_config.namespace = "argo"
global_config.host = ARGO_SERVER
global_config.token = ARGO_TOKEN
