import unittest
from phoebe_chubby.models import Tuanzi

class MockTuanzi(Tuanzi):
    def roll_dice(self) -> int:
        return 3

class TestTuanziMovement(unittest.TestCase):
    def setUp(self):
        # 模擬一個 32 格的地圖，每一格都是一個 list (堆疊)
        self.tiles = [[] for _ in range(33)]
        self.t1 = MockTuanzi(name="團子A", position=1)
        self.t2 = MockTuanzi(name="團子B", position=1)
        self.tiles[1] = [self.t1, self.t2] # A 在下，B 在上

    def test_basic_move(self):
        """測試單一團子的基礎移動"""
        # 讓 B 移動到第 5 格 (移動 4 格)
        self.t2.move(4, self.tiles)
        
        self.assertEqual(self.t2.position, 5)
        self.assertIn(self.t2, self.tiles[5])
        self.assertNotIn(self.t2, self.tiles[1])

    def test_stack_towing(self):
        """測試移動時是否帶動上方的團子 (Towing Effect)"""
        # 在第 10 格放置堆疊：A(底) -> B -> C(頂)
        t3 = MockTuanzi(name="團子C", position=10)
        self.t1.position = 10
        self.t2.position = 10
        self.tiles[10] = [self.t1, self.t2, t3]
        
        # 移動中間的 B 往後 2 格，應該帶動 C，但不帶動 A
        self.t2.move(2, self.tiles)
        
        self.assertEqual(self.t2.position, 12)
        self.assertEqual(t3.position, 12)
        self.assertEqual(self.t1.position, 10)
        
        # 檢查物理堆疊順序是否維持
        self.assertEqual(self.tiles[12], [self.t2, t3])
        self.assertEqual(self.tiles[10], [self.t1])

    def test_boundary_limit(self):
        """測試移動不會超出 1-32 格"""
        # 嘗試從 1 往回走 10 格
        self.t1.move(-10, self.tiles)
        self.assertEqual(self.t1.position, 1)
        
        # 嘗試從 30 往前走 10 格
        self.t1.position = 30
        self.tiles[30] = [self.t1]
        self.t1.move(10, self.tiles)
        self.assertEqual(self.t1.position, 32)

if __name__ == "__main__":
    unittest.main()
