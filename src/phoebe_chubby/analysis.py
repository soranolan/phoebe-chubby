import random
import sys
from typing import List, Dict
from .characters import (
    AugustaTuanzi, YunoTuanzi, PhroroTuanzi,
    ChangliTuanzi, JinhsiTuanzi, CalcharoTuanzi,
    KingBuTuanzi
)
from .models import Tuanzi

COURSE_LENGTH = 32

def run_single_analysis_match():
    """執行單場比賽並回傳所有參賽者的名次排序 (排除布大王)"""
    characters = [
        AugustaTuanzi(), YunoTuanzi(), PhroroTuanzi(),
        ChangliTuanzi(), JinhsiTuanzi(), CalcharoTuanzi(),
        KingBuTuanzi()
    ]
    random.shuffle(characters)
    
    tiles = [[] for _ in range(COURSE_LENGTH + 1)]
    for char in characters:
        if char.insert_at_bottom:
            tiles[char.position].insert(0, char)
        else:
            tiles[char.position].append(char)

    forced_last_queue_this = []
    forced_last_queue_next = []

    for round_num in range(1, 1000):
        # 0. 準備階段 (靜默模式)
        for char in characters:
            char.prepare_round(tiles, forced_last_queue_next, verbose=False)

        # 0. 決定順序
        if round_num > 1:
            random.shuffle(characters)
            other_chars = [c for c in characters if c not in forced_last_queue_this]
            characters = other_chars + forced_last_queue_this
        
        # 1. 擲骰與移動
        for char in characters:
            if isinstance(char, KingBuTuanzi) and round_num < 3:
                char.is_skipping = True
            elif isinstance(char, KingBuTuanzi):
                char.is_skipping = False
        
        round_rolls = {char: (char.roll_dice() if not char.is_skipping else 0) for char in characters}
        
        for char in list(characters):
            if char.is_skipping: continue
            
            # 觸發中點特技 (靜默模式)
            if not char.has_triggered_special and char.position >= 16:
                char.on_pass_midpoint(tiles, verbose=False)
                char.has_triggered_special = True

            roll = round_rolls[char]
            steps = char.calculate_steps(roll, round_rolls, tiles)
            
            # 執行移動 (靜默模式)
            if isinstance(char, KingBuTuanzi):
                char.move(steps, tiles, verbose=False)
            else:
                char.move(steps, tiles)
            
        # 2. 判定勝負
        winners = [c for c in tiles[COURSE_LENGTH] if c.direction == 1]
        if winners:
            # 根據 (位置, 堆疊索引) 對所有人進行最終排名
            def rank_key(c: Tuanzi):
                try:
                    stack_idx = tiles[c.position].index(c)
                except ValueError:
                    stack_idx = 0
                return (c.position, stack_idx)
            
            sorted_ranks = sorted(characters, key=rank_key, reverse=True)
            # 剔除布大王，只回傳參賽者名次
            return [c.name for c in sorted_ranks if not isinstance(c, KingBuTuanzi)]

        # 轉移隊列
        forced_last_queue_this = list(forced_last_queue_next)
        forced_last_queue_next = []
            
    return [c.name for c in characters if not isinstance(c, KingBuTuanzi)] # 平局

def run_batch_analysis(num_trials=1000):
    # 結構: { 角色名: { 名次(1-6): 次數 } }
    char_names = ["奧古斯塔", "尤諾", "弗洛洛", "長離", "今汐", "卡卡羅"]
    stats = {name: {rank: 0 for rank in range(1, 7)} for name in char_names}

    print(f"🚀 開始執行 {num_trials} 場純數據分析 (排除布大王)...")
    
    for i in range(1, num_trials + 1):
        ranking = run_single_analysis_match()
        for rank_idx, name in enumerate(ranking):
            rank = rank_idx + 1
            if name in stats:
                stats[name][rank] = stats[name].get(rank, 0) + 1
        
        if i % 1000 == 0:
            print(f"⏳ 已完成 {i}/{num_trials} 場...", end='\r')
            sys.stdout.flush()

    print("\n\n📊 === 最終平衡性分析報告 (排除布大王) ===")
    print(f"{'角色':<8} | {'1st':^5} | {'2nd':^5} | {'3rd':^5} | {'平均名次':^8}")
    print("-" * 50)
    
    sorted_summary = []
    for name, ranks in stats.items():
        total_rank_sum = sum(rank * count for rank, count in ranks.items())
        avg_rank = total_rank_sum / num_trials
        sorted_summary.append((name, ranks, avg_rank))
    
    # 根據平均名次排序 (越小越強)
    sorted_summary.sort(key=lambda x: x[2])
    
    for name, ranks, avg in sorted_summary:
        win_rate = (ranks[1] / num_trials) * 100
        print(f"{name:<10} | {ranks[1]:^5} | {ranks[2]:^5} | {ranks[3]:^5} | {avg:^10.2f}")

    print("\n* 統計已排除布大王，僅針對 6 位參賽團子進行名次排定。")

if __name__ == "__main__":
    trials = 10000
    if len(sys.argv) > 1:
        trials = int(sys.argv[1])
    run_batch_analysis(trials)
