from .models import Tuanzi
import random
from typing import List, Dict

# --- 千咲：最小點數加成 ---
class ChisakiTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("千咲", start_pos)
    
    def roll_dice(self) -> int:
        return random.randint(1, 3)
    
    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        """千咲目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles, forced_last_queue, verbose)
    
    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        min_roll = min(all_rolls.values())
        if roll == min_roll:
            return roll + 2
        return roll

# --- 菲比：歲主庇佑 ---
class PhoebeTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("菲比", start_pos)
        self.skill_name = "歲主庇佑"

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        """菲比目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles, forced_last_queue, verbose)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        if random.random() < 0.50:
            self.step_modifier_reason = f"觸發{self.skill_label()}"
            return roll + 1
        return roll

# --- 緋雪：引路白鳥 ---
class FeixueTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("緋雪", start_pos)
        self.skill_name = "引路白鳥"
        self.has_met_king_bu = False

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        super().prepare_round(tiles, forced_last_queue, verbose)
        self._check_king_bu_encounter(tiles, verbose)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        if tiles is not None:
            self._check_king_bu_encounter(tiles, verbose=False)
        if self.has_met_king_bu:
            return roll + 1
        return roll

    def on_turn_end(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        super().on_turn_end(tiles, forced_last_queue, verbose)
        self._check_king_bu_encounter(tiles, verbose)

    def _check_king_bu_encounter(self, tiles: List[List[Tuanzi]], verbose: bool = True):
        if self.has_met_king_bu:
            return
        if any(isinstance(c, KingBuTuanzi) for c in tiles[self.position]):
            self.has_met_king_bu = True
            if verbose:
                print(f"🕊️ {self.name} 遇見布大王，觸發{self.skill_label()}！之後每次移動額外前進 1 格。")

# --- 莫寧：3/2/1 循環 ---
class MorningTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("莫寧", start_pos)
        self.skill_name = "精密演算"
        self.cycle = [3, 2, 1]
        self.cycle_index = 0

    def roll_dice(self) -> int:
        val = self.cycle[self.cycle_index]
        self.cycle_index = (self.cycle_index + 1) % len(self.cycle)
        return val

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        """莫寧目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles, forced_last_queue, verbose)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        return roll

# --- 琳奈：炫彩時刻 ---
class LinneTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("琳奈", start_pos)
        self.skill_name = "炫彩時刻"

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        """琳奈目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles, forced_last_queue, verbose)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        p = random.random()
        if p < 0.6:
            return roll * 2
        elif p < 0.8:
            return 0
        return roll

# --- 愛彌斯：中點瞬移 ---
class AmisTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("愛彌斯", start_pos)
        self.skill_name = "電子幽靈登場"

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        """愛彌斯目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles, forced_last_queue, verbose)

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
                print(f"✨ {self.name} 觸發{self.skill_label()}，感應到 {target_char.name}，帶著上方共 {len(moving_group)} 人疊到了第 {target_pos} 格的頂端！")

# --- 守岸人：穩定點數 2 或 3 ---
class ShorekeeperTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("守岸人", start_pos)
        self.skill_name = "收束的未來"

    def roll_dice(self) -> int:
        return random.choice([2, 3])

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        """守岸人目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles, forced_last_queue, verbose)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        return roll

