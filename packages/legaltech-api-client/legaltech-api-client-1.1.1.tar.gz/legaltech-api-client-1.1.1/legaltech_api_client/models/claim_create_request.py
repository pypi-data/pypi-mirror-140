import json
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union

import attr

from ..models.claim_metadata import ClaimMetadata
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClaimCreateRequest")


@attr.s(auto_attribs=True)
class ClaimCreateRequest:
    """
    Attributes:
        product (str):
        network (str):
        url (str):
        user_requester (Union[Unset, None, str]):
        item_metadata (Union[Unset, ClaimMetadata]):
    """

    product: str
    network: str
    url: str
    user_requester: Union[Unset, None, str] = UNSET
    item_metadata: Union[Unset, ClaimMetadata] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        product = self.product
        network = self.network
        url = self.url
        user_requester = self.user_requester
        item_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.item_metadata, Unset):
            item_metadata = self.item_metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "product": product,
                "network": network,
                "url": url,
            }
        )
        if user_requester is not UNSET:
            field_dict["user_requester"] = user_requester
        if item_metadata is not UNSET:
            field_dict["item_metadata"] = item_metadata

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        product = self.product if isinstance(self.product, Unset) else (None, str(self.product).encode(), "text/plain")
        network = self.network if isinstance(self.network, Unset) else (None, str(self.network).encode(), "text/plain")
        url = self.url if isinstance(self.url, Unset) else (None, str(self.url).encode(), "text/plain")
        user_requester = (
            self.user_requester
            if isinstance(self.user_requester, Unset)
            else (None, str(self.user_requester).encode(), "text/plain")
        )
        item_metadata: Union[Unset, Tuple[None, bytes, str]] = UNSET
        if not isinstance(self.item_metadata, Unset):
            item_metadata = (None, json.dumps(self.item_metadata.to_dict()).encode(), "application/json")

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {key: (None, str(value).encode(), "text/plain") for key, value in self.additional_properties.items()}
        )
        field_dict.update(
            {
                "product": product,
                "network": network,
                "url": url,
            }
        )
        if user_requester is not UNSET:
            field_dict["user_requester"] = user_requester
        if item_metadata is not UNSET:
            field_dict["item_metadata"] = item_metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        product = d.pop("product")

        network = d.pop("network")

        url = d.pop("url")

        user_requester = d.pop("user_requester", UNSET)

        _item_metadata = d.pop("item_metadata", UNSET)
        item_metadata: Union[Unset, ClaimMetadata]
        if isinstance(_item_metadata, Unset):
            item_metadata = UNSET
        else:
            item_metadata = ClaimMetadata.from_dict(_item_metadata)

        claim_create_request = cls(
            product=product,
            network=network,
            url=url,
            user_requester=user_requester,
            item_metadata=item_metadata,
        )

        claim_create_request.additional_properties = d
        return claim_create_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
