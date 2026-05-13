import random
from .characters import (
    AugustaTuanzi, YunoTuanzi, PhroroTuanzi,
    ChangliTuanzi, JinhsiTuanzi, CalcharoTuanzi,
    KingBuTuanzi
)

COURSE_LENGTH = 32

def run_simulation(max_rounds=999):
    # --- 定義下半場里程數 ---
    # 按照名次設定剩餘里程，第一名剩 32，後面依序增加
    characters_in_order = [
        PhroroTuanzi(start_pos=29),   # 第六名，落後 3 格 -> 32 + 3 = 35
        YunoTuanzi(start_pos=30),     # 第五名，落後 2 格 -> 32 + 2 = 34
        AugustaTuanzi(start_pos=30),  # 第四名，落後 2 格 -> 32 + 2 = 34
        CalcharoTuanzi(start_pos=31), # 第三名，落後 1 格 -> 32 + 1 = 33
        JinhsiTuanzi(start_pos=31),   # 第二名，落後 1 格 -> 32 + 1 = 33
        ChangliTuanzi(start_pos=32),  # 第一名，基準 -> 32
        KingBuTuanzi(start_pos=32)    # 布大王
    ]
    
    # 初始化里程數
    dist_map = {
        "長離": 32, "今汐": 33, "卡卡羅": 33,
        "奧古斯塔": 34, "尤諾": 34, "弗洛洛": 35,
        "布大王": 999 # 布大王不用跑完
    }

    tiles = [[] for _ in range(COURSE_LENGTH + 1)]
    for char in characters_in_order:
        char.remaining_distance = dist_map.get(char.name, 32)
            
        # 如果起始位置就在中點 (16) 之後，預設這圈的技能已用過
        if char.position >= 16:
            char.has_triggered_special = True
            
        # 放置團子
        if char.insert_at_bottom:
            tiles[char.position].insert(0, char)
        else:
            tiles[char.position].append(char)

    characters = list(characters_in_order)
    random.shuffle(characters)

    print("=== 鳴潮小團快跑 模擬開始 (下半場：里程倒數模式) ===")
    print("📢 獲勝條件：將剩餘里程扣至 0 或以下者獲勝！")
    
    TILE_EFFECTS = {
        3: "f1", 6: "rift", 10: "b1", 11: "f1",
        16: "f1", 20: "rift", 23: "f1", 28: "b1"
    }
    
    forced_last_queue_this = []
    forced_last_queue_next = []

    for round_num in range(1, max_rounds + 1):
        print(f"\n📢 [第 {round_num} 回合] 準備決定順序...")
        
        for char in characters:
            char.prepare_round(tiles, forced_last_queue_next)

        if round_num > 1:
            random.shuffle(characters)
            other_chars = [c for c in characters if c not in forced_last_queue_this]
            characters = other_chars + forced_last_queue_this
        
        print("🗺️  當前地圖【堆疊順序】(底層 ➔ 頂層):")
        for i, stack in enumerate(tiles):
            if stack:
                stack_str = " ➔ ".join([f"{c.name}(剩 {c.remaining_distance})" for c in stack])
                print(f"   [格子 {i:02d}] {stack_str}")

        action_names = [c.name for c in characters]
        print(f"🎬 本回合【行動順序】為：「{' ➔ '.join(action_names)}」")

        round_rolls = {}
        for char in characters:
            # 所有人都擲骰，is_skipping 由 calculate_steps 動態決定
                roll = char.roll_dice()
                round_rolls[char] = roll

        for char in list(characters):
            # 特技觸發
            if not char.has_triggered_special and char.position >= 16:
                char.on_pass_midpoint(tiles)
                char.has_triggered_special = True

            roll = round_rolls[char]
            steps = char.calculate_steps(roll, round_rolls, tiles)
            
            # is_skipping 由 calculate_steps 動態決定 (如奧古斯塔的技能)
            if char.is_skipping:
                print(f"😴 {char.name} 本回合休息，待在第 {char.position} 格 (剩 {char.remaining_distance})。")
                char.on_turn_end(tiles, forced_last_queue_next, verbose=True)
                continue

            old_dist = char.remaining_distance
            old_pos = char.position
            char.move(steps, tiles, verbose=True)
            
            msg = f"🎲 {char.name} 擲出了 {roll} 點"
            if steps != roll:
                msg += f" (技能修正為 {steps} 步)"
            
            msg += f"，從第 {old_pos} 格 (剩 {old_dist}) 出發..."
            print(msg)
            print(f"🏃 {char.name} 移動到了第 {char.position} 格 (剩 {char.remaining_distance})。")

            effect = TILE_EFFECTS.get(char.position)
            if effect:
                if effect == "f1":
                    print(f"🚀 {char.name} 踩到加速格！額外前進 1 格。")
                    char.move(1, tiles, verbose=True)
                elif effect == "b1":
                    print(f"⚠️ {char.name} 踩到陷阱格！倒退 1 格。")
                    char.move(-1, tiles, verbose=True)
                elif effect == "rift":
                    print(f"🌀 {char.name} 觸發空間裂隙！第 {char.position} 格順序重組為: ", end="")
                    random.shuffle(tiles[char.position])
                    print([c.name for c in tiles[char.position]])
                print(f"📍 特技後，{char.name} 最終位於第 {char.position} 格 (剩 {char.remaining_distance})。")
            
            # 回合結束勾子 (例如長離的後行判定)
            char.on_turn_end(tiles, forced_last_queue_next, verbose=True)

        # 勝利條件：剩餘里程 <= 0
        winners = [c for c in characters if not isinstance(c, KingBuTuanzi) and c.remaining_distance <= 0]
        if winners:
            print(f"\n🏁 第 {round_num} 回合，{winners[0].name} 成功扣完所有格數，獲得最終勝利！")
            break

        forced_last_queue_this = list(forced_last_queue_next)
        forced_last_queue_next = []

    print("\n=== 模擬結束 ===")

if __name__ == "__main__":
    run_simulation()
