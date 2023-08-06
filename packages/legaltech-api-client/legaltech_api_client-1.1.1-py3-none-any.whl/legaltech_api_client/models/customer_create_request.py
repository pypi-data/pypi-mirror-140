from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.blank_enum import BlankEnum
from ..models.country_enum import CountryEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomerCreateRequest")


@attr.s(auto_attribs=True)
class CustomerCreateRequest:
    """
    Attributes:
        name (str):
        email (str):
        matrix_company (Union[Unset, None, str]):
        country (Union[BlankEnum, CountryEnum, None, Unset]):
    """

    name: str
    email: str
    matrix_company: Union[Unset, None, str] = UNSET
    country: Union[BlankEnum, CountryEnum, None, Unset] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        email = self.email
        matrix_company = self.matrix_company
        country: Union[None, Unset, str]
        if isinstance(self.country, Unset):
            country = UNSET
        elif self.country is None:
            country = None

        elif isinstance(self.country, CountryEnum):
            country = UNSET
            if not isinstance(self.country, Unset):
                country = self.country.value

        elif isinstance(self.country, BlankEnum):
            country = UNSET
            if not isinstance(self.country, Unset):
                country = self.country.value

        else:
            country = self.country

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "email": email,
            }
        )
        if matrix_company is not UNSET:
            field_dict["matrix_company"] = matrix_company
        if country is not UNSET:
            field_dict["country"] = country

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        name = self.name if isinstance(self.name, Unset) else (None, str(self.name).encode(), "text/plain")
        email = self.email if isinstance(self.email, Unset) else (None, str(self.email).encode(), "text/plain")
        matrix_company = (
            self.matrix_company
            if isinstance(self.matrix_company, Unset)
            else (None, str(self.matrix_company).encode(), "text/plain")
        )
        country: Union[None, Unset, str]
        if isinstance(self.country, Unset):
            country = UNSET
        elif self.country is None:
            country = None

        elif isinstance(self.country, CountryEnum):
            country = UNSET
            if not isinstance(self.country, Unset):
                country = (None, str(self.country.value).encode(), "text/plain")

        elif isinstance(self.country, BlankEnum):
            country = UNSET
            if not isinstance(self.country, Unset):
                country = (None, str(self.country.value).encode(), "text/plain")

        else:
            country = self.country

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {key: (None, str(value).encode(), "text/plain") for key, value in self.additional_properties.items()}
        )
        field_dict.update(
            {
                "name": name,
                "email": email,
            }
        )
        if matrix_company is not UNSET:
            field_dict["matrix_company"] = matrix_company
        if country is not UNSET:
            field_dict["country"] = country

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        email = d.pop("email")

        matrix_company = d.pop("matrix_company", UNSET)

        def _parse_country(data: object) -> Union[BlankEnum, CountryEnum, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                _country_type_0 = data
                country_type_0: Union[Unset, CountryEnum]
                if isinstance(_country_type_0, Unset):
                    country_type_0 = UNSET
                else:
                    country_type_0 = CountryEnum(_country_type_0)

                return country_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                _country_type_1 = data
                country_type_1: Union[Unset, BlankEnum]
                if isinstance(_country_type_1, Unset):
                    country_type_1 = UNSET
                else:
                    country_type_1 = BlankEnum(_country_type_1)

                return country_type_1
            except:  # noqa: E722
                pass
            return cast(Union[BlankEnum, CountryEnum, None, Unset], data)

        country = _parse_country(d.pop("country", UNSET))

        customer_create_request = cls(
            name=name,
            email=email,
            matrix_company=matrix_company,
            country=country,
        )

        customer_create_request.additional_properties = d
        return customer_create_request

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
