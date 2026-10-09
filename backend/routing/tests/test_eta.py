import unittest
from datetime import datetime, timezone
from routing.eta import calculate_eta

class TestEta(unittest.TestCase):
    def test_calculate_eta(self):
        dep = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
        
        # exactly halfway through a 10 hour route
        eta = calculate_eta(dep, 10.0, 50.0, 100.0)
        self.assertEqual(eta.hour, 17) # 12 + (10 * 50 / 100) = 17
        
        # start of route
        eta = calculate_eta(dep, 10.0, 0.0, 100.0)
        self.assertEqual(eta.hour, 12)
        
        # zero total miles (avoid division by zero)
        eta = calculate_eta(dep, 10.0, 0.0, 0.0)
        self.assertEqual(eta, dep)

if __name__ == "__main__":
    unittest.main()
