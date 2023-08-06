from abc import ABC

from dkist_processing_common.tasks import WorkflowTaskBase

from dkist_processing_vbi.models.constants import VbiConstants


class VbiTaskBase(WorkflowTaskBase, ABC):
    @property
    def constants_model_class(self):
        return VbiConstants
