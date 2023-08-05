import datetime
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from legaltech_api_client.client import Client
from legaltech_api_client.models.activity import Activity
from legaltech_api_client.types import UNSET, Response, Unset


def _get_kwargs(
    claim_id: str,
    *,
    client: Client,
    created_at: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_gt: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_gte: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_lt: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_lte: Union[Unset, None, datetime.datetime] = UNSET,
    authorization: str,
) -> Dict[str, Any]:
    url = "{}/api/v1/claims/{claim_id}/activities/".format(client.base_url, claim_id=claim_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    headers["Authorization"] = authorization

    params: Dict[str, Any] = {}
    json_created_at: Union[Unset, None, str] = UNSET
    if not isinstance(created_at, Unset):
        json_created_at = created_at.isoformat() if created_at else None

    params["created_at"] = json_created_at

    json_created_at_gt: Union[Unset, None, str] = UNSET
    if not isinstance(created_at_gt, Unset):
        json_created_at_gt = created_at_gt.isoformat() if created_at_gt else None

    params["created_at__gt"] = json_created_at_gt

    json_created_at_gte: Union[Unset, None, str] = UNSET
    if not isinstance(created_at_gte, Unset):
        json_created_at_gte = created_at_gte.isoformat() if created_at_gte else None

    params["created_at__gte"] = json_created_at_gte

    json_created_at_lt: Union[Unset, None, str] = UNSET
    if not isinstance(created_at_lt, Unset):
        json_created_at_lt = created_at_lt.isoformat() if created_at_lt else None

    params["created_at__lt"] = json_created_at_lt

    json_created_at_lte: Union[Unset, None, str] = UNSET
    if not isinstance(created_at_lte, Unset):
        json_created_at_lte = created_at_lte.isoformat() if created_at_lte else None

    params["created_at__lte"] = json_created_at_lte

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, List[Activity]]]:
    if response.status_code == 201:
        response_201 = []
        _response_201 = response.json()
        for response_201_item_data in _response_201:
            response_201_item = Activity.from_dict(response_201_item_data)

            response_201.append(response_201_item)

        return response_201
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, List[Activity]]]:
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
    created_at: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_gt: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_gte: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_lt: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_lte: Union[Unset, None, datetime.datetime] = UNSET,
    authorization: str,
) -> Response[Union[Any, List[Activity]]]:
    """Get activities perform on a Claim.

    Args:
        claim_id (str):
        created_at (Union[Unset, None, datetime.datetime]):
        created_at_gt (Union[Unset, None, datetime.datetime]):
        created_at_gte (Union[Unset, None, datetime.datetime]):
        created_at_lt (Union[Unset, None, datetime.datetime]):
        created_at_lte (Union[Unset, None, datetime.datetime]):
        authorization (str):

    Returns:
        Response[Union[Any, List[Activity]]]
    """

    kwargs = _get_kwargs(
        claim_id=claim_id,
        client=client,
        created_at=created_at,
        created_at_gt=created_at_gt,
        created_at_gte=created_at_gte,
        created_at_lt=created_at_lt,
        created_at_lte=created_at_lte,
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
    created_at: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_gt: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_gte: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_lt: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_lte: Union[Unset, None, datetime.datetime] = UNSET,
    authorization: str,
) -> Optional[Union[Any, List[Activity]]]:
    """Get activities perform on a Claim.

    Args:
        claim_id (str):
        created_at (Union[Unset, None, datetime.datetime]):
        created_at_gt (Union[Unset, None, datetime.datetime]):
        created_at_gte (Union[Unset, None, datetime.datetime]):
        created_at_lt (Union[Unset, None, datetime.datetime]):
        created_at_lte (Union[Unset, None, datetime.datetime]):
        authorization (str):

    Returns:
        Response[Union[Any, List[Activity]]]
    """

    return sync_detailed(
        claim_id=claim_id,
        client=client,
        created_at=created_at,
        created_at_gt=created_at_gt,
        created_at_gte=created_at_gte,
        created_at_lt=created_at_lt,
        created_at_lte=created_at_lte,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    claim_id: str,
    *,
    client: Client,
    created_at: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_gt: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_gte: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_lt: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_lte: Union[Unset, None, datetime.datetime] = UNSET,
    authorization: str,
) -> Response[Union[Any, List[Activity]]]:
    """Get activities perform on a Claim.

    Args:
        claim_id (str):
        created_at (Union[Unset, None, datetime.datetime]):
        created_at_gt (Union[Unset, None, datetime.datetime]):
        created_at_gte (Union[Unset, None, datetime.datetime]):
        created_at_lt (Union[Unset, None, datetime.datetime]):
        created_at_lte (Union[Unset, None, datetime.datetime]):
        authorization (str):

    Returns:
        Response[Union[Any, List[Activity]]]
    """

    kwargs = _get_kwargs(
        claim_id=claim_id,
        client=client,
        created_at=created_at,
        created_at_gt=created_at_gt,
        created_at_gte=created_at_gte,
        created_at_lt=created_at_lt,
        created_at_lte=created_at_lte,
        authorization=authorization,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    claim_id: str,
    *,
    client: Client,
    created_at: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_gt: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_gte: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_lt: Union[Unset, None, datetime.datetime] = UNSET,
    created_at_lte: Union[Unset, None, datetime.datetime] = UNSET,
    authorization: str,
) -> Optional[Union[Any, List[Activity]]]:
    """Get activities perform on a Claim.

    Args:
        claim_id (str):
        created_at (Union[Unset, None, datetime.datetime]):
        created_at_gt (Union[Unset, None, datetime.datetime]):
        created_at_gte (Union[Unset, None, datetime.datetime]):
        created_at_lt (Union[Unset, None, datetime.datetime]):
        created_at_lte (Union[Unset, None, datetime.datetime]):
        authorization (str):

    Returns:
        Response[Union[Any, List[Activity]]]
    """

    return (
        await asyncio_detailed(
            claim_id=claim_id,
            client=client,
            created_at=created_at,
            created_at_gt=created_at_gt,
            created_at_gte=created_at_gte,
            created_at_lt=created_at_lt,
            created_at_lte=created_at_lte,
            authorization=authorization,
        )
    ).parsed
