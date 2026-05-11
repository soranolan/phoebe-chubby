from .models import Tuanzi
import random
from typing import List, Dict

# --- 千咲：最小點數加成 ---
class ChisakiTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("千咲")
    
    def roll_dice(self) -> int:
        return random.randint(1, 3)
    
    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int]) -> int:
        min_roll = min(all_rolls.values())
        if roll == min_roll:
            return roll + 2
        return roll

# --- 莫寧：3/2/1 循環 ---
class MorningTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("莫寧")
        self.cycle = [3, 2, 1]
        self.cycle_index = 0

    def roll_dice(self) -> int:
        val = self.cycle[self.cycle_index]
        self.cycle_index = (self.cycle_index + 1) % len(self.cycle)
        return val

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int]) -> int:
        return roll

# --- 琳奈：60% 雙倍, 20% 停頓, 20% 正常 ---
class LinneTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("琳奈")

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int]) -> int:
        p = random.random()
        if p < 0.6:
            return roll * 2
        elif p < 0.8:
            return 0
        return roll

# --- 愛彌斯：中點瞬移 ---
class AmisTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("愛彌斯")

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def take_turn(self, tiles: List[List[Tuanzi]], all_rolls: Dict[Tuanzi, int]):
        # 1. 正常的擲骰子與位移
        roll = self.roll_dice()
        steps = self.calculate_steps(roll, all_rolls)
        self.move(steps, tiles)
        
        # 2. 位移後檢查：如果滿足條件（已達 16 格且未發動過），立刻執行瞬移
        if not self.has_triggered_special and self.position >= 16:
            # 1. 尋找所有在前面的非布大王團子，並找出最近的那一個
            all_others = [c for c in all_rolls.keys() if c != self and not isinstance(c, KingBuTuanzi)]
            others_in_front = [c for c in all_others if c.position > self.position]
            
            if others_in_front:
                # 找到最近的團子 (position 最小)
                target_char = min(others_in_front, key=lambda x: x.position)
                target_pos = target_char.position
                
                # 2. 執行瞬移：直接疊在目標格子的最頂端 (後到者居上)
                old_pos = self.position
                old_stack = tiles[old_pos]
                idx_in_old = old_stack.index(self)
                moving_group = old_stack[idx_in_old:]
                tiles[old_pos] = old_stack[:idx_in_old]
                
                # 直接 extend 到最後面 (即堆疊頂部)
                tiles[target_pos].extend(moving_group)
                
                for char in moving_group:
                    char.position = target_pos
                
                self.has_triggered_special = True
                print(f"✨ [技能瞬移] 愛彌斯感應到 {target_char.name}，帶著上方共 {len(moving_group)} 人疊到了第 {target_pos} 格的頂端！")

# --- 守岸人：穩定點數 2 或 3 ---
class ShorekeeperTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("守岸人")

    def roll_dice(self) -> int:
        return random.choice([2, 3])

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int]) -> int:
        return roll

# --- 珂萊塔：28% 機率雙倍 ---
class ColettaTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("珂萊塔")

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int]) -> int:
        if random.random() < 0.28:
            return roll * 2
        return roll

# --- 布大王：逆行者 ---
class KingBuTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("布大王")
        self.position = 32 # 從終點開始
        self.direction = -1 # 往 0 走
        self.insert_at_bottom = True # 他永遠墊底
    
    def roll_dice(self) -> int:
        return random.randint(1, 6) # 1~6 點

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int]) -> int:
        return -roll # 往起點走 (負向)

    def move(self, steps: int, tiles: List[List[Tuanzi]]):
        """布大王特有的『掃街』位移：每經過一格就鏟起該格的所有人"""
        if steps >= 0:
            super().move(steps, tiles)
            return
            
        # 往回走的邏輯 (steps 為負數)
        total_back_steps = abs(steps)
        for _ in range(total_back_steps):
            old_pos = self.position
            new_pos = max(1, old_pos - 1) # 一次只退一格
            
            if new_pos == old_pos:
                break
                
            # 找到自己在舊格子的堆疊
            stack = tiles[old_pos]
            idx = stack.index(self)
            moving_group = stack[idx:]
            tiles[old_pos] = stack[:idx]
            
            # 關鍵：先移動到新格子，並鑽到新格子堆疊的最下面，把原本在那裡的人也『鏟』到背上
            # 這樣新格子原本的人就會在 moving_group 的上方，一起被帶到下一格
            tiles[new_pos] = moving_group + tiles[new_pos]
            
            for char in moving_group:
                char.position = new_pos
            
        # 額外邏輯：『幽靈重置』
        # 如果布大王移動完後，發現自己後方（1 號位方向）已經沒人了
        # 也就是說他的 position 是全場最小的
        all_positions = [c.position for c in tiles[new_pos] if c != self] # 同格的其他人
        # 還要看其他格子的所有人
        for p, stack in enumerate(tiles):
            if p != new_pos:
                all_positions.extend([c.position for c in stack])
        
        if all_positions and self.position < min(all_positions):
            # 他是最後一名，沒人可鏟了，立刻閃現回 32
            print(f"👻 {self.name} 發現身後空無一人，閃現回 32 號位準備包抄！")
            tiles[self.position].remove(self)
            self.position = 32
            tiles[32].insert(0, self)

def get_all_characters():
    return [
        ChisakiTuanzi(),
        MorningTuanzi(),
        LinneTuanzi(),
        AmisTuanzi(),
        ShorekeeperTuanzi(),
        ColettaTuanzi(),
        KingBuTuanzi()
    ]
