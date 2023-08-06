# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import pytest
import numpy as np
from PySDM_examples.Lowe_et_al_2019 import Settings, Simulation, aerosol
from PySDM.initialisation.sampling import spectral_sampling
from PySDM.physics import si
from .constants import constants

assert hasattr(constants, '_pytestfixturefunction')


class TestFig2:
    @staticmethod
    @pytest.mark.parametrize("aerosol, surface_tension, s_max, n_final", (
        (aerosol.AerosolMarine(),  "Constant", .30, 140),
        (aerosol.AerosolMarine(),  "CompressedFilmOvadnevaite", .27, 160),
        (aerosol.AerosolBoreal(),  "Constant", .21, 395),
        (aerosol.AerosolBoreal(),  "CompressedFilmOvadnevaite", .16, 495),
        (aerosol.AerosolNascent(), "Constant", .42, 90),
        (aerosol.AerosolNascent(), "CompressedFilmOvadnevaite", .34, 150)
    ))
    # pylint: disable=redefined-outer-name,unused-argument
    def test_peak_supersaturation_and_final_concentration(
        constants, aerosol, surface_tension, s_max, n_final
    ):
        # arrange
        settings = Settings(
            dt=2 * si.s, n_sd_per_mode=32,
            model={'CompressedFilmOvadnevaite': 'film', 'Constant': 'bulk'}[surface_tension],
            aerosol=aerosol,
            spectral_sampling=spectral_sampling.ConstantMultiplicity
        )
        settings.output_interval = settings.t_max
        simulation = Simulation(settings)

        # act
        output = simulation.run()

        # assert
        assert len(output['S_max']) == 2
        np.testing.assert_approx_equal(output['S_max'][-1], s_max, significant=2)
        np.testing.assert_approx_equal(output['n_c_cm3'][-1], n_final, significant=2)
