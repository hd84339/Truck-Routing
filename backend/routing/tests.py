import unittest
from .risk import assess, level_for, summarize, rank_key


class RiskRules(unittest.TestCase):
    def test_wind_bands(self):
        self.assertEqual([level_for("wind", v) for v in (10, 25, 34.9, 35, 45, 54.9, 55)], [0, 1, 1, 2, 3, 3, 4])

    def test_rain_snow_bands(self):
        self.assertEqual([level_for("rain", v) for v in (0.09, 0.10, 0.3, 0.75, 1.0, 1.01)], [0, 1, 2, 3, 3, 4])
        self.assertEqual([level_for("snow", v) for v in (0.4, 0.5, 1.5, 2.5, 3.0, 3.1)], [0, 1, 2, 3, 3, 4])

    def test_load_rules(self):
        self.assertEqual(assess(55, 0, 0, 0)[0], 4)               # any load
        self.assertEqual(assess(50, 0, 0, 30001)[0], 4)
        self.assertEqual(assess(50, 0, 0, 30000)[0], 3)           # not >30k -> plain Severe
        self.assertEqual(assess(40, 0, 0, 40001)[0], 3)           # High -> Severe
        self.assertEqual(assess(40, 0, 0, 40000)[0], 2)

    def test_worst_condition_wins(self):
        self.assertEqual(assess(10, 0.6, 0.1, 0)[0], 3)

    def test_ranking(self):
        mk = lambda lv: summarize(lv, [0, 25, 50, 75], 5)
        a, b = mk([0, 3, 0, 0]), mk([2, 2, 2, 2])
        self.assertLess(rank_key(b), rank_key(a))                 # fewer Severe beats fewer High
        self.assertLess(rank_key(mk([0, 0, 0, 0])), rank_key(mk([4, 0, 0, 0])))


if __name__ == "__main__":
    unittest.main()
