from dataclasses import dataclass, field
from typing import List, Dict

@dataclass(eq=False)
class Tuanzi:
    name: str
    position: int = 1
    direction: int = 1 # 1 代表往 32 走，-1 代表往 1 走
    has_triggered_special: bool = False

    def roll_dice(self) -> int:
        return 0 # 子類別實作

    def calculate_steps(self, roll: int, all_rolls: Dict['Tuanzi', int], tiles: List[List['Tuanzi']] = None) -> int:
        return roll

    insert_at_bottom: bool = False # 是否強制鑽到堆疊最下面
    is_skipping: bool = False      # 本回合是否跳過行動
    force_last: bool = False       # 本回合是否強制最後一個行動

    def prepare_round(self, tiles: List[List['Tuanzi']], forced_last_queue: List['Tuanzi'] = None, verbose: bool = True):
        """每回合開始前的準備動作"""
        pass

    def move(self, steps: int, tiles: List[List['Tuanzi']]):
        """執行物理位移，並帶動上方所有團子移動"""
        if steps == 0:
            return
        
        old_pos = self.position
        new_pos = max(1, min(old_pos + steps, 32)) 
        
        if new_pos != old_pos:
            stack = tiles[old_pos]
            try:
                idx = stack.index(self)
            except ValueError:
                return 
            
            # 邏輯修正：如果在起點 (1 號位)，大家是平齊的，不帶動別人
            if old_pos == 1:
                moving_group = [self]
                stack.remove(self)
            else:
                moving_group = stack[idx:]
                tiles[old_pos] = stack[:idx]
            
            # 根據屬性決定是疊在上面，還是鑽到下面
            if self.insert_at_bottom:
                tiles[new_pos] = moving_group + tiles[new_pos]
            else:
                tiles[new_pos].extend(moving_group)
            
            for char in moving_group:
                char.position = new_pos

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
