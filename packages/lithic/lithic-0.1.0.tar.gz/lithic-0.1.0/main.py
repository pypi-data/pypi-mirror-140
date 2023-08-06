
import requests


class Lithic:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://lithic.com/api/v1"

    def list_cards(self):
        url = f"{self.base_url}/cards"

        headers = {
            "Accept": "application/json",
            "Authorization": f"api-key {self.api_key}",
        }

        resp = requests.request("GET", url, headers=headers)
        resp.raise_for_status()
        return resp

        