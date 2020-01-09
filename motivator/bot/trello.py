import requests

from django.conf import settings

def trello_api_request(endpoint: str, query_params: dict) -> dict:
    query_params.update({
        'token': settings.TRELLO_TOKEN,
        'key': settings.TRELLO_KEY
    })
    url = f' https://api.trello.com/1/{endpoint}'
    response = requests.get(url, params=query_params)
    return response.json()
