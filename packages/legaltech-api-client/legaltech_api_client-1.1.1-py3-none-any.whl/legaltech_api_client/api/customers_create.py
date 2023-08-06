from typing import Any, Dict, Optional, Union, cast

import httpx

from legaltech_api_client.client import Client
from legaltech_api_client.models.customer_create_request import CustomerCreateRequest
from legaltech_api_client.models.customer_create_response import CustomerCreateResponse
from legaltech_api_client.types import Response


def _get_kwargs(
    *,
    client: Client,
    form_data: CustomerCreateRequest,
    multipart_data: CustomerCreateRequest,
    json_body: CustomerCreateRequest,
    authorization: str,
) -> Dict[str, Any]:
    url = "{}/api/v1/customers/".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    headers["Authorization"] = authorization

    json_body.to_dict()

    multipart_data.to_multipart()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "data": form_data.to_dict(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, CustomerCreateResponse]]:
    if response.status_code == 200:
        response_200 = CustomerCreateResponse.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == 409:
        response_409 = cast(Any, None)
        return response_409
    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, CustomerCreateResponse]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    form_data: CustomerCreateRequest,
    multipart_data: CustomerCreateRequest,
    json_body: CustomerCreateRequest,
    authorization: str,
) -> Response[Union[Any, CustomerCreateResponse]]:
    """Create new Customer.

    Args:
        authorization (str):
        multipart_data (CustomerCreateRequest):
        json_body (CustomerCreateRequest):

    Returns:
        Response[Union[Any, CustomerCreateResponse]]
    """

    kwargs = _get_kwargs(
        client=client,
        form_data=form_data,
        multipart_data=multipart_data,
        json_body=json_body,
        authorization=authorization,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    form_data: CustomerCreateRequest,
    multipart_data: CustomerCreateRequest,
    json_body: CustomerCreateRequest,
    authorization: str,
) -> Optional[Union[Any, CustomerCreateResponse]]:
    """Create new Customer.

    Args:
        authorization (str):
        multipart_data (CustomerCreateRequest):
        json_body (CustomerCreateRequest):

    Returns:
        Response[Union[Any, CustomerCreateResponse]]
    """

    return sync_detailed(
        client=client,
        form_data=form_data,
        multipart_data=multipart_data,
        json_body=json_body,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    form_data: CustomerCreateRequest,
    multipart_data: CustomerCreateRequest,
    json_body: CustomerCreateRequest,
    authorization: str,
) -> Response[Union[Any, CustomerCreateResponse]]:
    """Create new Customer.

    Args:
        authorization (str):
        multipart_data (CustomerCreateRequest):
        json_body (CustomerCreateRequest):

    Returns:
        Response[Union[Any, CustomerCreateResponse]]
    """

    kwargs = _get_kwargs(
        client=client,
        form_data=form_data,
        multipart_data=multipart_data,
        json_body=json_body,
        authorization=authorization,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    form_data: CustomerCreateRequest,
    multipart_data: CustomerCreateRequest,
    json_body: CustomerCreateRequest,
    authorization: str,
) -> Optional[Union[Any, CustomerCreateResponse]]:
    """Create new Customer.

    Args:
        authorization (str):
        multipart_data (CustomerCreateRequest):
        json_body (CustomerCreateRequest):

    Returns:
        Response[Union[Any, CustomerCreateResponse]]
    """

    return (
        await asyncio_detailed(
            client=client,
            form_data=form_data,
            multipart_data=multipart_data,
            json_body=json_body,
            authorization=authorization,
        )
    ).parsed
