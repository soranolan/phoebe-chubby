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
    def __init__(self, start_pos: int = 32):
        super().__init__("布大王", start_pos)
        self.direction = -1 # 往 0 走
        self.insert_at_bottom = True # 他永遠墊底
        self.round_count = 0
    
    def roll_dice(self) -> int:
        return random.randint(1, 6) # 1~6 點
    
    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        """布大王前兩回合固定休息"""
        self.round_count += 1
        if self.round_count <= 2:
            self.is_skipping = True
        else:
            self.is_skipping = False
        super().prepare_round(tiles, forced_last_queue, verbose)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        return -roll # 往起點走 (負向)

    def move(self, steps: int, tiles: List[List[Tuanzi]], verbose: bool = False):
        """布大王特有的『掃街』位移：每經過一格就鏟起該格的所有人"""
        if steps >= 0:
            super().move(steps, tiles)
            return
            
        # 往回走的邏輯 (steps 為負數)
        total_back_steps = abs(steps)
        for _ in range(total_back_steps):
            old_pos = self.position
            # 呼叫基類移動一格，基類會處理所有的堆疊與圈數邏輯
            super().move(-1, tiles)
            
            # 如果位置沒變（撞牆），就停止
            if self.position == old_pos:
                break
            
        # 額外邏輯：『幽靈重置』
        # 如果布大王移動完後，發現自己後方（1 號位方向）已經沒人了
        # 也就是說他的 position 是全場最小的
        all_positions = [c.position for c in tiles[self.position] if c != self] # 同格的其他人
        # 還要看其他格子的所有人
        for p, stack in enumerate(tiles):
            if p != self.position:
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
    def __init__(self, start_pos: int = 1):
        super().__init__("奧古斯塔", start_pos)
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
    def __init__(self, start_pos: int = 1):
        super().__init__("尤諾", start_pos)

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        super().prepare_round(tiles, forced_last_queue, verbose)

    def on_pass_midpoint(self, tiles: List[List[Tuanzi]], verbose: bool = True):
        """當經過中點時，發動【全地圖吸引】：將所有參賽者吸至身邊"""
        # 1. 取得全局排名 (底層 -> 頂層)
        ranking = []
        for stack in tiles:
            ranking.extend(stack)
        
        try:
            my_idx = ranking.index(self)
        except ValueError:
            return

        # 2. 分類：誰在我前面，誰在我後面 (排除自己和布大王)
        chars_behind = [c for c in ranking[:my_idx] if not isinstance(c, KingBuTuanzi)]
        chars_ahead = [c for c in ranking[my_idx+1:] if not isinstance(c, KingBuTuanzi)]

        if not chars_behind and not chars_ahead:
            return

        if verbose:
            print(f"🌌 [極大技能觸發] {self.name}發動『全地圖引力』！！所有團子都被吸向中點！")

        # 3. 從各地圖格子中移除這些人
        for c in chars_behind + chars_ahead:
            # 如果他們本來就在尤諾所在的格子，不要移除 (避免破壞 list 結構)
            if c.position != self.position:
                tiles[c.position].remove(c)
                c.position = self.position

        # 4. 重新組裝尤諾所在的格子
        # 先找到尤諾格原本的布大王 (如果有)
        bu_in_my_tile = [c for c in tiles[self.position] if isinstance(c, KingBuTuanzi)]
        
        # 新堆疊 = [原本排名在後的人] + [尤諾] + [原本排名在前的人]
        new_stack = chars_behind + [self] + chars_ahead
        
        # 重新放回格子 (布大王依然在最底層，如果有)
        tiles[self.position] = bu_in_my_tile + new_stack
        
        if verbose:
            if chars_behind:
                print(f"  - 後方 {len(chars_behind)} 名團子被吸至身下")
            if chars_ahead:
                print(f"  - 前方 {len(chars_ahead)} 名團子被吸至頭頂")

# --- 弗洛洛：底層爆發 ---
class PhroroTuanzi(Tuanzi):
    def __init__(self, start_pos: int = 1):
        super().__init__("弗洛洛", start_pos)
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
    def __init__(self, start_pos: int = 1):
        super().__init__("長離", start_pos)
        self.will_be_last_next_round = False

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        # 回合開始時，如果上一回合標記了要後行，就加入隊列
        if self.will_be_last_next_round:
            if forced_last_queue is not None:
                forced_last_queue.append(self)
                if verbose:
                    print(f"🕯️  {self.name} 展現『優雅後行』，本回合將最後行動。")
            self.will_be_last_next_round = False
        self.force_last = False

    def on_turn_end(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        """走完後判定：如果腳下有人，機率性觸發下一回合後行"""
        stack = tiles[self.position]
        try:
            my_idx = stack.index(self)
            if my_idx > 0: # 下方有其他人 (代表我疊在別人的背上)
                if random.random() < 0.65:
                    self.will_be_last_next_round = True
        except ValueError:
            pass

# --- 今汐：乘風而上 ---
class JinhsiTuanzi(Tuanzi):
    def __init__(self, start_pos: int = 1):
        super().__init__("今汐", start_pos)

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
    def __init__(self, start_pos: int = 1):
        super().__init__("卡卡羅", start_pos)

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
