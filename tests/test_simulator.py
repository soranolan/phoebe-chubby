import sys
import unittest
sys.path.insert(0, "src")

from phoebe_chubby.models import Tuanzi
from phoebe_chubby.characters import CalcharoTuanzi, KingBuTuanzi, AugustaTuanzi


def make_tiles(size=33):
    return [[] for _ in range(size)]


class TestTuanziMove(unittest.TestCase):

    def test_move_decrements_remaining_distance(self):
        """移動後剩餘里程應正確扣除"""
        tiles = make_tiles()
        char = CalcharoTuanzi(start_pos=5)
        char.remaining_distance = 20
        tiles[5] = [char]
        char.move(3, tiles)
        self.assertEqual(char.remaining_distance, 17)
        self.assertEqual(char.position, 8)

    def test_move_wraps_around_board(self):
        """超過 32 格應循環回到 1 號位"""
        tiles = make_tiles()
        char = CalcharoTuanzi(start_pos=31)
        char.remaining_distance = 10
        tiles[31] = [char]
        char.move(3, tiles)
        self.assertEqual(char.position, 2)
        self.assertEqual(char.remaining_distance, 7)

    def test_move_carries_stack(self):
        """移動時應帶著上方的團子一起移動"""
        tiles = make_tiles()
        bottom = CalcharoTuanzi(start_pos=5)
        bottom.remaining_distance = 20
        top = AugustaTuanzi(start_pos=5)
        top.remaining_distance = 20
        tiles[5] = [bottom, top]

        bottom.move(3, tiles)

        self.assertEqual(bottom.position, 8)
        self.assertEqual(top.position, 8)
        self.assertIn(bottom, tiles[8])
        self.assertIn(top, tiles[8])

    def test_skill_resets_on_milestone(self):
        """剩餘里程跨過 32 的倍數時，技能旗標應重置"""
        tiles = make_tiles()
        char = CalcharoTuanzi(start_pos=5)
        char.remaining_distance = 2
        char.has_triggered_special = True
        tiles[5] = [char]
        char.move(3, tiles)  # 剩餘從 2 → -1，跨過 0（32 的倍數邊界）
        self.assertFalse(char.has_triggered_special)

    def test_move_zero_steps_does_nothing(self):
        """移動 0 步不應改變任何狀態"""
        tiles = make_tiles()
        char = CalcharoTuanzi(start_pos=5)
        char.remaining_distance = 20
        tiles[5] = [char]
        char.move(0, tiles)
        self.assertEqual(char.position, 5)
        self.assertEqual(char.remaining_distance, 20)


class TestKingBuMove(unittest.TestCase):

    def test_kingbu_inserts_at_bottom(self):
        """布大王移動後應插入新格子的最底層"""
        tiles = make_tiles()
        kingbu = KingBuTuanzi(start_pos=5)
        kingbu.remaining_distance = 1010
        tiles[5] = [kingbu]

        # 布大王往後退 3 步：5 → 2
        kingbu.move(-3, tiles)

        # 確認移動到正確位置
        self.assertEqual(kingbu.position, 2)
        # 確認在格子中
        self.assertIn(kingbu, tiles[2])
        # 確認在格子最底層 (index 0)
        self.assertEqual(tiles[2][0], kingbu)


if __name__ == "__main__":
    unittest.main()
