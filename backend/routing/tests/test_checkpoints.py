import unittest
from routing.checkpoints import sample_checkpoints

class TestCheckpoints(unittest.TestCase):
    def test_sample_checkpoints(self):
        geom = [(0, 0), (0, 1), (0, 2)]
        # This is roughly a straight line. If we request 1 mile intervals, it should place them correctly.
        # But we pass total_mi manually in this function. Let's say it's 10 miles long, step is 5.
        miles, pts = sample_checkpoints(geom, 10.0, 5.0)
        
        self.assertEqual(miles, [0.0, 5.0, 10.0])
        self.assertEqual(len(pts), 3)
        self.assertEqual(pts[0], geom[0]) # 0.0 is the start
        self.assertEqual(pts[-1], geom[-1]) # 10.0 is the end

if __name__ == "__main__":
    unittest.main()
