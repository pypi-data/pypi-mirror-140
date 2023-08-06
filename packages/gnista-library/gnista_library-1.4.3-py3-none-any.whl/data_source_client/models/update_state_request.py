from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateStateRequest")


@attr.s(auto_attribs=True)
class UpdateStateRequest:
    """
    Attributes:
        broken (Union[Unset, bool]):
    """

    broken: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        broken = self.broken

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if broken is not UNSET:
            field_dict["broken"] = broken

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        broken = d.pop("broken", UNSET)

        update_state_request = cls(
            broken=broken,
        )

        return update_state_request
