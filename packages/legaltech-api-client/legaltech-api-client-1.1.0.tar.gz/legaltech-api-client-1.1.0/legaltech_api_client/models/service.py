import datetime
from typing import Any, Dict, List, Type, TypeVar

import attr
from dateutil.parser import isoparse

from ..models.case import Case

T = TypeVar("T", bound="Service")


@attr.s(auto_attribs=True)
class Service:
    """
    Attributes:
        id (str):
        code (str):
        cases (List[Case]):
        created_at (datetime.datetime):
    """

    id: str
    code: str
    cases: List[Case]
    created_at: datetime.datetime
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        code = self.code
        cases = []
        for cases_item_data in self.cases:
            cases_item = cases_item_data.to_dict()

            cases.append(cases_item)

        created_at = self.created_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "code": code,
                "cases": cases,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        code = d.pop("code")

        cases = []
        _cases = d.pop("cases")
        for cases_item_data in _cases:
            cases_item = Case.from_dict(cases_item_data)

            cases.append(cases_item)

        created_at = isoparse(d.pop("created_at"))

        service = cls(
            id=id,
            code=code,
            cases=cases,
            created_at=created_at,
        )

        service.additional_properties = d
        return service

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
