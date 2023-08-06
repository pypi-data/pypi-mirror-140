import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.claim_metadata import ClaimMetadata
from ..models.current_state_enum import CurrentStateEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClaimRetrieve")


@attr.s(auto_attribs=True)
class ClaimRetrieve:
    """
    Attributes:
        id (str):
        product_id (str):
        network (str):
        url (str):
        is_assigned (str):
        current_state (Union[Unset, CurrentStateEnum]):
        user_requester (Union[Unset, None, str]):
        item_metadata (Union[Unset, ClaimMetadata]):
        notes (Union[Unset, None, str]):
        assignment_at (Union[Unset, None, datetime.datetime]):
    """

    id: str
    product_id: str
    network: str
    url: str
    is_assigned: str
    current_state: Union[Unset, CurrentStateEnum] = UNSET
    user_requester: Union[Unset, None, str] = UNSET
    item_metadata: Union[Unset, ClaimMetadata] = UNSET
    notes: Union[Unset, None, str] = UNSET
    assignment_at: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        product_id = self.product_id
        network = self.network
        url = self.url
        is_assigned = self.is_assigned
        current_state: Union[Unset, str] = UNSET
        if not isinstance(self.current_state, Unset):
            current_state = self.current_state.value

        user_requester = self.user_requester
        item_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.item_metadata, Unset):
            item_metadata = self.item_metadata.to_dict()

        notes = self.notes
        assignment_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.assignment_at, Unset):
            assignment_at = self.assignment_at.isoformat() if self.assignment_at else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "product_id": product_id,
                "network": network,
                "url": url,
                "is_assigned": is_assigned,
            }
        )
        if current_state is not UNSET:
            field_dict["current_state"] = current_state
        if user_requester is not UNSET:
            field_dict["user_requester"] = user_requester
        if item_metadata is not UNSET:
            field_dict["item_metadata"] = item_metadata
        if notes is not UNSET:
            field_dict["notes"] = notes
        if assignment_at is not UNSET:
            field_dict["assignment_at"] = assignment_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        product_id = d.pop("product_id")

        network = d.pop("network")

        url = d.pop("url")

        is_assigned = d.pop("is_assigned")

        _current_state = d.pop("current_state", UNSET)
        current_state: Union[Unset, CurrentStateEnum]
        if isinstance(_current_state, Unset):
            current_state = UNSET
        else:
            current_state = CurrentStateEnum(_current_state)

        user_requester = d.pop("user_requester", UNSET)

        _item_metadata = d.pop("item_metadata", UNSET)
        item_metadata: Union[Unset, ClaimMetadata]
        if isinstance(_item_metadata, Unset):
            item_metadata = UNSET
        else:
            item_metadata = ClaimMetadata.from_dict(_item_metadata)

        notes = d.pop("notes", UNSET)

        _assignment_at = d.pop("assignment_at", UNSET)
        assignment_at: Union[Unset, None, datetime.datetime]
        if _assignment_at is None:
            assignment_at = None
        elif isinstance(_assignment_at, Unset):
            assignment_at = UNSET
        else:
            assignment_at = isoparse(_assignment_at)

        claim_retrieve = cls(
            id=id,
            product_id=product_id,
            network=network,
            url=url,
            is_assigned=is_assigned,
            current_state=current_state,
            user_requester=user_requester,
            item_metadata=item_metadata,
            notes=notes,
            assignment_at=assignment_at,
        )

        claim_retrieve.additional_properties = d
        return claim_retrieve

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
