from .Client import Client

class Database(Client):
    def __init__(self, client, database_id):
        self.__client = client
        self.database_id = database_id
        self.base_url = f"{client.base_url}/databases/"

    def create_database(self, parent):
        payload = {
            "parent": parent,
        }
        response = requests.request("POST", url, json=payload, headers=headers)
        return

    def retrieve_database(self):
        response = requests.request(
            'GET',
            f'{self.base_url}{self.database_id}',
            headers=self.__client._headers
        )

        return response

    def update_database(self, database_id):
        pass