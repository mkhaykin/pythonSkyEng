from http import HTTPStatus
from typing import Any

import requests
from requests.exceptions import ConnectionError

from src.app.exceptions import APIServiceUnavailableException, APIUnauthorizedException


def get(
        url: str,
        token: str | None = None,
        data: dict | None = None,

) -> requests.Response:
    return _request('get', url=url, token=token, data=data)


def post(
        url: str,
        token: str | None = None,
        data: dict | None = None,
        json: dict | None = None,
) -> requests.Response:
    return _request(
        method='post',
        url=url,
        token=token,
        data=data,
        json=json,
    )


def put(url: str, token: str | None = None, data: dict | None = None) -> requests.Response:
    return _request('put', url=url, token=token, data=data)


def delete(url: str, token: str | None = None, data: dict | None = None) -> requests.Response:
    return _request('delete', url=url, token=token, data=data)


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
        # method: Callable,
        method: str,
        url: str,
        token: str | None = None,
        data: dict | None = None,
        json: dict | None = None,
) -> requests.Response:
    params: dict[str, Any] = {}
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        params.update({'headers': headers})
    if data:
        params.update({'data': data})
    if json:
        params.update({'json': json})

    try:
        # return method(url, **params)
        answer = requests.request(
            method=method,
            url=url,
            **params,
        )
    except ConnectionError:
        raise APIServiceUnavailableException()
    else:
        if answer.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
            raise APIServiceUnavailableException()
        elif answer.status_code == HTTPStatus.UNAUTHORIZED:
            raise APIUnauthorizedException()

        # except Exception as e:
        #     current_app.logger.error(e)

        return answer
