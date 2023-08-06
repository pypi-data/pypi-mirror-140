import requests, os, json

class Client:
    """
    Main class for Notion client initialization

    Attributes
    -----------

    Protected:
        _headers : dict
            header with the  Notion's API key and version to auth HTTP requests
        _base_url: str
            Notion's API URL base

    """

    def __init__(self, headers):
        """
            Creates a new Notion instance
        """
        self._headers = headers
        self._base_url = "https://api.notion.com/v1"

    @property
    def headers():
        return None

    @headers.setter
    def headers(self, auth_token, version="2021-08-16"):
        self._headers = {
            "Accept": "application/json",
            "Notion-Version": version,
            "Authorization": f"Bearer {auth_token}"
        }

        return self._headers