# --- 珂萊塔：28% 機率雙倍 ---
class ColettaTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("珂萊塔", start_pos)

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        """珂萊塔目前沒有每回合開始前的特殊邏輯"""
        super().prepare_round(tiles, forced_last_queue, verbose)

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
        # 回合開始只重置狀態
        self.force_last = False
        self.is_skipping = False

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        if tiles is None:
            return roll
            
        stack = tiles[self.position]
        if len(stack) > 1 and stack[-1] == self:
            # 觸發休息
            self.is_skipping = True
            # 我們在下一步的 move 裡處理日誌，或者在這裡標記
            return 0
        
        return roll

    def on_turn_end(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        # 如果是因為技能而休息，則下一回合墊後
        if self.is_skipping:
            if forced_last_queue is not None:
                forced_last_queue.append(self)
            if verbose:
                print(f"🛌 {self.name} 觸發{self.skill_label()}，決定原地休息，下一回合將最後行動。")

# --- 尤諾：錨定命途 ---
class YunoTuanzi(Tuanzi):
    def __init__(self, start_pos: int = 1):
        super().__init__("尤諾", start_pos)
        self.skill_name = "錨定命途"

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
            print(f"🌌 {self.name} 觸發{self.skill_label()}！所有團子都被吸向中點！")

        # 3. 從各地圖格子中移除這些人，並同步里程
        for c in chars_behind + chars_ahead:
            if c.position != self.position:
                # 計算位移差：(目標位置 - 原始位置)
                diff = self.position - c.position
                # 考慮 32 格循環位移修正 (取最短路徑吸過來)
                if diff > 16: diff -= 32
                if diff < -16: diff += 32
                
                # 同步里程：被吸往前里程減少，被吸往後里程增加
                c.remaining_distance -= diff
                
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

# --- 弗洛洛：優雅陰謀 ---
class PhroroTuanzi(Tuanzi):
    def __init__(self, start_pos: int = 1):
        super().__init__("弗洛洛", start_pos)
        self.skill_name = "優雅陰謀"
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
                    print(f"🕯️  {self.name} 觸發{self.skill_label()}，本回合將最後行動。")
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
        self.skill_name = "令尹之名"

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def prepare_round(self, tiles: List[List[Tuanzi]], forced_last_queue: List[Tuanzi] = None, verbose: bool = True):
        pass

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        if tiles is None or self.position <= 1:
            return roll

        stack = tiles[self.position]
        try:
            my_idx = stack.index(self)
            if my_idx < len(stack) - 1: # 頭頂有人
                target_above = stack[my_idx + 1]
                # 頭頂的人正在休息時，機率提升
                trigger_chance = 0.80 if target_above.is_skipping else 0.40
                if random.random() < trigger_chance:
                    stack.remove(self)
                    stack.append(self) # 躍升至頂端
                    # 透過旗標讓 move() 能夠打印日誌
                    self._dragon_jumped_over = target_above.name if target_above.is_skipping else None
                    self._did_dragon_jump = True
        except ValueError:
            pass

        return roll

    def move(self, steps: int, tiles: List[List[Tuanzi]], verbose: bool = False):
        if getattr(self, '_did_dragon_jump', False) and verbose:
            msg = f"🐉 {self.name} 觸發{self.skill_label()}"
            if getattr(self, '_dragon_jumped_over', None):
                msg += f"（趁著 {self._dragon_jumped_over} 休息超車）"
            print(f"{msg}，躍升至堆疊頂端！")
            self._did_dragon_jump = False
            self._dragon_jumped_over = None
        super().move(steps, tiles, verbose)

# --- 卡卡羅：如影隨形 ---
class CalcharoTuanzi(Tuanzi):
    def __init__(self, start_pos: int = 1):
        super().__init__("卡卡羅", start_pos)
        self.skill_name = "如影隨形"

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
                self.step_modifier_reason = f"觸發{self.skill_label()}"
                return roll + 3
        return roll

class LucaixTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("陸赫斯", start_pos)

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def tile_effect_bonus(self, effect: str) -> int:
        if effect == 'f1':
            return 3
        elif effect == 'b1':
            return -1
        return 0

class DaniaTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("達妮婭", start_pos)
        self.last_roll = None

    def roll_dice(self) -> int:
        return random.randint(1, 3)
        
    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        steps = roll
        if self.last_roll is not None and roll == self.last_roll:
            steps += 2
        self.last_roll = roll
        return steps

class SigelicaTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("西格莉卡", start_pos)

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def after_rolls(self, round_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]], verbose: bool = False):
        # Determine ranking based on remaining_distance and stack_idx
        # First, filter out KingBu which is always last anyway, and get active characters
        active_chars = [c for c in round_rolls.keys() if c.name != "布大王"]
        
        def rank_key(c: Tuanzi):
            try:
                stack_idx = tiles[c.position].index(c)
            except ValueError:
                stack_idx = 0
            return (-c.remaining_distance, stack_idx)
            
        sorted_chars = sorted(active_chars, key=rank_key, reverse=True)
        
        try:
            my_idx = sorted_chars.index(self)
        except ValueError:
            return
            
        # Target up to 2 characters ahead of me (lower index in sorted_chars)
        targets = []
        if my_idx > 0:
            targets.append(sorted_chars[my_idx - 1])
        if my_idx > 1:
            targets.append(sorted_chars[my_idx - 2])
            
        for t in targets:
            t.step_debuff += 1
            if verbose:
                print(f"🎯 {self.name} 標記了 {t.name}，本回合移動減免 1 格！")

class KatishiaTuanzi(Tuanzi):
    def __init__(self, start_pos=1):
        super().__init__("卡提希婭", start_pos)
        self.skill_name = "翻盤橋段"
        self.buff_active = False

    def roll_dice(self) -> int:
        return random.randint(1, 3)

    def calculate_steps(self, roll: int, all_rolls: Dict[Tuanzi, int], tiles: List[List[Tuanzi]] = None) -> int:
        steps = roll
        if self.buff_active:
            if random.random() < 0.60:
                self.step_modifier_reason = f"觸發{self.skill_label()}"
                steps += 2
        return steps

    def on_turn_end(self, tiles: List[List['Tuanzi']], forced_last_queue: List['Tuanzi'] = None, verbose: bool = True):
        super().on_turn_end(tiles, forced_last_queue, verbose)
        if not self.buff_active:
            all_chars = []
            for stack in tiles:
                for c in stack:
                    all_chars.append(c)
            
            active_chars = [c for c in all_chars if c.name != "布大王"]
            if not active_chars:
                return

            def rank_key(c: Tuanzi):
                try:
                    stack_idx = tiles[c.position].index(c)
                except ValueError:
                    stack_idx = 0
                return (-c.remaining_distance, stack_idx)
            
            sorted_chars = sorted(active_chars, key=rank_key, reverse=True)
            if sorted_chars and sorted_chars[-1] == self:
                self.buff_active = True
                if verbose:
                    print(f"🔥 {self.name} 處於最後一名，觸發{self.skill_label()}！後續回合 60% 機率額外前進 2 格。")

def get_all_characters():
    return [
        ChisakiTuanzi(),
        PhoebeTuanzi(),
        FeixueTuanzi(),
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
        CalcharoTuanzi(),
        LucaixTuanzi(),
        DaniaTuanzi(),
        SigelicaTuanzi(),
        KatishiaTuanzi()
    ]
