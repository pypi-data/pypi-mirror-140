import logging
from typing import Generator
from typing import Iterable
from typing import Optional
from typing import TypeVar
from typing import Union

import numpy as np
from astropy.io import fits
from dkist_processing_common.models.fits_access import FitsAccessBase

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess


class IntermediateFrameHelpersMixin:
    """
    Mixin for methods that support easy loading and writing of intermediate frames.
    """

    F = TypeVar("F", bound=FitsAccessBase)

    def intermediate_frame_helpers_load_intermediate_arrays(
        self,
        beam: Optional[int] = None,
        task: Optional[str] = None,
        modstate: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[np.ndarray, None, None]:
        """
        Yield a generator that produces ndarrays for the requested tags
        """
        # See intermediate_frame_helpers_write_arrays for an explanation of how this works, to add new tags *all* that's needed
        # is to add a kwarg that has the same name as a tag
        passed_args = locals()
        tags = [VispTag.intermediate(), VispTag.frame()]
        for t, v in passed_args.items():
            if t not in ["self"] and v is not None:
                tags.append(getattr(VispTag, t)(v))

        for path, hdu in self.fits_data_read_hdu(tags=tags):
            yield hdu.data

    def intermediate_frame_helpers_load_dark_array(
        self, beam: Optional[int] = None, exposure_time: Optional[float] = None
    ) -> np.ndarray:
        return next(
            self.intermediate_frame_helpers_load_intermediate_arrays(
                beam=beam, task="DARK", exposure_time=exposure_time
            )
        )

    def intermediate_frame_helpers_load_lamp_gain_array(
        self, beam: Optional[int] = None, modstate: Optional[int] = None
    ) -> np.ndarray:
        return next(
            self.intermediate_frame_helpers_load_intermediate_arrays(
                beam=beam, task="LAMP_GAIN", modstate=modstate
            )
        )

    def intermediate_frame_helpers_load_solar_gain_array(
        self, beam: Optional[int] = None, modstate: Optional[int] = None
    ) -> np.ndarray:
        return next(
            self.intermediate_frame_helpers_load_intermediate_arrays(
                beam=beam, task="SOLAR_GAIN", modstate=modstate
            )
        )

    def intermediate_frame_helpers_load_demodulated_arrays(
        self, beam: Optional[int] = None, modstate: Optional[int] = None
    ) -> Generator[np.ndarray, None, None]:
        return self.intermediate_frame_helpers_load_intermediate_arrays(
            beam=beam, task="DEMODULATED_ARRAYS", modstate=modstate
        )

    def intermediate_frame_helpers_write_arrays(
        self,
        arrays: Union[Iterable[np.ndarray], np.ndarray],
        headers: Optional[Union[Iterable[fits.Header], fits.Header]] = None,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        dsps_repeat: Optional[int] = None,
        raster_step: Optional[int] = None,
        task: Optional[str] = None,
        exposure_time: Optional[float] = None,
    ) -> None:
        # To add a new tag all you need to do is add a kwarg that has the same name as a tag. That's it!
        ## Construct the tags based on which optional parameters were passed
        passed_args = locals()
        tags = [VispTag.intermediate(), VispTag.frame()]
        for t, v in passed_args.items():
            # Look at all the arguments passed to this function, ignore those that aren't tags
            # and update tags with those that aren't None
            if t not in ["self", "arrays", "headers"] and v is not None:
                tags.append(getattr(VispTag, t)(v))

        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        if headers is not None:
            headers = [headers] if isinstance(headers, fits.Header) else headers
        else:
            headers = [None] * len(arrays)

        for array, header in zip(arrays, headers):
            hdul = fits.HDUList([fits.PrimaryHDU(data=array, header=header)])
            self.fits_data_write(hdu_list=hdul, tags=tags)

        filenames = [str(p) for p in self.read(tags=tags)]
        logging.info(f"Wrote intermediate file for {tags = } to {filenames}")

    def intermediate_frame_helpers_load_demod_matrices(self, beam_num: int) -> np.ndarray:
        tags = [
            VispTag.intermediate(),
            VispTag.task("DEMOD_MATRICES"),
            VispTag.beam(beam_num),
        ]
        path, hdu = next(self.fits_data_read_hdu(tags=tags))
        return hdu.data

    def intermediate_frame_helpers_fits_access_generator(
        self,
        tags: Iterable[str],
    ) -> Generator[F, None, None]:
        tags += [VispTag.intermediate(), VispTag.frame()]
        frame_generator = self.fits_data_read_fits_access(tags, cls=VispL0FitsAccess)
        return frame_generator

    def intermediate_frame_helpers_load_angle(self, beam: int) -> float:
        angle_array = next(
            self.intermediate_frame_helpers_load_intermediate_arrays(
                beam=beam, task="GEOMETRIC_ANGLE"
            )
        )
        return angle_array[0]

    def intermediate_frame_helpers_load_state_offset(self, beam: int, modstate: int) -> np.ndarray:
        offset = next(
            self.intermediate_frame_helpers_load_intermediate_arrays(
                beam=beam, task="GEOMETRIC_OFFSET", modstate=modstate
            )
        )
        return offset

    def intermediate_frame_helpers_load_spec_shift(self, beam: int) -> np.ndarray:
        shifts = next(
            self.intermediate_frame_helpers_load_intermediate_arrays(
                beam=beam, task="GEOMETRIC_SPEC_SHIFTS"
            )
        )
        return shifts
