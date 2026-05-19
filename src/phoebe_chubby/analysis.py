import random
import sys
import time
from typing import List, Dict
from .characters import (
    AugustaTuanzi, YunoTuanzi, PhroroTuanzi,
    ChangliTuanzi, JinhsiTuanzi, CalcharoTuanzi,
    KingBuTuanzi, LucaixTuanzi, DaniaTuanzi,
    ChisakiTuanzi, ColettaTuanzi, SigelicaTuanzi,
    KatishiaTuanzi, LinneTuanzi, PhoebeTuanzi,
    AmisTuanzi, ShorekeeperTuanzi, FeixueTuanzi,
    MorningTuanzi
)
from .logging import pad_display
from .models import Tuanzi

COURSE_LENGTH = 32
QUALIFY_RANK = 3


def ordinal(rank: int) -> str:
    if 10 <= rank % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(rank % 10, "th")
    return f"{rank}{suffix}"


def pct(count: int, total: int) -> float:
    return count / total * 100 if total else 0


def pct_cell(count: int, total: int) -> str:
    return f"{pct(count, total):>6.2f}%"


def print_table(headers: List[str], rows: List[List[str]]):
    print(" | ".join(headers))
    print("-" * (sum(len(cell) for cell in headers) + 3 * (len(headers) - 1)))
    for row in rows:
        print(" | ".join(row))

