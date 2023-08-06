from typing import Generator
from typing import Optional
from typing import TypeVar

import numpy as np
from dkist_processing_common.models.fits_access import FitsAccessBase

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess


class InputFrameLoadersMixin:
    """
    Mixin for methods that support easy loading of input frames
    """

    F = TypeVar("F", bound=FitsAccessBase)

    def input_frame_loaders_fits_access_generator(
        self,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        dsps_repeat: Optional[int] = None,
        raster_step: Optional[int] = None,
        task: Optional[str] = None,
        cs_step: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[F, None, None]:
        passed_args = locals()
        tags = [VispTag.input(), VispTag.frame()]
        for t, v in passed_args.items():
            if t not in ["self"] and v is not None:
                tags.append(getattr(VispTag, t)(v))

        frame_generator = self.fits_data_read_fits_access(tags, cls=VispL0FitsAccess)
        return frame_generator

    def input_frame_loaders_dark_array_generator(
        self, beam: Optional[int] = None, exposure_time: Optional[float] = None
    ) -> Generator[np.ndarray, None, None]:
        dark_array_fits_access = self.input_frame_loaders_fits_access_generator(
            task="DARK", beam=beam, exposure_time=exposure_time
        )
        return (array.data for array in dark_array_fits_access)

    def input_frame_loaders_lamp_gain_array_generator(
        self,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[np.ndarray, None, None]:
        lamp_gain_array_fits_access = self.input_frame_loaders_fits_access_generator(
            task="LAMP_GAIN", beam=beam, modstate=modstate, exposure_time=exposure_time
        )
        return (array.data for array in lamp_gain_array_fits_access)

    def input_frame_loaders_solar_gain_array_generator(
        self,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[np.ndarray, None, None]:
        solar_gain_array_fits_access = self.input_frame_loaders_fits_access_generator(
            task="SOLAR_GAIN", beam=beam, modstate=modstate, exposure_time=exposure_time
        )
        return (array.data for array in solar_gain_array_fits_access)

    def input_frame_loaders_observe_fits_access_generator(
        self,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        raster_step: Optional[int] = None,
        dsps_repeat: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[FitsAccessBase, None, None]:
        return self.input_frame_loaders_fits_access_generator(
            task="OBSERVE",
            beam=beam,
            modstate=modstate,
            raster_step=raster_step,
            dsps_repeat=dsps_repeat,
            exposure_time=exposure_time,
        )

    def input_frame_loaders_polcal_fits_access_generator(
        self,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        cs_step: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[FitsAccessBase, None, None]:
        return self.input_frame_loaders_fits_access_generator(
            task="POLCAL",
            beam=beam,
            modstate=modstate,
            cs_step=cs_step,
            exposure_time=exposure_time,
        )
