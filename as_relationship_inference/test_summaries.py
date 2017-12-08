#!/usr/bin/env python
# Author: Ruediger Birkner (Networked Systems Group at ETH Zurich)

import unittest

from gao_algorithms import basic_heuristic, refined_heuristic
from sark_algorithms import compute_as_ranking, compute_equal, compute_larger, inference_heuristic


class TestGao(unittest.TestCase):
    pass


class TestSARK(unittest.TestCase):
    # COMPUTE EQUAL
    def test_compute_equal1(self):
        rank_vector = [9, 9, 9, 9]
        self.assertEqual(compute_equal(rank_vector, rank_vector), 4, 'wrong count for equal rank vectors')

    def test_compute_equal2(self):
        rank_vector1 = [9, 9, 9, 9]
        rank_vector2 = [1, 1, 1, 1]
        self.assertEqual(compute_equal(rank_vector1, rank_vector2), 0, 'wrong count for equal rank vectors')

    def test_compute_equal3(self):
        rank_vector1 = [9, 9, 9, 9]
        rank_vector2 = [1, 1, 9, 9]
        self.assertEqual(compute_equal(rank_vector1, rank_vector2), 2, 'wrong count for equal rank vectors')

    def test_compute_equal4(self):
        rank_vector1 = [9, 9, 9, 9]
        rank_vector2 = [9, 1, 9, 1]
        self.assertEqual(compute_equal(rank_vector1, rank_vector2), 2, 'wrong count for equal rank vectors')

    # COMPUTE LARGER
    def test_compute_larger1(self):
        rank_vector = [9, 9, 9, 9]
        self.assertEqual(compute_larger(rank_vector, rank_vector), 0, 'wrong count for equal rank vectors')

    def test_compute_larger2(self):
        rank_vector1 = [9, 9, 9, 9]
        rank_vector2 = [1, 1, 1, 1]
        self.assertEqual(compute_larger(rank_vector1, rank_vector2), 4, 'wrong count for equal rank vectors')

    def test_compute_larger3(self):
        rank_vector1 = [9, 9, 9, 9]
        rank_vector2 = [1, 1, 9, 9]
        self.assertEqual(compute_larger(rank_vector1, rank_vector2), 2, 'wrong count for equal rank vectors')

    def test_compute_larger4(self):
        rank_vector1 = [9, 9, 9, 9]
        rank_vector2 = [9, 1, 9, 1]
        self.assertEqual(compute_larger(rank_vector1, rank_vector2), 2, 'wrong count for equal rank vectors')

    def test_compute_larger5(self):
        rank_vector1 = [9, 1, 9, 1]
        rank_vector2 = [9, 9, 9, 9]
        self.assertEqual(compute_larger(rank_vector1, rank_vector2), 0, 'wrong count for equal rank vectors')


if __name__ == '__main__':
    unittest.main()