def run_single_analysis_match(initial_states=None):
    """
    執行單場里程制比賽。
    :param initial_states: 初始狀態 Dict, 例如 {"長離": {"pos": 32, "dist": 32}, ...}
    """
    class_map = {
        "弗洛洛": PhroroTuanzi, "西格莉卡": SigelicaTuanzi,
        "尤諾": YunoTuanzi, "卡卡羅": CalcharoTuanzi, "琳奈": LinneTuanzi,
        "卡提希婭": KatishiaTuanzi, "菲比": PhoebeTuanzi,
        "愛彌斯": AmisTuanzi, "今汐": JinhsiTuanzi,
        "守岸人": ShorekeeperTuanzi, "緋雪": FeixueTuanzi,
        "莫寧": MorningTuanzi, "布大王": KingBuTuanzi
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
            PhoebeTuanzi(), CalcharoTuanzi(), MorningTuanzi(),
            PhroroTuanzi(), LinneTuanzi(), FeixueTuanzi(),
            KingBuTuanzi()
        ]
        for char in characters:
            char.remaining_distance = 999 if isinstance(char, KingBuTuanzi) else 32
        
    random.shuffle(characters)
    
    tiles = [[] for _ in range(COURSE_LENGTH + 1)]
    for char in characters:
        if char.insert_at_bottom:
            tiles[char.position].insert(0, char)
        else:
            tiles[char.position].append(char)

    TILE_EFFECTS = {
        4: "f1", 6: "rift", 10: "f1", 14: "rift",
        16: "b1", 20: "f1", 23: "rift", 26: "b1",
        30: "b1"
    }

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
        
        round_rolls = {char: char.roll_dice() for char in characters}
        
        if round_num > 1:
            for char in list(characters):
                char.after_rolls(round_rolls, tiles, verbose=False)
        
        for char in list(characters):
            # 特技觸發：剩餘里程 ≤ 16 代表已跑超過一半
            if not char.has_triggered_special and char.remaining_distance <= 16:
                char.on_pass_midpoint(tiles, verbose=False)
                char.has_triggered_special = True

            roll = round_rolls[char]
            char.step_modifier_reason = ""
            calculated_steps = char.calculate_steps(roll, round_rolls, tiles)
            
            steps = calculated_steps - char.step_debuff
            if steps < calculated_steps and char.step_debuff > 0:
                steps = max(1, steps)

            # is_skipping 由 calculate_steps 動態決定 (如奧古斯塔的技能)
            if char.is_skipping:
                char.on_turn_end(tiles, forced_last_queue_next, verbose=False)
                continue

            char.move(steps, tiles)
            
            effect = TILE_EFFECTS.get(char.position)
            if effect:
                bonus = char.tile_effect_bonus(effect)
                if effect == "f1":
                    total_steps = 1 + bonus
                    if total_steps != 0:
                        char.move(total_steps, tiles)
                elif effect == "b1":
                    total_steps = -1 + bonus
                    if total_steps != 0:
                        char.move(total_steps, tiles)
                elif effect == "rift":
                    random.shuffle(tiles[char.position])
            
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
    if initial_states:
        char_names = [name for name in initial_states.keys() if name != "布大王"]
    else:
        # 預設名單
        char_names = ["菲比", "卡卡羅", "莫寧", "弗洛洛", "琳奈", "緋雪"]

    stats = {name: {rank: 0 for rank in range(1, len(char_names) + 1)} for name in char_names}

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

    summary = []
    for name, ranks in stats.items():
        avg = sum(r * c for r, c in ranks.items()) / num_trials
        summary.append((name, ranks, avg))
    
    summary.sort(
        key=lambda x: (
            -sum(x[1][rank] for rank in range(1, min(QUALIFY_RANK, len(char_names)) + 1)),
            x[2],
        )
    )

    qualify_rank = min(QUALIFY_RANK, len(char_names))

    print(f"\n\n📊 === 最終平衡性分析報告 (耗時: {duration:.2f} 秒) ===")
    print(f"\n🏁 六進三決策摘要（晉級線：Top {qualify_rank}）")
    summary_headers = [
        pad_display("角色", 10),
        f"{'進前三':^7}",
        f"{'進前三%':^9}",
        f"{'淘汰%':^9}",
        f"{'冠軍%':^9}",
        f"{'墊底%':^9}",
        f"{'平均名次':^10}",
    ]
    summary_rows = []
    for name, ranks, avg in summary:
        qualified = sum(ranks[rank] for rank in range(1, qualify_rank + 1))
        eliminated = num_trials - qualified
        summary_rows.append([
            pad_display(name, 10),
            f"{qualified:^7}",
            pct_cell(qualified, num_trials),
            pct_cell(eliminated, num_trials),
            pct_cell(ranks[1], num_trials),
            pct_cell(ranks[len(char_names)], num_trials),
            f"{avg:^10.2f}",
        ])
    print_table(summary_headers, summary_rows)

    rank_headers = [f"{ordinal(rank):^7}" for rank in range(1, len(char_names) + 1)]

    print("\n📈 名次次數分布")
    count_headers = [pad_display("角色", 10)] + rank_headers + [f"{'平均名次':^10}"]
    count_rows = []
    for name, ranks, avg in summary:
        row = [pad_display(name, 10)]
        row.extend(f"{ranks[rank]:^7}" for rank in range(1, len(char_names) + 1))
        row.append(f"{avg:^10.2f}")
        count_rows.append(row)
    print_table(count_headers, count_rows)

    print("\n📊 單名次機率")
    rate_headers = [pad_display("角色", 10)] + rank_headers
    rate_rows = []
    for name, ranks, _avg in summary:
        row = [pad_display(name, 10)]
        row.extend(pct_cell(ranks[rank], num_trials) for rank in range(1, len(char_names) + 1))
        rate_rows.append(row)
    print_table(rate_headers, rate_rows)

    print("\n📉 累計 TopN 機率")
    cumulative_headers = [pad_display("角色", 10)]
    cumulative_headers.extend(f"{f'Top{rank}':^7}" for rank in range(1, len(char_names) + 1))
    cumulative_rows = []
    for name, ranks, _avg in summary:
        cumulative = 0
        row = [pad_display(name, 10)]
        for rank in range(1, len(char_names) + 1):
            cumulative += ranks[rank]
            row.append(pct_cell(cumulative, num_trials))
        cumulative_rows.append(row)
    print_table(cumulative_headers, cumulative_rows)

if __name__ == "__main__":
    # 設定起始狀態
    initial_states = {
        "菲比": {"pos": 1, "dist": 32},
        "卡卡羅": {"pos": 1, "dist": 32},
        "莫寧": {"pos": 1, "dist": 32},
        "弗洛洛": {"pos": 1, "dist": 32},
        "琳奈": {"pos": 1, "dist": 32},
        "緋雪": {"pos": 1, "dist": 32},
        "布大王": {"pos": 32, "dist": 999}
    }
    
    # 預設執行 10000 場統計
    trials = 10000
    if len(sys.argv) > 1:
        try:
            trials = int(sys.argv[1])
        except ValueError:
            pass
            
    run_batch_analysis(trials, initial_states=initial_states)
