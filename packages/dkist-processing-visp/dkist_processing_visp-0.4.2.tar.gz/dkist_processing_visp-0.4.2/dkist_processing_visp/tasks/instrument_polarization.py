import logging
from collections import defaultdict
from typing import Dict
from typing import List

import numpy as np
from astropy.io import fits
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_math.transform.binning import bin_arrays
from dkist_processing_pac import Data as pac_data
from dkist_processing_pac import FittingFramework
from dkist_processing_pac import GenerateDemodMatrices
from dkist_processing_pac import generic
from dkist_processing_pac.DKISTDC import data as dkistdc_data

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.mixin.corrections import CorrectionsMixin
from dkist_processing_visp.tasks.mixin.input_frame_loaders import InputFrameLoadersMixin
from dkist_processing_visp.tasks.mixin.intermediate_frame_helpers import (
    IntermediateFrameHelpersMixin,
)
from dkist_processing_visp.tasks.mixin.metadata import MetaDataMixin
from dkist_processing_visp.tasks.visp_base import VispTaskBase


class InstrumentPolarizationCalibration(
    VispTaskBase,
    IntermediateFrameHelpersMixin,
    InputFrameLoadersMixin,
    CorrectionsMixin,
    MetaDataMixin,
    QualityMixin,
):
    """
    Task class for instrument polarization for a VISP calibration run.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    record_provenance = True

    def run(self) -> None:
        """
        For each beam:
            - Reduce calibration sequence steps
            - Fit reduced data to PAC parameters
            - Compute and save demodulation matrices

        Returns
        -------
        None

        """
        # TODO: There might be a better way to skip this task
        if not self.constants.correct_for_polarization:
            return

        # Process the pol cal frames
        with self.apm_step("Iterate over beams"):
            for beam in range(1, self.constants.num_beams + 1):
                reduced_arrays = self.reduce_cs_steps(beam)
                with self.apm_step("Fit to PAC parameters"):
                    logging.info(f"Fit PAC parameters for beam {beam}")
                    telescope_db = generic.get_default_telescope_db()
                    dresser = pac_data.Dresser()
                    dresser.add_drawer(dkistdc_data.DCDrawer(reduced_arrays))
                    # TODO: Should we be specifying threads here???
                    dc_cmp, dc_tmp, dc_tm = FittingFramework.run_core(
                        dresser,
                        fit_TM=False,
                        threads=1,
                        telescope_db=telescope_db,
                        fit_mode=self.parameters.pac_fit_mode,
                        init_set=self.parameters.pac_init_set,
                        noprint=True,
                    )
                with self.apm_step("Compute and save demodulation matrices"):
                    logging.info(f"Computing demodulation matrices for beam {beam}")
                    demod_matrices = GenerateDemodMatrices.DC_main(dresser, dc_cmp, telescope_db)
                    # Reshaping the demodulation matrix to get rid of unit length dimensions
                    demod_matrices = demod_matrices.reshape((4, self.constants.num_modstates))
                    # Save the demod matrices as intermediate products
                    # TODO: FITS for now, but need to figure out if this is the final solution
                    self.intermediate_frame_helpers_write_arrays(
                        demod_matrices,
                        beam=beam,
                        task="DEMOD_MATRICES",
                    )

        with self.apm_step("Finding number of input polcal frames"):
            no_of_raw_polcal_frames: int = self.metadata_count_after_beam_split(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task("POLCAL"),
                ],
            )

        with self.apm_step("Sending polcal frame count for quality metric storage"):
            self.quality_store_task_type_counts(
                task_type="polcal", total_frames=no_of_raw_polcal_frames
            )

    def reduce_cs_steps(self, beam: int) -> Dict[int, List[VispL0FitsAccess]]:
        """
        Reduce all of the data for the cal sequence steps for this beam

        Parameters
        ----------
        beam
            The current beam being processed

        Returns
        -------
        Dict
            A Dict of calibrated and binned arrays for all the cs steps for this beam
        """
        # Create the dict to hold the results
        reduced_arrays = defaultdict(list)

        with self.apm_step("Iterate over the modulator states"):
            for modstate in range(1, self.constants.num_modstates + 1):
                with self.apm_step("Get geometric objects"):
                    angle = self.intermediate_frame_helpers_load_angle(beam=beam)
                    state_offset = self.intermediate_frame_helpers_load_state_offset(
                        beam=beam, modstate=modstate
                    )
                    spec_shift = self.intermediate_frame_helpers_load_spec_shift(beam=beam)
                for exp_time in self.constants.polcal_exposure_times:
                    # Put this loop here because the geometric objects will be constant across exposure times
                    logging.info(f"Loading dark for {exp_time = } and {beam = }")
                    try:
                        dark_array = self.intermediate_frame_helpers_load_dark_array(
                            beam, exposure_time=exp_time
                        )
                    except StopIteration:
                        raise ValueError(f"No matching dark found for {exp_time = } s")
                    with self.apm_step("Iterate over the cal sequence steps"):
                        for cs_step in range(self.constants.num_cs_steps):
                            reduced_arrays[cs_step].append(
                                self.reduce_single_step(
                                    beam,
                                    dark_array,
                                    modstate,
                                    cs_step,
                                    exp_time,
                                    angle,
                                    state_offset,
                                    spec_shift,
                                )
                            )
        return reduced_arrays

    def reduce_single_step(
        self,
        beam: int,
        dark_array: np.ndarray,
        modstate: int,
        cs_step: int,
        exp_time: float,
        angle: float,
        state_offset: np.ndarray,
        spec_shift: np.ndarray,
    ) -> VispL0FitsAccess:
        """
        Reduce a single calibration step for this beam, cs step and modulator state

        Parameters
        ----------
        beam
            The current beam being processed
        dark_array
            The dark array for the current beam
        modstate
            The current modulator state
        cs_step
            The current cal sequence step
        angle
            The beam angle for the current modstate
        state_offset
            The state offset for the current modstate
        spec_shift
            The spectral shift for the current modstate

        Returns
        -------
        The final reduced result for this single step
        """
        logging.info(f"Reducing {cs_step=} for {modstate=} and {beam=}")
        # Get the iterable of objects for this beam, cal seq step and mod state
        with self.apm_step("Get input inst pol cal object(s)"):
            # Get the headers and arrays as iterables
            pol_cal_headers = (
                obj.header
                for obj in self.input_frame_loaders_polcal_fits_access_generator(
                    beam=beam, modstate=modstate, cs_step=cs_step, exposure_time=exp_time
                )
            )
            pol_cal_arrays = (
                obj.data
                for obj in self.input_frame_loaders_polcal_fits_access_generator(
                    beam=beam, modstate=modstate, cs_step=cs_step, exposure_time=exp_time
                )
            )
        # Grab the 1st header
        avg_inst_pol_cal_header = next(pol_cal_headers)
        # Average the arrays (this works for a single array as well)
        avg_inst_pol_cal_array = average_numpy_arrays(pol_cal_arrays)
        with self.apm_step("Dark correct the array"):
            dark_corrected_array = subtract_array_from_arrays(avg_inst_pol_cal_array, dark_array)
        with self.apm_step("Solar gain correct the array"):
            solar_gain_array = self.intermediate_frame_helpers_load_solar_gain_array(
                beam=beam, modstate=modstate
            )
            gain_corrected_array = next(
                divide_arrays_by_array(dark_corrected_array, solar_gain_array)
            )
        with self.apm_step("Geo correct the array"):
            geo_corrected_array = self.corrections_correct_geometry(
                gain_corrected_array, -state_offset, angle
            )
        with self.apm_step("Perform spectral correction"):
            spectral_corrected_array = self.corrections_remove_spec_geometry(
                geo_corrected_array, spec_shift
            )
        with self.apm_step("Extract macro pixels"):
            # Extract the macro pixels
            bin_factors = (
                gain_corrected_array.shape[0] // self.constants.num_spectral_bins,
                gain_corrected_array.shape[1] // self.constants.num_spatial_bins,
            )
            binned_array = next(bin_arrays(spectral_corrected_array, bin_factors))
        with self.apm_step("Create VispL0FitsAccess object with result"):
            result = VispL0FitsAccess(
                fits.ImageHDU(binned_array[None, :, :], avg_inst_pol_cal_header), auto_squeeze=False
            )
        return result
