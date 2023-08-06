""" Contains some shared types for properties """
from typing import Generic, MutableMapping, Optional, TypeVar

import attr


class Unset:
    def __bool__(self) -> bool:
        return False


UNSET: Unset = Unset()


T = TypeVar("T")


@attr.s(auto_attribs=True)
class Response(Generic[T]):
    """A response from an endpoint"""

    status_code: int
    content: bytes
    headers: MutableMapping[str, str]
    parsed: Optional[T]


__all__ = ["Response", ]
