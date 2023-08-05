import numpy as np
from pystrict import strict
from PySDM import Formulae
from PySDM.initialisation.sampling import spectral_sampling as spec_sampling
from PySDM.physics import si
from PySDM_examples.Lowe_et_al_2019.aerosol import Aerosol


@strict
class Settings:
    def __init__(self, dt: float, n_sd_per_mode: int,
                 aerosol: Aerosol,
                 model: str,
                 spectral_sampling: type(spec_sampling.SpectralSampling),
                 ):
        assert model in ('bulk', 'film')
        self.model = model
        self.n_sd_per_mode = n_sd_per_mode
        self.formulae = Formulae(
            surface_tension='CompressedFilmOvadnevaite' if model == 'film' else 'Constant',
            constants={
                'sgm_org': 40 * si.mN / si.m,
                'delta_min': 0.1 * si.nm
            }
        )
        const = self.formulae.constants
        self.aerosol = aerosol
        self.spectral_sampling = spectral_sampling
        self.t_max = (400 + 196) * si.s
        self.output_interval = 10 * si.s
        self.dt = dt

        self.w = .32 * si.m / si.s
        self.g = 9.81 * si.m / si.s**2

        self.p0 = 980 * si.mbar
        self.T0 = 280 * si.K
        pv0 = .99 * self.formulae.saturation_vapour_pressure.pvs_Celsius(self.T0 - const.T0)
        self.q0 = const.eps * pv0 / (self.p0 - pv0)

        self.cloud_radius_range = (
                .5 * si.micrometre,
                np.inf
        )

        self.mass_of_dry_air = 44

        self.wet_radius_bins_edges = np.logspace(
            np.log10(4 * si.um),
            np.log10(12 * si.um),
            128+1,
            endpoint=True
        )

    @property
    def rho0(self):
        const = self.formulae.constants
        rhod0 = self.formulae.trivia.p_d(self.p0, self.q0) / self.T0 / const.Rd
        return rhod0 * (1 + self.q0)

    @property
    def nt(self):
        nt = self.t_max / self.dt
        assert nt == int(nt)
        return int(nt)

    @property
    def steps_per_output_interval(self) -> int:
        return int(self.output_interval / self.dt)

    @property
    def output_steps(self) -> np.ndarray:
        return np.arange(0, self.nt + 1, self.steps_per_output_interval)
