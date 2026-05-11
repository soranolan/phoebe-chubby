import unittest
from phoebe_chubby.analysis import run_single_race, run_batch_simulation
from io import StringIO
import sys

class TestBalanceAndAnalysis(unittest.TestCase):
    def test_single_race_returns_valid_winner(self):
        """測試單場比賽是否一定會產出合法的贏家"""
        winner = run_single_race()
        valid_names = ["千咲", "莫寧", "琳奈", "愛彌斯", "守岸人", "珂萊塔", "布大王", "平局"]
        self.assertIn(winner, valid_names)

    def test_batch_simulation_output(self):
        """測試批次模擬是否能跑完並產出報告"""
        # 攔截 print 輸出以驗證內容
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            run_batch_simulation(num_trials=100)
        finally:
            sys.stdout = sys.__stdout__
            
        output = captured_output.getvalue()
        self.assertIn("統計結果", output)
        self.assertIn("已完成 100 場", output)

    def test_multi_winner_distribution(self):
        """
        測試角色多樣性：
        在 100 場比賽中，不應該只有同一個角色獲勝（除非機率低到極致）。
        這個測試確保遊戲機制能讓多個角色都有機會勝出。
        """
        winners = set()
        for _ in range(100):
            winners.add(run_single_race())
        
        # 預期至少有 2 種以上的結果 (避免單一角色獨大或死當)
        self.assertGreaterEqual(len(winners), 2, f"警告：100 場比賽中只有贏家 {winners}，可能存在平衡性極端偏差！")

if __name__ == "__main__":
    unittest.main()
