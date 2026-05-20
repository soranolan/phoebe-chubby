import random
from .board import DEFAULT_MAP
from .logging import actor_name, event_name
from .characters import KingBuTuanzi
from .roster import create_default_participants

def run_simulation(max_rounds=999):
    # --- 定義上半場起始狀態 ---
    characters_in_order = create_default_participants()

    tiles = DEFAULT_MAP.create_tiles()
    for char in characters_in_order:
        # 上半場從 1 號位出發，技能尚未觸發
            
        # 放置團子
        if char.insert_at_bottom:
            tiles[char.position].insert(0, char)
        else:
            tiles[char.position].append(char)

    characters = list(characters_in_order)
    random.shuffle(characters)

    print("=== 鳴潮小團快跑 模擬開始 (上半場) ===")
    print("📢 獲勝條件：將剩餘里程扣至 0 或以下者獲勝！")
    
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
            round_rolls[char] = char.roll_dice()
            
        # 呼叫擲骰後的勾子 (例如西格莉卡標記排名較高者)
        if round_num > 1: # 首輪僅決定順序不發動
            for char in list(characters):
                char.after_rolls(round_rolls, tiles, verbose=True)

        for char in list(characters):
            # 特技觸發：剩餘里程 ≤ 16 代表已跑超過一半
            if not char.has_triggered_special and char.remaining_distance <= 16:
                char.on_pass_midpoint(tiles)
                char.has_triggered_special = True

            roll = round_rolls[char]
            char.step_modifier_reason = ""
            calculated_steps = char.calculate_steps(roll, round_rolls, tiles)
            
            steps = calculated_steps - char.step_debuff
            if steps < calculated_steps and char.step_debuff > 0:
                steps = max(1, steps)
            
            # is_skipping 由 calculate_steps 動態決定 (如奧古斯塔的技能)
            if char.is_skipping:
                print(
                    f"😴 {actor_name(char.name)} | {event_name('休息')} | "
                    f"待在第 {char.position:02d} 格 | 剩 {char.remaining_distance:>3}"
                )
                char.on_turn_end(tiles, forced_last_queue_next, verbose=True)
                continue

            old_dist = char.remaining_distance
            old_pos = char.position
            char.move(steps, tiles, verbose=True)
            
            msg = f"🎲 {actor_name(char.name)} | {event_name('擲骰')} | {roll} 點"
            if steps != roll:
                if char.step_modifier_reason:
                    msg += f" ({char.step_modifier_reason}，技能修正為 {steps} 步)"
                else:
                    msg += f" (技能修正為 {steps} 步)"
            
            msg += f" | 從第 {old_pos:02d} 格出發 | 剩 {old_dist:>3}"
            print(msg)
            print(
                f"🏃 {actor_name(char.name)} | {event_name('移動')} | "
                f"到了第 {char.position:02d} 格 | 剩 {char.remaining_distance:>3}"
            )

            effect = DEFAULT_MAP.effect_at(char.position)
            if effect:
                bonus = char.tile_effect_bonus(effect)
                
                if effect == "f1":
                    total_steps = 1 + bonus
                    print(f"🚀 {actor_name(char.name)} | {event_name('加速')} | 額外前進 {total_steps} 格")
                    if total_steps != 0:
                        char.move(total_steps, tiles, verbose=True)
                elif effect == "b1":
                    total_steps = -1 + bonus
                    print(f"⚠️  {actor_name(char.name)} | {event_name('陷阱')} | 倒退 {abs(total_steps)} 格")
                    if total_steps != 0:
                        char.move(total_steps, tiles, verbose=True)
                elif effect == "rift":
                    print(
                        f"🌀 {actor_name(char.name)} | {event_name('裂隙')} | "
                        f"第 {char.position:02d} 格順序重組為: ",
                        end=""
                    )
                    random.shuffle(tiles[char.position])
                    print([c.name for c in tiles[char.position]])
                print(
                    f"📍 {actor_name(char.name)} | {event_name('結果')} | "
                    f"最終位於第 {char.position:02d} 格 | 剩 {char.remaining_distance:>3}"
                )
            
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
