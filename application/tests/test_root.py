import unittest

class SumofFirst5Numbers(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(sum([1]), 1, "Should be 1")
    def test_sum_tuple(self):
        self.assertEqual(sum([2]), 2, "Should be 2")

if __name__ == '__main__':
    unittest.main()