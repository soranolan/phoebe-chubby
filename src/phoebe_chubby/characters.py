from .models import Tuanzi
import random
from typing import List, Dict

# --- 千咲：最小點數加成 ---
class ChisakiTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("千咲")
    
    def roll_dice(self) -> int:
        return random.randint(1, 3)
    
    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None):
        """千咲目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles)
    
    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
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

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None):
        """莫寧目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        return roll

# --- 琳奈：60% 雙倍, 20% 停頓, 20% 正常 ---
class LinneTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("琳奈")

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None):
        """琳奈目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
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

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None):
        """愛彌斯目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles)

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

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None):
        """守岸人目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        return roll

# --- 珂萊塔：28% 機率雙倍 ---
class ColettaTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("珂萊塔")

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None):
        """珂萊塔目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
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
    
    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        """布大王目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles, forced_last_queue, verbose)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        return -roll # 往起點走 (負向)

    def move(self, steps: int, tiles: List[List[Tuanzi]], verbose: bool = True):
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
            if verbose:
                print(f"👻 {self.name} 發現身後空無一人，閃現回 32 號位準備包抄！")
            tiles[self.position].remove(self)
            self.position = 32
            tiles[32].insert(0, self)
            
# --- 奧古斯塔：堆疊頂端停頓 ---
class AugustaTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("奧古斯塔")
        self.force_last_next = False

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        # 奧古斯塔的 force_last 現在由引擎透過 queue 管理，這裡重置狀態
        self.force_last = False 
        
        # 檢查本回合是否在【真正的堆疊】頂端 (人數必須 > 1)
        stack = tiles[self.position]
        if len(stack) > 1 and stack[-1] == self:
            self.is_skipping = True
            if forced_last_queue is not None:
                forced_last_queue.append(self)
        else:
            self.is_skipping = False

# --- 尤諾：空間引力 ---
class YunoTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("尤諾")

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        super().prepare_round(tiles, forced_last_queue, verbose)

    def on_pass_midpoint(self, tiles: List[List[Tuanzi]], verbose: bool = True):
        """當經過中點時，拉近排名前後的整個堆疊"""
        # 1. 取得全局排名
        ranking = []
        for stack in tiles:
            ranking.extend(stack)
        
        try:
            my_idx = ranking.index(self)
        except ValueError:
            return

        char_behind = ranking[my_idx - 1] if my_idx > 0 else None
        char_ahead = ranking[my_idx + 1] if my_idx < len(ranking) - 1 else None

        # 排除布大王
        if isinstance(char_behind, KingBuTuanzi): char_behind = None
        if isinstance(char_ahead, KingBuTuanzi): char_ahead = None

        if not char_behind and not char_ahead:
            return

        if verbose:
            print(f"🌌 [技能觸發] 尤諾發動『空間引力』，開始搬運鄰近堆疊！")

        # 2. 處理後方堆疊 (排名落後者)
        if char_behind and char_behind.position != self.position:
            old_pos = char_behind.position
            stack_b = tiles[old_pos]
            idx_b = stack_b.index(char_behind)
            group_b = stack_b[idx_b:] # 抓走他及其上方所有人
            tiles[old_pos] = stack_b[:idx_b]
            
            # 插入到尤諾下方
            stack_y = tiles[self.position]
            idx_y = stack_y.index(self)
            tiles[self.position] = stack_y[:idx_y] + group_b + stack_y[idx_y:]
            
            for c in group_b: c.position = self.position
            if verbose:
                print(f"  - 將後方 {char_behind.name} 的堆疊 (共 {len(group_b)} 人) 從第 {old_pos} 格吸至身下")

        # 3. 處理前方堆疊 (排名領先者)
        if char_ahead and char_ahead.position != self.position:
            # 注意：如果剛才搬運後方堆疊時尤諾的格子發生了變化，這裡需要重新定位尤諾 (雖然 position 沒變但 stack 變了)
            old_pos = char_ahead.position
            stack_a = tiles[old_pos]
            idx_a = stack_a.index(char_ahead)
            group_a = stack_a[idx_a:] # 抓走他及其上方所有人
            tiles[old_pos] = stack_a[:idx_a]
            
            # 插入到尤諾格子的最上方 (維持領先排名)
            tiles[self.position].extend(group_a)
            
            for c in group_a: c.position = self.position
            if verbose:
                print(f"  - 將前方 {char_ahead.name} 的堆疊 (共 {len(group_a)} 人) 從第 {old_pos} 格吸至頭頂")

# --- 弗洛洛：底層爆發 ---
class PhroroTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("弗洛洛")
        self.extra_steps = 0

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        # 檢查是否在【真正的堆疊】最底層 (人數必須 > 1，且在 index 0)
        stack = tiles[self.position]
        if len(stack) > 1 and stack[0] == self:
            self.extra_steps = 3
        else:
            self.extra_steps = 0

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        if self.extra_steps > 0:
            # print(f"🚀 {self.name} 從底層發力，額外前進 {self.extra_steps} 格！")
            return roll + self.extra_steps
        return roll

# --- 長離：優雅後行 ---
class ChangliTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("長離")
        self.force_last_next = False

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        # 長離的 force_last 現在由引擎透過 queue 管理
        self.force_last = False
        
        # 檢查本回合是否有人在自己下方
        stack = tiles[self.position]
        try:
            my_idx = stack.index(self)
            if my_idx > 0: # 下方有其他人
                if random.random() < 0.65:
                    if forced_last_queue is not None:
                        forced_last_queue.append(self)
        except ValueError:
            pass

# --- 今汐：乘風而上 ---
class JinhsiTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("今汐")

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        # 檢查頭頂是否有人，且必須離開起跑點
        if self.position <= 1:
            return
            
        stack = tiles[self.position]
        try:
            my_idx = stack.index(self)
            if my_idx < len(stack) - 1: # 頭頂有人
                if random.random() < 0.40:
                    if verbose:
                        print(f"🐉 {self.name} 發動『騰龍』，躍升至第 {self.position} 格的堆疊頂端！")
                    stack.remove(self)
                    stack.append(self)
        except ValueError:
            pass

# --- 卡卡羅：絕地追擊 ---
class CalcharoTuanzi(Tuanzi):
    def __init__(self):
        super().__init__("卡卡羅")

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        super().prepare_round(tiles, forced_last_queue, verbose)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        if tiles is None:
            return roll
            
        # 判定是否為「最後一名」：
        # 1. 位置是最低的
        min_pos = min(c.position for c in all_rolls.keys())
        if self.position == min_pos:
            # 2. 在該格子的堆疊中最底層 (index == 0)
            stack = tiles[self.position]
            if stack and stack[0] == self:
                # print(f"⚔️ {self.name} 處於絕地 (最後一名)，爆發前進！")
                return roll + 3
        return roll

def get_all_characters():
    return [
        ChisakiTuanzi(),
        MorningTuanzi(),
        LinneTuanzi(),
        AmisTuanzi(),
        ShorekeeperTuanzi(),
        ColettaTuanzi(),
        KingBuTuanzi(),
        AugustaTuanzi(),
        YunoTuanzi(),
        PhroroTuanzi(),
        ChangliTuanzi(),
        JinhsiTuanzi(),
        CalcharoTuanzi()
    ]
