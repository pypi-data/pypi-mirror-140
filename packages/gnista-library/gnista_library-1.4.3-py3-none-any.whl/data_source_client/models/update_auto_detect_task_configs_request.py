from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.auto_detect_task_config import AutoDetectTaskConfig
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateAutoDetectTaskConfigsRequest")


@attr.s(auto_attribs=True)
class UpdateAutoDetectTaskConfigsRequest:
    """
    Attributes:
        auto_detect_task_configs (Union[Unset, None, List[AutoDetectTaskConfig]]):
    """

    auto_detect_task_configs: Union[Unset, None, List[AutoDetectTaskConfig]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        auto_detect_task_configs: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.auto_detect_task_configs, Unset):
            if self.auto_detect_task_configs is None:
                auto_detect_task_configs = None
            else:
                auto_detect_task_configs = []
                for auto_detect_task_configs_item_data in self.auto_detect_task_configs:
                    auto_detect_task_configs_item = auto_detect_task_configs_item_data.to_dict()

                    auto_detect_task_configs.append(auto_detect_task_configs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if auto_detect_task_configs is not UNSET:
            field_dict["autoDetectTaskConfigs"] = auto_detect_task_configs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        auto_detect_task_configs = []
        _auto_detect_task_configs = d.pop("autoDetectTaskConfigs", UNSET)
        for auto_detect_task_configs_item_data in _auto_detect_task_configs or []:
            auto_detect_task_configs_item = AutoDetectTaskConfig.from_dict(auto_detect_task_configs_item_data)

            auto_detect_task_configs.append(auto_detect_task_configs_item)

        update_auto_detect_task_configs_request = cls(
            auto_detect_task_configs=auto_detect_task_configs,
        )

        return update_auto_detect_task_configs_request
