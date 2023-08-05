"""Unit tests for the CRD reader, making use of the `crd_file` fixture."""

from pathlib import Path

import pytest
import numpy as np

from rimseval.data_io.crd_reader import CRDReader


# TEST PROPERTIES #


def test_crd_reader_wrong_filetype():
    """Raise TypeError if file is not given as Path instance."""
    fname = "some_file.crd"
    with pytest.raises(TypeError) as err:
        CRDReader(fname)
    err_msg = err.value.args[0]
    assert err_msg == "Filename must be given as a valid Path using pathlib."


def test_crd_reader_header(crd_file):
    """Assert that the header of a crd file is read correctly."""
    hdr, _, _, fname = crd_file
    crd = CRDReader(Path(fname))
    assert crd.header == hdr


def test_crd_reader_all_data(crd_file):
    """Return all the data from the CRD file."""
    _, ions_per_shot, all_tofs, fname = crd_file
    crd = CRDReader(Path(fname))
    ret_ions_per_shot, ret_arrival_bins = crd.all_data
    np.testing.assert_equal(ions_per_shot, ret_ions_per_shot)
    np.testing.assert_equal(all_tofs, ret_arrival_bins)


def test_crd_all_tofs(crd_file):
    """Return all tof arrival bins."""
    _, _, all_tofs, fname = crd_file
    crd = CRDReader(Path(fname))
    np.testing.assert_equal(crd.all_tofs, all_tofs)


def test_crd_ions_per_shot(crd_file):
    """Return ions per shot array."""
    _, ions_per_shot, _, fname = crd_file
    crd = CRDReader(Path(fname))
    np.testing.assert_equal(crd.ions_per_shot, ions_per_shot)


def test_crd_nof_ions(crd_file):
    """Return number of ions."""
    _, ions_per_shot, _, fname = crd_file
    crd = CRDReader(Path(fname))
    assert crd.nof_ions == ions_per_shot.sum()


def test_crd_nof_shots(crd_file):
    """Return number of shots."""
    hdr, _, _, fname = crd_file
    crd = CRDReader(Path(fname))
    assert crd.nof_shots == hdr["nofShots"]
