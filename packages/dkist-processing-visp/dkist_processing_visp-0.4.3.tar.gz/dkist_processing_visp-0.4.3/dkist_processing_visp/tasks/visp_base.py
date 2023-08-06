from abc import ABC

from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.fits import FitsDataMixin
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetMixin

from dkist_processing_visp.models.constants import VispConstants
from dkist_processing_visp.models.parameters import VispParameters


class VispTaskBase(WorkflowTaskBase, FitsDataMixin, InputDatasetMixin, ABC):
    @property
    def constants_model_class(self):
        return VispConstants

    def __init__(
        self,
        recipe_run_id: int,
        workflow_name: str,
        workflow_version: str,
    ):
        super().__init__(
            recipe_run_id=recipe_run_id,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
        )
        self.parameters = VispParameters(
            self.input_dataset_parameters, wavelength=self.constants.wavelength
        )
