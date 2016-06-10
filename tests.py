# import unittest
import utils as ut
import numpy as np


class TestUtils(object):
    def test_convolve_image(self):
        test_array = np.array([[2, 2, 2], [2, 8, 2], [2, 2, 2]])
        self.assertEquals(ut.convolve_image(test_array, ut.KN_ISOLATED_POINTS), 48)

    def test_tracker_positions(self):
        """
            0 0 255
            255 0 0
            255 255 255
        """
        test_array = np.array([[0, 0, 255], [255, 0, 0], [255, 255, 255]])

        trackers = []

        for y, row in enumerate(test_array):
            for x, col in enumerate(row):
                if col == 255:
                    find = ut.tracker_positions(test_array, (x, y))
                    find.sort()
                    if find not in trackers:
                        trackers.append(find)

        self.assertEquals(len(trackers), 2)