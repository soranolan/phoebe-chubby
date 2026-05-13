import sys
import unittest
sys.path.insert(0, "src")

from phoebe_chubby.characters import (
    AugustaTuanzi, YunoTuanzi, PhroroTuanzi,
    ChangliTuanzi, JinhsiTuanzi, CalcharoTuanzi,
    KingBuTuanzi
)
from phoebe_chubby.models import Tuanzi


def make_tiles(size=33):
    return [[] for _ in range(size)]


class TestAugusta(unittest.TestCase):

    def test_skips_when_on_top_of_stack(self):
        """奧古斯塔在堆疊頂端時應觸發休息（步數 = 0）"""
        tiles = make_tiles()
        other = CalcharoTuanzi(start_pos=5)
        augusta = AugustaTuanzi(start_pos=5)
        tiles[5] = [other, augusta]  # 奧古斯塔在頂端

        augusta.prepare_round(tiles, [], verbose=False)
        steps = augusta.calculate_steps(3, {}, tiles)
        self.assertEqual(steps, 0)
        self.assertTrue(augusta.is_skipping)

    def test_moves_normally_when_alone(self):
        """奧古斯塔獨自在格子時應正常行動"""
        tiles = make_tiles()
        augusta = AugustaTuanzi(start_pos=5)
        tiles[5] = [augusta]

        augusta.prepare_round(tiles, [], verbose=False)
        steps = augusta.calculate_steps(2, {}, tiles)
        self.assertEqual(steps, 2)
        self.assertFalse(augusta.is_skipping)

    def test_moves_normally_when_at_bottom(self):
        """奧古斯塔在堆疊底層時應正常行動"""
        tiles = make_tiles()
        augusta = AugustaTuanzi(start_pos=5)
        other = CalcharoTuanzi(start_pos=5)
        tiles[5] = [augusta, other]  # 奧古斯塔在底層

        augusta.prepare_round(tiles, [], verbose=False)
        steps = augusta.calculate_steps(3, {}, tiles)
        self.assertEqual(steps, 3)
        self.assertFalse(augusta.is_skipping)


class TestJinhsi(unittest.TestCase):

    def test_jumps_to_top_when_someone_above(self):
        """今汐在有人壓頭時，應有機率躍升至頂端"""
        # 跑 50 次，至少應有一次成功
        jumped = False
        tiles = make_tiles()
        for _ in range(50):
            tiles = make_tiles()
            other = CalcharoTuanzi(start_pos=10)
            jinhsi = JinhsiTuanzi(start_pos=10)
            jinhsi.remaining_distance = 20
            tiles[10] = [jinhsi, other]  # 今汐在底，other 在頂
            jinhsi.calculate_steps(2, {}, tiles)
            if tiles[10][-1] == jinhsi:
                jumped = True
                break
        self.assertTrue(jumped, "今汐應至少有一次成功躍升至頂端")

    def test_does_not_jump_when_alone(self):
        """今汐獨自在格子時不應觸發騰龍"""
        tiles = make_tiles()
        jinhsi = JinhsiTuanzi(start_pos=10)
        jinhsi.remaining_distance = 20
        tiles[10] = [jinhsi]
        jinhsi.calculate_steps(2, {}, tiles)
        self.assertEqual(tiles[10], [jinhsi])

    def test_higher_chance_when_above_is_skipping(self):
        """頭頂的人休息時，今汐的騰龍機率應較高"""
        tiles = make_tiles()
        other = AugustaTuanzi(start_pos=10)
        other.is_skipping = True  # 模擬奧古斯塔休息中
        jinhsi = JinhsiTuanzi(start_pos=10)
        jinhsi.remaining_distance = 20
        tiles[10] = [jinhsi, other]

        jumps = sum(
            1 for _ in range(200)
            if (tiles.__setitem__(10, [jinhsi, other]) or True)
            and jinhsi.calculate_steps(2, {}, tiles) is not None
            and tiles[10][-1] == jinhsi
        )
        # 機率應 > 50%（80% 觸發），200 次裡至少 80 次
        self.assertGreater(jumps, 80, "奧古斯塔休息時，今汐騰龍次數應超過 80/200")


class TestChangli(unittest.TestCase):

    def test_marks_next_round_flag_when_stacked(self):
        """長離移動後疊在別人背上時，應設定下一回合後行旗標"""
        marked = False
        for _ in range(30):
            tiles = make_tiles()
            other = CalcharoTuanzi(start_pos=5)
            changli = ChangliTuanzi(start_pos=5)
            changli.remaining_distance = 20
            tiles[5] = [other, changli]  # 長離在頂端（疊在別人背上）
            changli.on_turn_end(tiles, [], verbose=False)
            if changli.will_be_last_next_round:
                marked = True
                break
        self.assertTrue(marked, "長離在別人背上時應觸發後行旗標")

    def test_no_flag_when_alone(self):
        """長離獨自在格子時不應設定後行旗標"""
        tiles = make_tiles()
        changli = ChangliTuanzi(start_pos=5)
        changli.remaining_distance = 20
        tiles[5] = [changli]
        changli.on_turn_end(tiles, [], verbose=False)
        self.assertFalse(changli.will_be_last_next_round)


class TestPhroro(unittest.TestCase):

    def test_bonus_steps_when_at_bottom(self):
        """弗洛洛在堆疊底層時，應獲得 +3 步的加成"""
        tiles = make_tiles()
        phroro = PhroroTuanzi(start_pos=5)
        other = CalcharoTuanzi(start_pos=5)
        tiles[5] = [phroro, other]  # 弗洛洛在底層
        phroro.prepare_round(tiles, [], verbose=False)
        steps = phroro.calculate_steps(2, {}, tiles)
        self.assertEqual(steps, 5)  # 2 + 3

    def test_no_bonus_when_alone(self):
        """弗洛洛獨自在格子時不應獲得加成"""
        tiles = make_tiles()
        phroro = PhroroTuanzi(start_pos=5)
        tiles[5] = [phroro]
        phroro.prepare_round(tiles, [], verbose=False)
        steps = phroro.calculate_steps(2, {}, tiles)
        self.assertEqual(steps, 2)


class TestKingBu(unittest.TestCase):

    def test_insert_at_bottom_flag(self):
        """布大王應設定 insert_at_bottom = True"""
        kingbu = KingBuTuanzi(start_pos=1)
        self.assertTrue(kingbu.insert_at_bottom)


if __name__ == "__main__":
    unittest.main()
