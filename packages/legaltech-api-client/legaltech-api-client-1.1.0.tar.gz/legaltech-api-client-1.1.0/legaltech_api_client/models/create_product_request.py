import json
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union

import attr

from ..models.create_product_service_request import CreateProductServiceRequest
from ..models.product_metadata import ProductMetadata
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateProductRequest")


@attr.s(auto_attribs=True)
class CreateProductRequest:
    """
    Attributes:
        customer (str):
        name (str):
        alias (str):
        service_data (CreateProductServiceRequest):
        metadata (Union[Unset, ProductMetadata]):
    """

    customer: str
    name: str
    alias: str
    service_data: CreateProductServiceRequest
    metadata: Union[Unset, ProductMetadata] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        customer = self.customer
        name = self.name
        alias = self.alias
        service_data = self.service_data.to_dict()

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "customer": customer,
                "name": name,
                "alias": alias,
                "service_data": service_data,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        customer = (
            self.customer if isinstance(self.customer, Unset) else (None, str(self.customer).encode(), "text/plain")
        )
        name = self.name if isinstance(self.name, Unset) else (None, str(self.name).encode(), "text/plain")
        alias = self.alias if isinstance(self.alias, Unset) else (None, str(self.alias).encode(), "text/plain")
        service_data = (None, json.dumps(self.service_data.to_dict()).encode(), "application/json")

        metadata: Union[Unset, Tuple[None, bytes, str]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = (None, json.dumps(self.metadata.to_dict()).encode(), "application/json")

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {key: (None, str(value).encode(), "text/plain") for key, value in self.additional_properties.items()}
        )
        field_dict.update(
            {
                "customer": customer,
                "name": name,
                "alias": alias,
                "service_data": service_data,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        customer = d.pop("customer")

        name = d.pop("name")

        alias = d.pop("alias")

        service_data = CreateProductServiceRequest.from_dict(d.pop("service_data"))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ProductMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ProductMetadata.from_dict(_metadata)

        create_product_request = cls(
            customer=customer,
            name=name,
            alias=alias,
            service_data=service_data,
            metadata=metadata,
        )

        create_product_request.additional_properties = d
        return create_product_request

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
