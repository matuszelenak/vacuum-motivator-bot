import requests

from django.conf import settings

TRELLO_BOARD_ID = '5d0780ba5fc4773b7b64ea4c'
TRELLO_LISTS = {
    settings.ACTIONS_START: '5d359d600fac700d5d3738d9',
    settings.ACTIONS_STOP: '5d359d67b8dfca07cdecbfca',
    settings.ACTIONS_CONTINUE: '5d359d698baeb81eb0675852',
    settings.ACTIONS_DO: '5d078b958a48e34151ab782e',
    settings.ACTIONS_LONGTERM: '5d10b78efe5d0c237d376cf9',
    settings.ACTIONS_UNFINISHED: '5dad99bf0df0d37236224dfc',
    settings.ACTIONS_UNFULLFILLED: '5d10b79f978f016d3e9f5bef'
}
TRELLO_LIST_ID = '5d078b958a48e34151ab782e'


def trello_api_request(endpoint: str, query_params: dict) -> dict:
    query_params.update({
        'token': settings.TRELLO_TOKEN,
        'key': settings.TRELLO_KEY
    })
    url = f' https://api.trello.com/1/{endpoint}'
    response = requests.get(url, params=query_params)
    return response.json()
