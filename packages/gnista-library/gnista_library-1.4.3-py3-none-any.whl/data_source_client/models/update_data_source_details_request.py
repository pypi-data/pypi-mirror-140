from typing import Any, Dict, Type, TypeVar

import attr

from ..models.data_source_details_request import DataSourceDetailsRequest

T = TypeVar("T", bound="UpdateDataSourceDetailsRequest")


@attr.s(auto_attribs=True)
class UpdateDataSourceDetailsRequest:
    """
    Attributes:
        details (DataSourceDetailsRequest):
    """

    details: DataSourceDetailsRequest

    def to_dict(self) -> Dict[str, Any]:
        details = self.details.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "details": details,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        details = DataSourceDetailsRequest.from_dict(d.pop("details"))

        update_data_source_details_request = cls(
            details=details,
        )

        return update_data_source_details_request
