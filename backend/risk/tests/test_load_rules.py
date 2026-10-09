import unittest
from risk.classifier import assess

class TestLoadRules(unittest.TestCase):
    def test_load_rules(self):
        # >55 mph wind is No Travel (4) for any load
        self.assertEqual(assess(55, 0, 0, 0)[0], 4)
        
        # 45-54 mph wind with load > 30000 is No Travel (4)
        self.assertEqual(assess(50, 0, 0, 30001)[0], 4)
        
        # 45-54 mph wind with load <= 30000 is Severe (3)
        self.assertEqual(assess(50, 0, 0, 30000)[0], 3)
        
        # 35-44 mph wind with load > 40000 is Severe (3)
        self.assertEqual(assess(40, 0, 0, 40001)[0], 3)
        
        # 35-44 mph wind with load <= 40000 is High (2)
        self.assertEqual(assess(40, 0, 0, 40000)[0], 2)
        
    def test_worst_condition_wins(self):
        # rain alone would be 3 (Severe: 0.6 >= 0.50), wind is 10 (0), snow is 0.1 (0) -> max is 3
        self.assertEqual(assess(10, 0.6, 0.1, 0)[0], 3)
        
        # wind alone would be 3 (Severe: 45), rain 0, snow 0 -> max is 3
        self.assertEqual(assess(45, 0, 0, 30000)[0], 3)

if __name__ == "__main__":
    unittest.main()
