from .Client import NotionClient
import json, requests

class Search(NotionClient):
    def __init__(self):
        pass

    @classmethod
    def search(cls, client : dict, filter_obj = "page") -> dict:
        if filter_obj != "database" and filter_obj != "page":
            return "Only database and page are available as filter"

        url = "https://api.notion.com/v1/search"
        headers = client._headers
        payload = {
            "page_size": 100,
            "filter": {
                "property": "object",
                "value": filter_obj
            }
        }

        response = requests.request("POST", url=url, json=payload, headers=headers)
        response_json = json.loads(response.text)

        return response_json
