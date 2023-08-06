from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.data_import_description_config import DataImportDescriptionConfig
from ..models.data_source_details_request import DataSourceDetailsRequest
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateDataSourceRequest")


@attr.s(auto_attribs=True)
class CreateDataSourceRequest:
    """
    Attributes:
        data_import_description (Union[Unset, None, DataImportDescriptionConfig]):
        details (Union[Unset, None, DataSourceDetailsRequest]):
    """

    data_import_description: Union[Unset, None, DataImportDescriptionConfig] = UNSET
    details: Union[Unset, None, DataSourceDetailsRequest] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        data_import_description: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.data_import_description, Unset):
            data_import_description = self.data_import_description.to_dict() if self.data_import_description else None

        details: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict() if self.details else None

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if data_import_description is not UNSET:
            field_dict["dataImportDescription"] = data_import_description
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _data_import_description = d.pop("dataImportDescription", UNSET)
        data_import_description: Union[Unset, None, DataImportDescriptionConfig]
        if _data_import_description is None:
            data_import_description = None
        elif isinstance(_data_import_description, Unset):
            data_import_description = UNSET
        else:
            data_import_description = DataImportDescriptionConfig.from_dict(_data_import_description)

        _details = d.pop("details", UNSET)
        details: Union[Unset, None, DataSourceDetailsRequest]
        if _details is None:
            details = None
        elif isinstance(_details, Unset):
            details = UNSET
        else:
            details = DataSourceDetailsRequest.from_dict(_details)

        create_data_source_request = cls(
            data_import_description=data_import_description,
            details=details,
        )

        return create_data_source_request
