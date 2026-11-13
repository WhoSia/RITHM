import unittest

import numpy as np

from r40_default_horizon import transition, trajectory


class DefaultHorizonTests(unittest.TestCase):
    def test_probabilities(self):
        for schedule in (0, .25, .5, .75, 1):
            matrix = transition(.6, .5, schedule)
            np.testing.assert_allclose(matrix.sum(axis=1), 1)
            self.assertTrue(np.all(matrix >= 0))

    def test_first_period_single_revision(self):
        matrix = transition(.6, .5, 0)
        cost, hits = trajectory(matrix, 3, 1)
        self.assertAlmostEqual(hits[0], matrix[3, 4])
        self.assertAlmostEqual(cost[0], 12*matrix[3, 2]+3*matrix[3, 3])
        self.assertEqual(trajectory(matrix, 4, 39)[1], [1.]*39)

    def test_scheduling_can_reverse_default_effect(self):
        def change(n, schedule):
            treated, _ = trajectory(transition(1.5, .5, schedule), n, 1)
            control, _ = trajectory(transition(1.5, 0, schedule), n, 1)
            return treated[0]-control[0]
        for n in (3, 5):
            self.assertGreater(change(n, 0), 0)
            self.assertLess(change(n, 1), 0)
        for schedule in (0, 1):
            self.assertLess(change(4, schedule), 0)
