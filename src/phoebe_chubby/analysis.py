import random
import sys
import time
from typing import List, Dict
from .characters import (
    AugustaTuanzi, YunoTuanzi, PhroroTuanzi,
    ChangliTuanzi, JinhsiTuanzi, CalcharoTuanzi,
    KingBuTuanzi
)
from .models import Tuanzi

COURSE_LENGTH = 32

def run_single_analysis_match(initial_states=None):
    """
    執行單場里程制比賽。
    :param initial_states: 初始狀態 Dict, 例如 {"長離": {"pos": 32, "dist": 32}, ...}
    """
    class_map = {
        "奧古斯塔": AugustaTuanzi, "尤諾": YunoTuanzi, "弗洛洛": PhroroTuanzi,
        "長離": ChangliTuanzi, "今汐": JinhsiTuanzi, "卡卡羅": CalcharoTuanzi,
        "布大王": KingBuTuanzi
    }

    if initial_states:
        characters = []
        for name, state in initial_states.items():
            char = class_map[name](start_pos=state["pos"])
            char.remaining_distance = state["dist"]
            # 如果起始位置就在中點之後，預設技能已用過
            if char.position >= 16:
                char.has_triggered_special = True
            characters.append(char)
    else:
        # 預設上半場開局 (每人剩 32 格)
        characters = [
            AugustaTuanzi(), YunoTuanzi(), PhroroTuanzi(),
            ChangliTuanzi(), JinhsiTuanzi(), CalcharoTuanzi(),
            KingBuTuanzi()
        ]
        for char in characters:
            char.remaining_distance = 32
        
    random.shuffle(characters)
    
    tiles = [[] for _ in range(COURSE_LENGTH + 1)]
    for char in characters:
        if char.insert_at_bottom:
            tiles[char.position].insert(0, char)
        else:
            tiles[char.position].append(char)

    forced_last_queue_this = []
    forced_last_queue_next = []

    for round_num in range(1, 2000):
        # 0. 準備階段
        for char in characters:
            char.prepare_round(tiles, forced_last_queue_next, verbose=False)

        # 0. 決定順序
        if round_num > 1:
            random.shuffle(characters)
            other_chars = [c for c in characters if c not in forced_last_queue_this]
            characters = other_chars + forced_last_queue_this
        
        # 所有人都擲骰，is_skipping 由 calculate_steps 動態決定
        round_rolls = {char: char.roll_dice() for char in characters}
        
        for char in list(characters):
            # 特技觸發：剩餘里程 ≤ 16 代表已跑超過一半
            if not char.has_triggered_special and char.remaining_distance <= 16:
                char.on_pass_midpoint(tiles, verbose=False)
                char.has_triggered_special = True

            roll = round_rolls[char]
            steps = char.calculate_steps(roll, round_rolls, tiles)

            # is_skipping 由 calculate_steps 動態決定 (如奧古斯塔的技能)
            if char.is_skipping:
                char.on_turn_end(tiles, forced_last_queue_next, verbose=False)
                continue

            char.move(steps, tiles)
            
            # 回合結束勾子 (例如長離的後行判定)
            char.on_turn_end(tiles, forced_last_queue_next, verbose=False)
            
        # 2. 判定勝負 (里程歸零)
        winners = [c for c in characters if not isinstance(c, KingBuTuanzi) and c.remaining_distance <= 0]
        if winners:
            # 排名邏輯：剩餘里程越小越前，里程相同看堆疊
            def rank_key(c: Tuanzi):
                try:
                    stack_idx = tiles[c.position].index(c)
                except ValueError:
                    stack_idx = 0
                return (-c.remaining_distance, stack_idx)
            
            sorted_ranks = sorted(characters, key=rank_key, reverse=True)
            return [c.name for c in sorted_ranks if not isinstance(c, KingBuTuanzi)]

        forced_last_queue_this = list(forced_last_queue_next)
        forced_last_queue_next = []
            
    return [c.name for c in characters if not isinstance(c, KingBuTuanzi)]



def run_batch_analysis(num_trials=1000, initial_states=None):
    char_names = ["奧古斯塔", "尤諾", "弗洛洛", "長離", "今汐", "卡卡羅"]
    stats = {name: {rank: 0 for rank in range(1, 7)} for name in char_names}

    mode_name = "上半場" if not initial_states else "下半場決賽"
    print(f"🚀 開始執行 {num_trials} 場 {mode_name} 數據分析...")
    
    start_time = time.time()
    for i in range(1, num_trials + 1):
        ranking = run_single_analysis_match(initial_states=initial_states)
        for rank_idx, name in enumerate(ranking):
            rank = rank_idx + 1
            if name in stats:
                stats[name][rank] += 1
        
        if i % 1000 == 0:
            print(f"⏳ 已完成 {i}/{num_trials} 場...", end='\r')
            sys.stdout.flush()

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n\n📊 === 最終平衡性分析報告 (耗時: {duration:.2f} 秒) ===")
    print(f"{'角色':<8} | {'1st':^5} | {'2nd':^5} | {'3rd':^5} | {'平均名次':^8}")
    print("-" * 50)
    
    summary = []
    for name, ranks in stats.items():
        avg = sum(r * c for r, c in ranks.items()) / num_trials
        summary.append((name, ranks, avg))
    
    summary.sort(key=lambda x: x[2])
    for name, ranks, avg in summary:
        print(f"{name:<10} | {ranks[1]:^5} | {ranks[2]:^5} | {ranks[3]:^5} | {avg:^10.2f}")

if __name__ == "__main__":
    # 設定下半場起始狀態
    second_half_states = {
        "弗洛洛": {"pos": 29, "dist": 35},
        "尤諾": {"pos": 30, "dist": 34},
        "奧古斯塔": {"pos": 30, "dist": 34},
        "卡卡羅": {"pos": 31, "dist": 33},
        "今汐": {"pos": 31, "dist": 33},
        "長離": {"pos": 32, "dist": 32},
        "布大王": {"pos": 32, "dist": 999}
    }
    
    # 預設執行 10000 場下半場統計
    trials = 10000
    if len(sys.argv) > 1:
        try:
            trials = int(sys.argv[1])
        except ValueError:
            pass
            
    run_batch_analysis(trials, initial_states=second_half_states)
