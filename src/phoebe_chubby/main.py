import random
from .characters import (
    AugustaTuanzi, YunoTuanzi, PhroroTuanzi,
    ChangliTuanzi, JinhsiTuanzi, CalcharoTuanzi,
    KingBuTuanzi
)

COURSE_LENGTH = 32
MIDPOINT = COURSE_LENGTH // 2

def run_simulation(max_rounds=999):
    characters = [
        AugustaTuanzi(),
        YunoTuanzi(),
        PhroroTuanzi(),
        ChangliTuanzi(),
        JinhsiTuanzi(),
        CalcharoTuanzi(),
        KingBuTuanzi()
    ]
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
    
    # 用於紀錄「下回合最後行動」的預約隊列
    forced_last_queue_this = []
    forced_last_queue_next = []

    for round_num in range(1, max_rounds + 1):
        # 0. 每一輪開始前，呼叫所有角色的準備動作，並收集下一輪的預約
        for char in characters:
            char.prepare_round(tiles, forced_last_queue_next)

        # 0. 隨機決定行動順序，並將「上一輪預約最後行動」的人按順序排在末尾
        random.shuffle(characters)
        other_chars = [c for c in characters if c not in forced_last_queue_this]
        characters = other_chars + forced_last_queue_this
        
        print(f"\n📢 [第 {round_num} 回合] 準備決定順序...")
        
        # 顯示地圖上的堆疊順序 (影響技能判定，如弗洛洛、今汐、奧古斯塔)
        print("🗺️  當前地圖【堆疊順序】(底層 ➔ 頂層):")
        for i, stack in enumerate(tiles):
            if stack:
                print(f"   [格子 {i:02d}] {' ➔ '.join([c.name for c in stack])}")

        # 顯示引擎決定的行動順序 (影響誰先擲骰子)
        print(f"🎬 本回合【行動順序】(由先 ➔ 後) 為：「{' ➔ '.join([c.name for c in characters])}」")
        
        # 1. 所有人預定點數 (跳過本回合休息的人)
        # 額外規則：布大王前兩回合不准動
        for char in characters:
            if isinstance(char, KingBuTuanzi) and round_num < 3:
                char.is_skipping = True
            elif isinstance(char, KingBuTuanzi):
                char.is_skipping = False
        
        round_rolls = {char: (char.roll_dice() if not char.is_skipping else 0) for char in characters}
        
        for char in list(characters):
            if char.is_skipping:
                print(f"😴 {char.name} 本回合休息中，待在第 {char.position} 格。")
                continue
                
            old_pos = char.position
            roll = round_rolls[char]
            steps = char.calculate_steps(roll, round_rolls, tiles)
            
            step_desc = f"{roll} 點" if steps == roll else f"{roll} 點 (技能修正為 {steps} 步)"
            print(f"🎲 {char.name} 擲出了 {step_desc}，準備從第 {old_pos} 格出發...")
            
            # 1. 執行基礎移動
            char.move(steps, tiles)
            new_pos = char.position
            if new_pos != old_pos:
                print(f"🏃 {char.name} 移動到了第 {new_pos} 格。")
            else:
                print(f"📍 {char.name} 停留在第 {new_pos} 格。")
            
            # 2. 檢查落點是否有賽道特技
            if new_pos != old_pos and new_pos in TILE_EFFECTS:
                effect = TILE_EFFECTS[new_pos]
                if effect == "f1":
                    print(f"🚀 {char.name} 踩到加速格！額外前進 1 格。")
                    char.move(1, tiles)
                elif effect == "b1":
                    print(f"⚠️ {char.name} 踩到陷阱格！倒退 1 格。")
                    char.move(-1, tiles)
                elif effect == "rift":
                    random.shuffle(tiles[new_pos])
                    print(f"🌀 {char.name} 觸發空間裂隙！第 {new_pos} 格順序重組為: {[c.name for c in tiles[new_pos]]}")
                print(f"📍 特技後，{char.name} 最終位於第 {char.position} 格。")
                
            # 3. 檢查一般的中點觸發
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
        
        # 本輪結束，將下一輪的預約名單轉正，並清空下下一輪的預約
        forced_last_queue_this = list(forced_last_queue_next)
        forced_last_queue_next = []

    print("\n=== 模擬結束 ===")

if __name__ == "__main__":
    run_simulation(max_rounds=999)
