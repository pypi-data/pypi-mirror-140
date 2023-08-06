class NotionClient:
    def __init__(self, headers : dict, version : str):
        self.version = version
        self._headers = headers
        self._base_url = "https://api.notion.com/v1"