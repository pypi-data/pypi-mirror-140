"""Tests for the high-level CloudVolume wrapper.

Basically just tests whether creating a CloudVolume still works with the
current installation.
"""
import pytest

import cirrusvolume as cv


def test_creation(testcloudvolume):
    """Testing whether basic instantiation of a CirrusVolume works."""
    cirrusvolume = cv.CloudVolume(testcloudvolume.cloudpath)
    assert type(cirrusvolume) == cv.precomputed.CirrusVolumePrecomputed


def test_writeblocking(readvolume):
    """Tests whether writes that don't follow the rules raise an exception."""
    with pytest.raises(AssertionError):
        readvolume[0:10, 0:10, 0:10] = 0
