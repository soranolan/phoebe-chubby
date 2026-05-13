import sys
import unittest
sys.path.insert(0, "src")

from phoebe_chubby.characters import (
    AugustaTuanzi, YunoTuanzi, PhroroTuanzi,
    ChangliTuanzi, JinhsiTuanzi, CalcharoTuanzi,
    KingBuTuanzi
)


class TestRosterV2(unittest.TestCase):
    """確認下半場所有角色都能正確初始化"""

    def test_all_characters_instantiate(self):
        """所有下半場角色都應能成功建立實例"""
        chars = [
            AugustaTuanzi(start_pos=32),
            YunoTuanzi(start_pos=32),
            PhroroTuanzi(start_pos=29),
            ChangliTuanzi(start_pos=32),
            JinhsiTuanzi(start_pos=31),
            CalcharoTuanzi(start_pos=31),
            KingBuTuanzi(start_pos=32),
        ]
        for c in chars:
            self.assertIsNotNone(c)

    def test_correct_names(self):
        """各角色的名稱應正確"""
        self.assertEqual(AugustaTuanzi().name, "奧古斯塔")
        self.assertEqual(YunoTuanzi().name, "尤諾")
        self.assertEqual(PhroroTuanzi().name, "弗洛洛")
        self.assertEqual(ChangliTuanzi().name, "長離")
        self.assertEqual(JinhsiTuanzi().name, "今汐")
        self.assertEqual(CalcharoTuanzi().name, "卡卡羅")
        self.assertEqual(KingBuTuanzi().name, "布大王")

    def test_dice_ranges(self):
        """各角色的骰子範圍應在合理範圍內"""
        chars = [
            AugustaTuanzi(), YunoTuanzi(), PhroroTuanzi(),
            ChangliTuanzi(), JinhsiTuanzi(), CalcharoTuanzi(),
        ]
        for char in chars:
            for _ in range(30):
                roll = char.roll_dice()
                self.assertGreaterEqual(roll, 1, f"{char.name} 骰出了 {roll} < 1")
                self.assertLessEqual(roll, 6, f"{char.name} 骰出了 {roll} > 6")

    def test_initial_remaining_distance(self):
        """預設初始里程應為 32"""
        for cls in [AugustaTuanzi, YunoTuanzi, PhroroTuanzi,
                    ChangliTuanzi, JinhsiTuanzi, CalcharoTuanzi]:
            char = cls()
            self.assertEqual(
                char.remaining_distance, 32,
                f"{char.name} 的初始里程應為 32，實際為 {char.remaining_distance}"
            )

    def test_kingbu_attributes(self):
        """布大王應有正確的特殊屬性"""
        kb = KingBuTuanzi()
        self.assertTrue(kb.insert_at_bottom)
        self.assertEqual(kb.direction, -1)


if __name__ == "__main__":
    unittest.main()
