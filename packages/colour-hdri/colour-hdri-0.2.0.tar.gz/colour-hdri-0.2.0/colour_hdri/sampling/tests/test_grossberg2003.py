# !/usr/bin/env python
"""
Defines the unit tests for the :mod:`colour_hdri.sampling.grossberg2003`
module.
"""

from __future__ import annotations

import numpy as np
import os
import unittest

from colour.hints import List

from colour_hdri import TESTS_RESOURCES_DIRECTORY
from colour_hdri.sampling import samples_Grossberg2003
from colour_hdri.utilities import ImageStack, filter_files

__author__ = "Colour Developers"
__copyright__ = "Copyright 2015 Colour Developers"
__license__ = "New BSD License - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "FROBISHER_001_DIRECTORY",
    "SAMPLING_DIRECTORY",
    "JPG_IMAGES",
    "TestSamplesGrossberg2003",
]

FROBISHER_001_DIRECTORY: str = os.path.join(
    TESTS_RESOURCES_DIRECTORY, "frobisher_001"
)

SAMPLING_DIRECTORY: str = os.path.join(
    TESTS_RESOURCES_DIRECTORY, "colour_hdri", "sampling"
)

JPG_IMAGES: List[str] = filter_files(FROBISHER_001_DIRECTORY, ("jpg",))


class TestSamplesGrossberg2003(unittest.TestCase):
    """
    Define :func:`colour_hdri.sampling.grossberg2003.\
samples_Grossberg2003` definition unit tests methods.
    """

    def test_samples_Grossberg2003(self):
        """
        Test :func:`colour_hdri.sampling.grossberg2003.\
samples_Grossberg2003` definition.
        """

        np.testing.assert_almost_equal(
            samples_Grossberg2003(ImageStack.from_files(JPG_IMAGES).data),
            np.load(
                os.path.join(
                    SAMPLING_DIRECTORY, "test_samples_Grossberg2003.npy"
                )
            ),
            decimal=7,
        )


if __name__ == "__main__":
    unittest.main()
