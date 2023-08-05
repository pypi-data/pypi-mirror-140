from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClaimMetadata")


@attr.s(auto_attribs=True)
class ClaimMetadata:
    """
    Attributes:
        item_country (Union[Unset, str]):
        item_title (Union[Unset, str]):
        item_vendor (Union[Unset, str]):
        item_price (Union[Unset, str]):
        item_currency (Union[Unset, str]):
        item_description (Union[Unset, str]):
        item_ref (Union[Unset, str]):
        user_verified (Union[Unset, bool]):
        screenshot (Union[Unset, str]):
        date_captured (Union[Unset, str]):
    """

    item_country: Union[Unset, str] = UNSET
    item_title: Union[Unset, str] = UNSET
    item_vendor: Union[Unset, str] = UNSET
    item_price: Union[Unset, str] = UNSET
    item_currency: Union[Unset, str] = UNSET
    item_description: Union[Unset, str] = UNSET
    item_ref: Union[Unset, str] = UNSET
    user_verified: Union[Unset, bool] = UNSET
    screenshot: Union[Unset, str] = UNSET
    date_captured: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        item_country = self.item_country
        item_title = self.item_title
        item_vendor = self.item_vendor
        item_price = self.item_price
        item_currency = self.item_currency
        item_description = self.item_description
        item_ref = self.item_ref
        user_verified = self.user_verified
        screenshot = self.screenshot
        date_captured = self.date_captured

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if item_country is not UNSET:
            field_dict["item_country"] = item_country
        if item_title is not UNSET:
            field_dict["item_title"] = item_title
        if item_vendor is not UNSET:
            field_dict["item_vendor"] = item_vendor
        if item_price is not UNSET:
            field_dict["item_price"] = item_price
        if item_currency is not UNSET:
            field_dict["item_currency"] = item_currency
        if item_description is not UNSET:
            field_dict["item_description"] = item_description
        if item_ref is not UNSET:
            field_dict["item_ref"] = item_ref
        if user_verified is not UNSET:
            field_dict["user_verified"] = user_verified
        if screenshot is not UNSET:
            field_dict["screenshot"] = screenshot
        if date_captured is not UNSET:
            field_dict["date_captured"] = date_captured

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        item_country = d.pop("item_country", UNSET)

        item_title = d.pop("item_title", UNSET)

        item_vendor = d.pop("item_vendor", UNSET)

        item_price = d.pop("item_price", UNSET)

        item_currency = d.pop("item_currency", UNSET)

        item_description = d.pop("item_description", UNSET)

        item_ref = d.pop("item_ref", UNSET)

        user_verified = d.pop("user_verified", UNSET)

        screenshot = d.pop("screenshot", UNSET)

        date_captured = d.pop("date_captured", UNSET)

        claim_metadata = cls(
            item_country=item_country,
            item_title=item_title,
            item_vendor=item_vendor,
            item_price=item_price,
            item_currency=item_currency,
            item_description=item_description,
            item_ref=item_ref,
            user_verified=user_verified,
            screenshot=screenshot,
            date_captured=date_captured,
        )

        claim_metadata.additional_properties = d
        return claim_metadata

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
