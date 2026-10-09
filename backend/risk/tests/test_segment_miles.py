import unittest
from risk.aggregation import summarize
from risk.segment_miles import get_segment_weights

class TestAggregation(unittest.TestCase):
    def test_segment_weights(self):
        # 3 points: start, middle, end. Middle owns half of first gap, half of second gap.
        weights = get_segment_weights([0, 25, 50, 75])
        self.assertEqual(weights, [12.5, 25.0, 25.0, 12.5])
        
        # 2 points
        weights = get_segment_weights([0, 10])
        self.assertEqual(weights, [5.0, 5.0])
        
        # 1 point
        weights = get_segment_weights([0])
        self.assertEqual(weights, [0.0])

    def test_aggregation(self):
        # 4 checkpoints at 0, 25, 50, 75 miles
        # levels: 0 (Low), 3 (Severe), 0 (Low), 0 (Low)
        s = summarize([0, 3, 0, 0], [0, 25, 50, 75], 5)
        
        self.assertEqual(s["severe_mi"], 25.0) # checkpoint at 25 mi owns [12.5, 37.5], which is 25 miles
        self.assertEqual(s["no_travel_mi"], 0.0)
        self.assertEqual(s["high_mi"], 0.0)
        self.assertEqual(s["max_level"], 3)
        self.assertEqual(s["duration_h"], 5.0)

if __name__ == "__main__":
    unittest.main()
