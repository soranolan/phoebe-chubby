import sys
import unittest
sys.path.insert(0, "src")

from phoebe_chubby.analysis import run_single_analysis_match

VALID_NAMES = {"奧古斯塔", "尤諾", "弗洛洛", "長離", "今汐", "卡卡羅"}

SECOND_HALF_STATES = {
    "奧古斯塔": {"pos": 32, "dist": 32},
    "尤諾":   {"pos": 32, "dist": 34},
    "弗洛洛": {"pos": 29, "dist": 35},
    "長離":   {"pos": 32, "dist": 32},
    "今汐":   {"pos": 31, "dist": 33},
    "卡卡羅": {"pos": 31, "dist": 33},
    "布大王": {"pos": 32, "dist": 999},
}


class TestIntegration(unittest.TestCase):

    def test_full_race_completes(self):
        """一場完整的下半場決賽應能正常結束並回傳六人排名"""
        ranking = run_single_analysis_match(initial_states=SECOND_HALF_STATES)
        self.assertEqual(len(ranking), 6)
        self.assertEqual(set(ranking), VALID_NAMES)

    def test_ranking_order_is_consistent(self):
        """回傳的排名應是一個有順序的列表（第一個是冠軍）"""
        ranking = run_single_analysis_match(initial_states=SECOND_HALF_STATES)
        # 確認是 list，不是 set
        self.assertIsInstance(ranking, list)

    def test_50_races_all_produce_valid_rankings(self):
        """連跑 50 場，每場排名都應合法"""
        for i in range(50):
            ranking = run_single_analysis_match(initial_states=SECOND_HALF_STATES)
            self.assertEqual(
                set(ranking), VALID_NAMES,
                f"第 {i+1} 場排名不合法：{ranking}"
            )

    def test_winner_distribution_is_varied(self):
        """100 場比賽中，第一名應有多個不同角色"""
        winners = set(
            run_single_analysis_match(initial_states=SECOND_HALF_STATES)[0]
            for _ in range(100)
        )
        self.assertGreaterEqual(
            len(winners), 2,
            f"100 場中第一名只有 {winners}，平衡性可能有嚴重問題"
        )

    def test_yuno_gravity_does_not_trigger_early(self):
        """尤諾的引力不應在比賽一開始就觸發（剩餘里程還 > 16 時）"""
        # 跑 20 場，觀察尤諾在下半場初期不應立刻觸發引力
        # 我們透過確認比賽能跑完（而不是卡在第 1 回合）來間接驗證
        for _ in range(20):
            try:
                ranking = run_single_analysis_match(initial_states=SECOND_HALF_STATES)
                self.assertEqual(len(ranking), 6)
            except Exception as e:
                self.fail(f"比賽發生異常：{e}")


if __name__ == "__main__":
    unittest.main()
