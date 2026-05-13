import sys
import unittest
sys.path.insert(0, "src")

from phoebe_chubby.analysis import run_single_analysis_match, run_batch_analysis

VALID_NAMES = {"奧古斯塔", "尤諾", "弗洛洛", "長離", "今汐", "卡卡羅"}


class TestSingleMatch(unittest.TestCase):

    def test_returns_valid_ranking(self):
        """單場比賽應回傳包含所有六名選手的完整排名"""
        ranking = run_single_analysis_match()
        self.assertIsInstance(ranking, list)
        self.assertEqual(len(ranking), 6)
        self.assertEqual(set(ranking), VALID_NAMES)

    def test_no_kingbu_in_ranking(self):
        """布大王不應出現在排名結果中"""
        for _ in range(20):
            ranking = run_single_analysis_match()
            self.assertNotIn("布大王", ranking)

    def test_multiple_runs_produce_variety(self):
        """100 場比賽中，第一名不應只有同一個角色"""
        first_place_winners = set()
        for _ in range(100):
            ranking = run_single_analysis_match()
            first_place_winners.add(ranking[0])
        self.assertGreaterEqual(
            len(first_place_winners), 2,
            f"100 場中第一名只有：{first_place_winners}，可能存在嚴重平衡問題"
        )

    def test_second_half_initial_states(self):
        """下半場起始狀態應正確傳入並影響比賽"""
        # 使用下半場的預設起始狀態 (dict 格式)
        second_half_states = {
            "奧古斯塔": {"pos": 32, "dist": 32},
            "尤諾":   {"pos": 32, "dist": 34},
            "弗洛洛": {"pos": 29, "dist": 35},
            "長離":   {"pos": 32, "dist": 32},
            "今汐":   {"pos": 31, "dist": 33},
            "卡卡羅": {"pos": 31, "dist": 33},
            "布大王": {"pos": 32, "dist": 999},
        }
        ranking = run_single_analysis_match(initial_states=second_half_states)
        self.assertEqual(set(ranking), VALID_NAMES)


class TestBatchAnalysis(unittest.TestCase):

    def test_completes_without_error(self):
        """批量分析應能正常跑完不拋出例外"""
        try:
            run_batch_analysis(num_trials=50)
        except Exception as e:
            self.fail(f"run_batch_analysis 拋出了例外：{e}")

    def test_second_half_mode(self):
        """下半場模式應能正常運行"""
        second_half_states = {
            "奧古斯塔": {"pos": 32, "dist": 32},
            "尤諾":   {"pos": 32, "dist": 34},
            "弗洛洛": {"pos": 29, "dist": 35},
            "長離":   {"pos": 32, "dist": 32},
            "今汐":   {"pos": 31, "dist": 33},
            "卡卡羅": {"pos": 31, "dist": 33},
            "布大王": {"pos": 32, "dist": 999},
        }
        try:
            run_batch_analysis(num_trials=50, initial_states=second_half_states)
        except Exception as e:
            self.fail(f"下半場模式拋出了例外：{e}")


if __name__ == "__main__":
    unittest.main()
