import datetime
from typing import Any, Dict, List, Type, TypeVar

import attr
from dateutil.parser import isoparse

T = TypeVar("T", bound="CreateProductServiceRequest")


@attr.s(auto_attribs=True)
class CreateProductServiceRequest:
    """
    Attributes:
        service (str):
        date_start (datetime.datetime):
        date_end (datetime.datetime):
    """

    service: str
    date_start: datetime.datetime
    date_end: datetime.datetime
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        service = self.service
        date_start = self.date_start.isoformat()

        date_end = self.date_end.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service": service,
                "date_start": date_start,
                "date_end": date_end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        service = d.pop("service")

        date_start = isoparse(d.pop("date_start"))

        date_end = isoparse(d.pop("date_end"))

        create_product_service_request = cls(
            service=service,
            date_start=date_start,
            date_end=date_end,
        )

        create_product_service_request.additional_properties = d
        return create_product_service_request

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
