from django.conf import settings
from pymongo import MongoClient

_clients = {}

def get_mongo_db():
    cfg = settings.MONGO
    name = cfg.get("CLIENT_NAME", "default")

    if name not in _clients:
        _clients[name] = MongoClient(cfg["URI"])

    return _clients[name][cfg["DB_NAME"]]
