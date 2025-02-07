import requests
import os

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://0.0.0.0:8000")

def get_moovitamix_data(endpoint: str) -> dict:
    url = f"{FASTAPI_URL}/{endpoint}"
    page = 1
    items = []
    while True:
        response = requests.get(url, params={"page": page, "size": 100})
        data = response.json()
        if response.status_code != 200 or not data["items"]:
            break
        items.extend(data["items"])
        page += 1
    return items

def get_moovitamix_tracks() -> dict:
    return get_moovitamix_data("tracks")

def get_moovitamix_users() -> dict:
    return get_moovitamix_data("users")

def get_moovitamix_listen_history() -> dict:
    return get_moovitamix_data("listen_history")