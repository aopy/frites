"""Test definition of electrophysiological datasets."""
import numpy as np

from frites.dataset import DatasetEphy
from frites.simulations import sim_multi_suj_ephy, sim_mi_cc
from frites.io import set_log_level


set_log_level(False)


class TestDatasetEphy(object):  # noqa

    @staticmethod
    def _get_data(n_subjects=5, n_times=50, n_roi=6, n_epochs=10,
                  n_sites_per_roi=1):
        data, roi, time = sim_multi_suj_ephy(
            modality="meeg", n_times=n_times, n_roi=n_roi, n_epochs=n_epochs,
            n_subjects=n_subjects, random_state=0,
            n_sites_per_roi=n_sites_per_roi)
        data = [k + 100 for k in data]
        y, _ = sim_mi_cc(data, snr=.8)
        z = [np.random.randint(0, 3, (10,)) for _ in range(len(y))]
        dt = DatasetEphy(data, y, roi, z=z, times=time)
        return dt

    def test_definition(self):
        """Test function definition."""
        # test array definition
        data, roi, time = sim_multi_suj_ephy(modality="intra", n_times=57,
                                             n_roi=5, n_sites_per_roi=7,
                                             n_epochs=10, n_subjects=5,
                                             random_state=0)
        y, _ = sim_mi_cc(data, snr=.8)
        z = [np.random.randint(0, 3, (10,)) for _ in range(len(y))]
        DatasetEphy(data, y, roi, z=z, times=time)
        # test mne definition
        data, roi, time = sim_multi_suj_ephy(modality="meeg", n_times=57,
                                             n_roi=5, n_sites_per_roi=1,
                                             n_epochs=7, n_subjects=5,
                                             as_mne=True, random_state=0)
        y, _ = sim_mi_cc(data, snr=.8)
        DatasetEphy(data, y, roi, times=time)

    def test_shapes(self):
        """Test function shapes."""
        dt = self._get_data()
        assert dt._groupedby == "subject"
        # shape checking before groupby
        assert len(dt.x) == len(dt.y) == len(dt.z) == 5
        n_suj = len(dt.x)
        assert all([dt.x[k].shape == (6, 50, 10) for k in range(n_suj)])
        assert all([dt.y[k].shape == (10,) for k in range(n_suj)])
        assert all([dt.z[k].shape == (10,) for k in range(n_suj)])
        # group by roi
        dt.groupby('roi')
        assert dt._groupedby == "roi"
        assert len(dt.x) == len(dt.y) == len(dt.z) == 6
        assert all([dt.x[k].shape == (50, 1, 50) for k in range(n_suj)])
        assert all([dt.y[k].shape == (50,) for k in range(n_suj)])
        assert all([dt.z[k].shape == (50, 1) for k in range(n_suj)])
        assert all([dt.suj_roi[k].shape == (50,) for k in range(n_suj)])
        assert all([dt.suj_roi_u[k].shape == (5,) for k in range(n_suj)])
        assert len(dt.roi_names) == 6

    def test_copnorm(self):
        """Test function copnorm."""
        dt = self._get_data()
        dt.groupby('roi')
        assert dt._copnormed is False
        # be sure that data are centered around 100
        assert 95 < np.ravel(dt.x).mean() < 105
        dt.copnorm()
        assert isinstance(dt._copnormed, str)
        assert -1 < np.ravel(dt.x).mean() < 1

    def test_properties(self):
        """Test function properties."""
        dt = self._get_data()
        assert dt.modality == "electrophysiological"
        x, y, z = dt.x, dt.y, dt.z  # noqa
        # test setting x
        try: dt.x = 2  # noqa
        except AttributeError: pass  # noqa
        # test setting y
        try: dt.y = 2  # noqa
        except AttributeError: pass  # noqa
        # test setting z
        try: dt.z = 2  # noqa
        except AttributeError: pass  # noqa
        # shape // nb_min_suj
        assert isinstance(dt.shape, str)
        dt.nb_min_suj

    def test_builtin(self):
        """Test function builtin."""
        dt = self._get_data()
        # __len__
        assert len(dt) == 5
        # __repr__
        repr(dt)
        str(dt)
        # __getitem__
        assert np.array_equal(dt.x[0], dt[0])