from typing import Any, Dict, Optional, Union, cast

import httpx

from legaltech_api_client.client import Client
from legaltech_api_client.models.claim_retrieve import ClaimRetrieve
from legaltech_api_client.types import Response


def _get_kwargs(
    claim_id: str,
    *,
    client: Client,
    authorization: str,
) -> Dict[str, Any]:
    url = "{}/api/v1/claims/{claim_id}/".format(client.base_url, claim_id=claim_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    headers["Authorization"] = authorization

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, ClaimRetrieve]]:
    if response.status_code == 200:
        response_200 = ClaimRetrieve.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, ClaimRetrieve]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    claim_id: str,
    *,
    client: Client,
    authorization: str,
) -> Response[Union[Any, ClaimRetrieve]]:
    """Get Claim details by ID

    Args:
        claim_id (str):
        authorization (str):

    Returns:
        Response[Union[Any, ClaimRetrieve]]
    """

    kwargs = _get_kwargs(
        claim_id=claim_id,
        client=client,
        authorization=authorization,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    claim_id: str,
    *,
    client: Client,
    authorization: str,
) -> Optional[Union[Any, ClaimRetrieve]]:
    """Get Claim details by ID

    Args:
        claim_id (str):
        authorization (str):

    Returns:
        Response[Union[Any, ClaimRetrieve]]
    """

    return sync_detailed(
        claim_id=claim_id,
        client=client,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    claim_id: str,
    *,
    client: Client,
    authorization: str,
) -> Response[Union[Any, ClaimRetrieve]]:
    """Get Claim details by ID

    Args:
        claim_id (str):
        authorization (str):

    Returns:
        Response[Union[Any, ClaimRetrieve]]
    """

    kwargs = _get_kwargs(
        claim_id=claim_id,
        client=client,
        authorization=authorization,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    claim_id: str,
    *,
    client: Client,
    authorization: str,
) -> Optional[Union[Any, ClaimRetrieve]]:
    """Get Claim details by ID

    Args:
        claim_id (str):
        authorization (str):

    Returns:
        Response[Union[Any, ClaimRetrieve]]
    """

    return (
        await asyncio_detailed(
            claim_id=claim_id,
            client=client,
            authorization=authorization,
        )
    ).parsed
