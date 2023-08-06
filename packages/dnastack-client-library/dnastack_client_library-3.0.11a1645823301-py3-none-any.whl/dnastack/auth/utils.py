from json import JSONDecodeError

import requests
from typing import AnyStr, Dict, Any
from urllib.parse import urlparse, urlunparse

from .oauth_client import OAuthClientParams, DEFAULT_AUTH_CLIENT
from ..exceptions import LoginException, RefreshException
from dnastack.helpers.logger import get_logger

logger = get_logger(__name__)


def get_audience_from_url(url: str) -> str:
    """
    Return the formatted audience from

    :param url: The url to generate an audience from
    :raises LoginException if an audience cannot be generated
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme in ("https", "drs"):
        return str(urlunparse(("https", parsed_url.netloc, "/", "", "", "")))
    else:
        raise LoginException(
            url=url,
            msg=f"Cannot get audience from url (scheme must be either 'https' or 'drs')",
        )


def login_refresh_token(
    token: AnyStr = None, oauth_client: OAuthClientParams = DEFAULT_AUTH_CLIENT
) -> Dict[AnyStr, Any]:
    """
    Generate an OAuth access token using an OAuth refresh token

    :param token: a dict containing the refresh token in the "refresh_token" field and optionally "scope"
    :param oauth_client: the parameters used to connect to
    :returns: A new token dict containing an access token
    :raises: RefreshException
    """
    if not token:
        raise RefreshException("The refresh token is missing")

    refresh_token_res = requests.post(
        oauth_client.token_url,
        data={
            "grant_type": "refresh_token",
            "refresh_token": token,
            "scope": oauth_client.scope,
        },
        auth=(oauth_client.client_id, oauth_client.client_secret),
    )

    if refresh_token_res.ok:
        fresh_token = refresh_token_res.json()
        return fresh_token
    else:
        error_msg = f"Unable to refresh token"
        try:
            error_json = refresh_token_res.json()
            error_msg += f": {error_json['error_description']}"
        except JSONDecodeError:
            pass

        raise RefreshException(url=oauth_client.base_url, msg=error_msg)
