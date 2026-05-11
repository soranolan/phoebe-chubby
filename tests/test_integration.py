import unittest
import random
from phoebe_chubby.models import Tuanzi
from phoebe_chubby.characters import KingBuTuanzi, ShorekeeperTuanzi

class TestGameIntegration(unittest.TestCase):
    def setUp(self):
        self.tiles = [[] for _ in range(33)]

    def test_map_trap_f1(self):
        """測試地圖前進陷阱 (f1)"""
        char = ShorekeeperTuanzi()
        char.position = 2
        self.tiles[2] = [char]
        
        # 模擬走 1 格踩到第 3 格 (f1)
        # 注意：陷阱邏輯在 main.py 的迴圈內，這裡我們模擬該行為
        char.move(1, self.tiles)
        if char.position == 3:
            # 觸發 f1 效果：再往前 1 格
            char.move(1, self.tiles)
            
        self.assertEqual(char.position, 4)

    def test_kingbu_infinite_loop(self):
        """測試布大王的無限循環重生邏輯"""
        kb = KingBuTuanzi()
        # 假設布大王已經殺回第 1 格
        kb.position = 1
        self.tiles[1] = [kb]
        
        # 模擬 main.py 中的重生檢查
        if kb.position == 1 and kb.direction == -1:
            self.tiles[1].remove(kb)
            kb.position = 32
            kb.insert_at_bottom = True
            self.tiles[32].insert(0, kb)
            
        self.assertEqual(kb.position, 32)
        self.assertEqual(self.tiles[32][0], kb) # 確認他在最下面

    def test_massive_stack_towing(self):
        """測試全體 7 人疊羅漢大移動"""
        chars = [ShorekeeperTuanzi() for i in range(7)]
        for i, c in enumerate(chars):
            c.name = f"團子{i}"
            c.position = 10
            
        self.tiles[10] = chars # 0 在最底，6 在最頂
        
        # 移動最底下的『團子0』
        chars[0].move(5, self.tiles)
        
        # 檢查是否所有人都在 15 格
        for c in chars:
            self.assertEqual(c.position, 15)
        
        # 檢查堆疊順序是否保持不變
        self.assertEqual(self.tiles[15], chars)
        self.assertEqual(len(self.tiles[10]), 0)

if __name__ == "__main__":
    unittest.main()
