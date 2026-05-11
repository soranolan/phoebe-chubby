import unittest
from phoebe_chubby.characters import (
    ChisakiTuanzi, MorningTuanzi, AmisTuanzi, KingBuTuanzi, ShorekeeperTuanzi
)

class TestCharacterSkills(unittest.TestCase):
    def setUp(self):
        self.tiles = [[] for _ in range(33)]

    def test_chisaki_bonus(self):
        """測試千咲的最小點數加成"""
        c = ChisakiTuanzi()
        s = ShorekeeperTuanzi() # 守岸人點數固定 2 或 3
        
        # 模擬擲骰子結果：千咲 1 點，守岸人 3 點 (千咲是最小)
        all_rolls = {c: 1, s: 3}
        steps = c.calculate_steps(1, all_rolls)
        self.assertEqual(steps, 1 + 2) # 1 點 + 2 格加成 = 3

    def test_morning_cycle(self):
        """測試莫寧的 3-2-1 循環"""
        m = MorningTuanzi()
        self.assertEqual(m.roll_dice(), 3)
        self.assertEqual(m.roll_dice(), 2)
        self.assertEqual(m.roll_dice(), 1)
        self.assertEqual(m.roll_dice(), 3) # 回到 3

    def test_amis_teleport(self):
        """測試愛彌斯的中點瞬移技能"""
        amis = AmisTuanzi()
        other = ShorekeeperTuanzi()
        
        # 設置情境：守岸人在 25 格，愛彌斯在 15 格，且愛彌斯頭上帶個路人
        other.position = 25
        self.tiles[25] = [other]
        
        amis.position = 15
        passenger = ShorekeeperTuanzi()
        passenger.name = "路人"
        passenger.position = 15
        self.tiles[15] = [amis, passenger]
        
        # 模擬愛彌斯行動，擲 1 點，移動到 16 格觸發技能
        all_rolls = {amis: 1, other: 3, passenger: 3}
        # 覆蓋 roll_dice 確保測試穩定
        amis.roll_dice = lambda: 1
        
        amis.take_turn(self.tiles, all_rolls)
        
        # 預期結果：愛彌斯帶著路人瞬移到了 25 格，且疊在守岸人上方
        self.assertEqual(amis.position, 25)
        self.assertEqual(passenger.position, 25)
        self.assertEqual(self.tiles[25], [other, amis, passenger])
        self.assertTrue(amis.has_triggered_special)

    def test_kingbu_sweeper(self):
        """測試布大王的『掃街』鏟人邏輯"""
        kb = KingBuTuanzi() # 布大王從 32 開始往 1 走
        target = ShorekeeperTuanzi() # 目標在 30 格
        
        target.position = 30
        self.tiles[30] = [target]
        kb.position = 31
        self.tiles[31] = [kb]
        
        # 布大王往回走 2 格 (31 -> 30 -> 29)
        # 他應該在 30 格鏟起守岸人，最後兩人都到 29 格
        kb.move(-2, self.tiles)
        
        self.assertEqual(kb.position, 29)
        self.assertEqual(target.position, 29)
        # 在 29 格，布大王應該在下面 (insert_at_bottom=True)
        self.assertEqual(self.tiles[29], [kb, target])

if __name__ == "__main__":
    unittest.main()
