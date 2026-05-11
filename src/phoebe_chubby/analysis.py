import random
from typing import List, Dict
from .characters import get_all_characters, KingBuTuanzi

COURSE_LENGTH = 32
MIDPOINT = COURSE_LENGTH // 2

def run_single_race() -> str:
    """執行單場比賽並回傳贏家名字"""
    characters = get_all_characters()
    random.shuffle(characters)
    
    tiles = [[] for _ in range(COURSE_LENGTH + 1)]
    for char in characters:
        if char.insert_at_bottom:
            tiles[char.position].insert(0, char)
        else:
            tiles[char.position].append(char)
    
    TILE_EFFECTS = {
        3: "f1", 6: "rift", 10: "b1", 11: "f1",
        16: "f1", 20: "rift", 23: "f1", 28: "b1"
    }
    
    for _ in range(1, 1000): # max_rounds
        # 每一輪隨機順序
        random.shuffle(characters)
        round_rolls = {char: char.roll_dice() for char in characters}
        
        # 為了避免在循環中移除/新增角色導致問題，我們先建立當前角色的快照
        current_chars = list(characters)
        for char in current_chars:
            old_pos = char.position
            roll = round_rolls[char]
            steps = char.calculate_steps(roll, round_rolls)
            
            # 執行移動 (布大王內部會處理掃街與閃現)
            char.move(steps, tiles)
            
            # 地圖特技
            current_pos = char.position
            if current_pos != old_pos and current_pos in TILE_EFFECTS:
                effect = TILE_EFFECTS[current_pos]
                if effect == "f1":
                    char.move(1, tiles)
                elif effect == "b1":
                    char.move(-1, tiles)
                elif effect == "rift":
                    random.shuffle(tiles[current_pos])
            
            # 中點事件
            if not char.has_triggered_special and old_pos < MIDPOINT <= char.position:
                char.on_pass_midpoint(tiles)
                char.has_triggered_special = True
        
        # 檢查勝負與重置
        # 1. 布大王抵達 1 格則重生到 32
        winners_rev = [c for c in tiles[1] if c.direction == -1]
        for rev_char in winners_rev:
            tiles[1].remove(rev_char)
            rev_char.position = 32
            tiles[32].insert(0, rev_char)
            
        # 2. 正向者抵達 32 格才算贏
        winners_fwd = [c for c in tiles[COURSE_LENGTH] if c.direction == 1]
        if winners_fwd:
            return winners_fwd[-1].name
            
    return "平局"

def run_batch_simulation(num_trials=1000):
    print(f"正在模擬 {num_trials} 場比賽 (布大王模式)，請稍候...")
    win_counts = {}
    
    for i in range(num_trials):
        winner = run_single_race()
        win_counts[winner] = win_counts.get(winner, 0) + 1
        
        if (i + 1) % 100 == 0:
            print(f"已完成 {i + 1} 場...")

    print("\n🏆 === 統計結果 (布大王) ===")
    sorted_stats = sorted(win_counts.items(), key=lambda x: x[1], reverse=True)
    for name, wins in sorted_stats:
        win_rate = (wins / num_trials) * 100
        print(f"【{name}】: {wins} 勝 ({win_rate:.1f}%)")

if __name__ == "__main__":
    import sys
    trials = 1000
    if len(sys.argv) > 1:
        trials = int(sys.argv[1])
    run_batch_simulation(trials)
