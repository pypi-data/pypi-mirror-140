import pytest

from edges_analysis.analysis.calibrate import LabCalibration
from edges_cal import Calibration
from edges_cal.modelling import LinLog
from pathlib import Path
from scipy import stats

from edges_estimate.eor_models import AbsorptionProfile


@pytest.fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def calobs(data_path) -> Calibration:
    return Calibration(data_path / "test-calfile.h5")


@pytest.fixture(scope="session")
def labcal(calobs, data_path) -> Calibration:
    return LabCalibration(calobs=calobs, s11_files=sorted(data_path.glob("*.s1p")))


@pytest.fixture(scope="session")
def calobs12(data_path) -> Calibration:
    """Calobs with 12 c/w terms."""
    return Calibration(data_path / "test-calfile-12.h5")


@pytest.fixture(scope="session")
def labcal12(calobs12, data_path) -> Calibration:
    return LabCalibration(calobs=calobs12, s11_files=sorted(data_path.glob("*.s1p")))


@pytest.fixture(scope="session")
def fiducial_eor(calobs):
    return AbsorptionProfile(
        freqs=calobs.freq.freq,
        params={
            "A": {
                "fiducial": 0.5,
                "min": 0,
                "max": 1.5,
                "ref": stats.norm(0.5, scale=0.01),
            },
            "w": {
                "fiducial": 15,
                "min": 5,
                "max": 25,
                "ref": stats.norm(15, scale=0.1),
            },
            "tau": {
                "fiducial": 5,
                "min": 0,
                "max": 20,
                "ref": stats.norm(5, scale=0.1),
            },
            "nu0": {
                "fiducial": 78,
                "min": 60,
                "max": 90,
                "ref": stats.norm(78, scale=0.1),
            },
        },
    )


@pytest.fixture(scope="function")
def fiducial_fg():
    return LinLog(n_terms=5, parameters=[2000, 10, -10, 5, -5])
