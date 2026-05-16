from dataclasses import dataclass, field
from typing import List, Dict

@dataclass(eq=False)
class Tuanzi:
    name: str
    position: int = 1
    remaining_distance: int = 32 # 剩餘里程數
    direction: int = 1           # 1 代表往 32 走，-1 代表往 1 走
    has_triggered_special: bool = False

    def roll_dice(self) -> int:
        return 0 # 子類別實作

    def calculate_steps(self, roll: int, all_rolls: Dict['Tuanzi', int], tiles: List[List['Tuanzi']] = None) -> int:
        return roll

    insert_at_bottom: bool = False # 是否強制鑽到堆疊最下面
    is_skipping: bool = False      # 本回合是否跳過行動
    force_last: bool = False       # 本回合是否強制最後一個行動
    step_debuff: int = 0           # 本回合受到的步數減免

    def prepare_round(self, tiles: List[List['Tuanzi']], forced_last_queue: List['Tuanzi'] = None, verbose: bool = True):
        """每回合開始前的準備動作"""
        self.step_debuff = 0
        pass

    def after_rolls(self, round_rolls: Dict['Tuanzi', int], tiles: List[List['Tuanzi']], verbose: bool = False):
        """每回合擲骰子後，開始移動前的勾子"""
        pass

    def on_turn_end(self, tiles: List[List['Tuanzi']], forced_last_queue: List['Tuanzi'] = None, verbose: bool = True):
        """回合結束後的特殊判定勾子"""
        pass

    def tile_effect_bonus(self, effect: str) -> int:
        """地圖特效觸發時的額外步數加成（預設 0）"""
        return 0

    def move(self, steps: int, tiles: List[List['Tuanzi']], verbose: bool = False):
        """執行物理位移，扣除剩餘里程"""
        if steps == 0:
            return
        
        old_pos = self.position
        # 物理位置在 1-32 之間循環
        # 計算方式：(當前位置 + 步數 - 1) % 32 + 1
        new_pos = (old_pos + steps - 1) % 32 + 1
        
        if new_pos != old_pos:
            stack = tiles[old_pos]
            try:
                idx = stack.index(self)
                
                # 1. 決定移動群組：僅在起點 (1 號位) 且剩餘距離是 32 倍數時不帶動他人
                if old_pos == 1 and self.remaining_distance % 32 == 0:
                    moving_group = [self]
                    stack.remove(self)
                else:
                    moving_group = stack[idx:]
                    tiles[old_pos] = stack[:idx]
                
                # 2. 決定放置方式
                if self.insert_at_bottom:
                    tiles[new_pos] = moving_group + tiles[new_pos]
                else:
                    tiles[new_pos].extend(moving_group)
                
                # 3. 更新群組中所有成員的狀態
                for char in moving_group:
                    # 檢查是否越過了 32 格（里程碑），如果是，重置技能
                    # 比如從 剩餘 1 變成 剩餘 -1，代表跨過了終點/起點線
                    old_milestone = (char.remaining_distance - 1) // 32
                    char.remaining_distance -= steps
                    new_milestone = (char.remaining_distance - 1) // 32
                    
                    if new_milestone < old_milestone:
                        char.has_triggered_special = False
                    
                    char.position = (char.position + steps - 1) % 32 + 1
            except ValueError:
                pass

    def take_turn(self, tiles: List[List['Tuanzi']], all_rolls: Dict['Tuanzi', int]):
        """
        每回合輪到該團子時的動作。
        預設：擲骰子 -> 計算步數 -> 移動
        """
        roll = self.roll_dice()
        steps = self.calculate_steps(roll, all_rolls)
        self.move(steps, tiles)

    def on_pass_midpoint(self, tiles: List[List['Tuanzi']], verbose: bool = True):
        """中點觸發勾子"""
        pass

    def __repr__(self):
        return f"{self.name}(pos={self.position})"
