"""Test khoi dong: package import duoc va set_seed chay khong loi."""

import nsmgat
from nsmgat.utils.seed import set_seed


def test_import_package():
    assert nsmgat is not None


def test_set_seed_runs():
    set_seed(42)
