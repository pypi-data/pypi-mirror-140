from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.data_import_description_config import DataImportDescriptionConfig
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateDataImportDescriptionRequest")


@attr.s(auto_attribs=True)
class UpdateDataImportDescriptionRequest:
    """
    Attributes:
        data_import_description (Union[Unset, None, DataImportDescriptionConfig]):
    """

    data_import_description: Union[Unset, None, DataImportDescriptionConfig] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        data_import_description: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.data_import_description, Unset):
            data_import_description = self.data_import_description.to_dict() if self.data_import_description else None

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if data_import_description is not UNSET:
            field_dict["dataImportDescription"] = data_import_description

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

        update_data_import_description_request = cls(
            data_import_description=data_import_description,
        )

        return update_data_import_description_request
