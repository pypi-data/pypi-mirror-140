from .Client import NotionClient
from .Database import *
from .Search import Search
from .Model import Model

def client(auth_token : str, version = "2021-08-16"):
    headers = {
        "Accept": "application/json",
        "Notion-Version": version,
        "Authorization": f"Bearer {auth_token}"
    }

    return NotionClient(headers, version)