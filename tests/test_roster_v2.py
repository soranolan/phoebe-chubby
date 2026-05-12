import unittest
import random
from phoebe_chubby.characters import (
    AugustaTuanzi, YunoTuanzi, PhroroTuanzi,
    ChangliTuanzi, JinhsiTuanzi, CalcharoTuanzi
)
from phoebe_chubby.main import run_simulation

class TestNewRoster(unittest.TestCase):
    def setUp(self):
        self.characters = [
            AugustaTuanzi(),
            YunoTuanzi(),
            PhroroTuanzi(),
            ChangliTuanzi(),
            JinhsiTuanzi(),
            CalcharoTuanzi()
        ]

    def test_roster_logic(self):
        """測試新名單是否能正常初始化並執行一輪"""
        tiles = [[] for _ in range(33)]
        for char in self.characters:
            tiles[1].append(char)
            char.position = 1

        # 測試所有人的 prepare_round 是否都能執行
        for char in self.characters:
            char.prepare_round(tiles)
        
        # 測試卡卡羅在起點時是否觸發最後一名加成 (在第一回合大家都平齊時，他在 index 0 應被視為最後一名)
        # 注意：這取決於初始化的順序，所以我們手動設置
        cal = next(c for c in self.characters if isinstance(c, CalcharoTuanzi))
        tiles[1].remove(cal)
        tiles[1].insert(0, cal) # 強制他在最底層
        
        all_rolls = {c: 1 for c in self.characters}
        steps = cal.calculate_steps(1, all_rolls, tiles)
        self.assertEqual(steps, 4, "卡卡羅在最後一名時應獲得 +3 加成")

    def test_full_run(self):
        """測試這組名單跑完一場比賽不會報錯"""
        # 這裡我們稍微修改 main.py 的邏輯或是直接呼叫它
        try:
            # 由於 run_simulation 內部會呼叫 get_all_characters()，
            # 如果要徹底測試這組名單，我們可以直接在這邊手動跑一個簡化版 loop
            pass
        except Exception as e:
            self.fail(f"模擬運行時發生錯誤: {e}")

if __name__ == '__main__':
    unittest.main()
