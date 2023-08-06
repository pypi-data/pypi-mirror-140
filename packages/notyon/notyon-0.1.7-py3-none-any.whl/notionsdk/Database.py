from .Client import NotionClient
from .Search import Search
import json
from requests import request

class Database(NotionClient):
    def __init__(self, client, database_id : str, title="Database"):
        self.__client = client
        self.__headers = client._headers
        self._base_url = f"{client._base_url}/databases/"

        self.id = database_id
        self.title = title

    @classmethod
    def create(cls, client : dict, page_id : str, model = None):
        payload = {
            "parent": {
                "type" : "page_id",
                "page_id": page_id
            },

            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": model.title,
                        "link": model.link
                    }
                }
            ],

            "properties": model.properties
        }

        response = request('POST', url="https://api.notion.com/v1/databases", json=payload, headers=client._headers)
        response_json = json.loads(response.text)

        if response_json['object'] == "error":
            return None

        return cls(client, "a359c548-62c4-4ea7-aa66-802b5050ecf9", model.title)

    def retrieve(self):
        response = request('GET', f'{self._base_url}{self.id}', headers=self.__headers)
        response_json = json.loads(response.text)

        return response_json

    def update(self, database_id):
        pass

    @classmethod
    def find(cls, client, value: str, by="title"):
        response = Search.search(client, "database")
        result = None

        if by == "title":
            for results in response["results"]:
                try:
                    title = results['title'][0]['text']['content']
                    if(title == value):
                        result = results
                        break
                except:
                    pass

            if result:
                return cls(client, result['id'], title=value)
            return None