from typing import Callable

import requests
from flask import current_app


def get(url: str, token: str | None = None, data: dict | None = None) -> requests.Response | None:
    return _request(requests.get, url=url, token=token, data=data)


def post(url: str, token: str | None = None, data: dict | None = None) -> requests.Response | None:
    return _request(requests.post, url=url, token=token, data=data)


def put(url: str, token: str | None = None, data: dict | None = None) -> requests.Response | None:
    return _request(requests.put, url=url, token=token, data=data)


def delete(url: str, token: str | None = None, data: dict | None = None) -> requests.Response | None:
    return _request(requests.delete, url=url, token=token, data=data)


# def _clear_data(data: dict | None) -> dict | None:
#     """ Удаляем чувствительную информацию при логировании."""
#     if not data:
#         return None
#
#     banned_keys = ['password']
#     for key in banned_keys:
#         if key in data:
#             data[key] = '*' * 7
#
#     return data


def _request(
        method: Callable,
        url: str,
        token: str | None = None,
        data: dict | None = None,
) -> requests.Response | None:
    params = {}
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        params.update({'headers': headers})
    if data:
        params.update({'data': data})

    try:
        return method(url, **params)
    except Exception as e:
        current_app.logger.error(e)

    return None
