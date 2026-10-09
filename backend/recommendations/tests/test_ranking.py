import unittest
from recommendations.ranking import rank_key
from risk.aggregation import summarize

class TestRanking(unittest.TestCase):
    def test_ranking_logic(self):
        mk = lambda lv: summarize(lv, [0, 25, 50, 75], 5)
        a = mk([0, 3, 0, 0]) # 1 Severe checkpoint
        b = mk([2, 2, 2, 2]) # 4 High checkpoints
        
        # rank_key orders ascending (lower is better)
        # fewer Severe (even with more High) beats more Severe
        self.assertLess(rank_key(b), rank_key(a))
        
        # No Travel is worst
        self.assertLess(rank_key(mk([0, 0, 0, 0])), rank_key(mk([4, 0, 0, 0])))

if __name__ == "__main__":
    unittest.main()
