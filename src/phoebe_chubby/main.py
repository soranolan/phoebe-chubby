import random
from .characters import get_all_characters

COURSE_LENGTH = 32
MIDPOINT = COURSE_LENGTH // 2

def run_simulation(max_rounds=999):
    characters = get_all_characters()
    random.shuffle(characters)
    
    tiles = [[] for _ in range(COURSE_LENGTH + 1)]
    for char in characters:
        if char.insert_at_bottom:
            tiles[char.position].insert(0, char)
        else:
            tiles[char.position].append(char)

    print("=== 鳴潮小團快跑 模擬開始 (地圖特技模式) ===")
    
    # 定義賽道特技
    # "f1": 前進 1 格, "b1": 倒退 1 格, "rift": 空間裂隙 (隨機堆疊)
    TILE_EFFECTS = {
        3: "f1", 6: "rift", 10: "b1", 11: "f1",
        16: "f1", 20: "rift", 23: "f1", 28: "b1"
    }
    
    for round_num in range(1, max_rounds + 1):
        # 0. 每一輪開始前，隨機決定行動順序
        random.shuffle(characters)
        print(f"\n--- 第 {round_num} 回合 行動順序: {[c.name for c in characters]} ---")
        
        # 1. 所有人預定點數
        round_rolls = {char: char.roll_dice() for char in characters}
        
        for char in list(characters):
            old_pos = char.position
            roll = round_rolls[char]
            steps = char.calculate_steps(roll, round_rolls)
            
            # 1. 執行基礎移動
            char.move(steps, tiles)
            
            # 2. 檢查落點是否有賽道特技 (如果移動後位置變了)
            current_pos = char.position
            if current_pos != old_pos and current_pos in TILE_EFFECTS:
                effect = TILE_EFFECTS[current_pos]
                
                if effect == "f1":
                    print(f"🚀 {char.name} 踩到前進裝置，額外向 32 方向移動 1 格！")
                    char.move(1, tiles)
                elif effect == "b1":
                    print(f"⚠️ {char.name} 踩到倒退格，向 1 方向移動 1 格！")
                    char.move(-1, tiles)
                elif effect == "rift":
                    random.shuffle(tiles[current_pos])
                    print(f"🌀 {char.name} 觸發空間裂隙！第 {current_pos} 格順序重組為: {[c.name for c in tiles[current_pos]]}")
                
            # 3. 檢查一般的中點觸發 (正常位移跨過)
            # 注意：某些角色如愛彌斯是在自己的 take_turn 裡面處理這個邏輯
            if not char.has_triggered_special and old_pos < MIDPOINT <= char.position:
                char.on_pass_midpoint(tiles)
                char.has_triggered_special = True
        
        # 顯示進度
        if round_num % 5 == 0 or round_num == 1:
            print(f"\n第 {round_num} 回合戰報:")
            for i, stack in enumerate(tiles):
                if stack:
                    print(f"  格子 {i:02d}: {[c.name for c in stack]}")
        
        # 檢查勝負
        # 1. 處理抵達 1 格的逆向者 (布大王無限循環)
        winners_rev = [c for c in tiles[1] if c.direction == -1]
        for rev_char in winners_rev:
            print(f"🔄 {rev_char.name} 已衝回 1 格，立刻重生回到 32 格繼續掃街！")
            
            # 從 1 號格移除
            tiles[1].remove(rev_char)
            
            # 重置到 32 號格 (依然鑽到最下面)
            rev_char.position = 32
            tiles[32].insert(0, rev_char)
            
        # 2. 檢查是否有正向者抵達 32 格 (真正的勝負)
        winners_fwd = [c for c in tiles[COURSE_LENGTH] if c.direction == 1]
        if winners_fwd:
            winner = winners_fwd[-1]
            print(f"\n🏁 第 {round_num} 回合，{winner.name} 成功抵達終點 32 格！")
            break

    print("\n=== 模擬結束 ===")

if __name__ == "__main__":
    run_simulation(max_rounds=999)
