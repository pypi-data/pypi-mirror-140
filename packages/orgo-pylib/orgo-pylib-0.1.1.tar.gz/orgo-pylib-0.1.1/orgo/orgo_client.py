from typing import Optional

import requests

from src.orgo.models import OrgoUser


def request_token(api_url: str, client_id: str, client_secret: str) -> str:
    """
    Retrieves a request token from the Authorization Server (Orgo)
    :param api_url: The base API URL (no trailing slash)
    :param client_id: The client ID
    :param client_secret: The client secret
    :return: The request token
    """
    response = requests.post(f'{api_url}/request-token-sso', json={"appId": client_id, "appSecret": client_secret})
    return response.json()['requestToken']


def validate_token(api_url: str, success_token: str) -> Optional[OrgoUser]:
    """
    Validates the success token and retrieves user information
    :param api_url: The base API URL (no trailing slash)
    :param success_token: The success token retrieved from the frontend
    :return: The user information or None if the success token was invalid
    """
    response = requests.get(f'{api_url}/verify-success-token-sso?successToken={success_token}')
    if response.status_code != 200:
        return None
    return OrgoUser(response.json())


def logout(api_url: str, success_token: str) -> bool:
    """
    Logs out the user (does not work yet due to Authentication Server error)
    :param api_url: The base API URL (no trailing slash)
    :param success_token: The success token retrieved from the frontend
    :return: True if the user was logged out, false otherwise
    """
    # Could be: , headers={"Authorization": f"Bearer {success_token}"}
    response = requests.get(f'{api_url}/logout-sso?successToken={success_token}')
    print(f"Logout response: {response.json()}")
    return response.status_code == 200
