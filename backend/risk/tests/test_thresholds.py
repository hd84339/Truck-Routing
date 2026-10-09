import unittest
from risk.classifier import level_for

class TestThresholds(unittest.TestCase):
    def test_wind_bands(self):
        # exact boundary checks
        self.assertEqual([level_for("wind", v) for v in (10, 24.9, 25, 34.9, 35, 44.9, 45, 54.9, 55, 60)], 
                         [0, 0, 1, 1, 2, 2, 3, 3, 4, 4])

    def test_rain_snow_bands(self):
        # exact boundary checks (upper edge is treated as the lower band)
        self.assertEqual([level_for("rain", v) for v in (0.09, 0.10, 0.24, 0.25, 0.49, 0.50, 0.99, 1.0, 1.01)], 
                         [0, 1, 1, 1, 2, 2, 3, 3, 4])
        self.assertEqual([level_for("snow", v) for v in (0.4, 0.5, 0.9, 1.0, 1.9, 2.0, 2.9, 3.0, 3.1)], 
                         [0, 1, 1, 1, 2, 2, 3, 3, 4])

if __name__ == "__main__":
    unittest.main()
