from dataclasses import dataclass
from typing import Dict, List, Type

from .characters import (
    AmisTuanzi, AugustaTuanzi, CalcharoTuanzi, ChangliTuanzi,
    ChisakiTuanzi, ColettaTuanzi, DaniaTuanzi, FeixueTuanzi,
    JinhsiTuanzi, KatishiaTuanzi, KingBuTuanzi, LinneTuanzi,
    LucaixTuanzi, MorningTuanzi, PhoebeTuanzi, PhroroTuanzi,
    ShorekeeperTuanzi, SigelicaTuanzi, YunoTuanzi,
)
from .models import Tuanzi


@dataclass(frozen=True)
class ParticipantSpec:
    character_class: Type[Tuanzi]
    start_pos: int = 1

    def create(self) -> Tuanzi:
        return self.character_class(start_pos=self.start_pos)


CHARACTER_CLASSES: Dict[str, Type[Tuanzi]] = {
    "千咲": ChisakiTuanzi,
    "菲比": PhoebeTuanzi,
    "緋雪": FeixueTuanzi,
    "莫寧": MorningTuanzi,
    "琳奈": LinneTuanzi,
    "愛彌斯": AmisTuanzi,
    "守岸人": ShorekeeperTuanzi,
    "珂萊塔": ColettaTuanzi,
    "布大王": KingBuTuanzi,
    "奧古斯塔": AugustaTuanzi,
    "尤諾": YunoTuanzi,
    "弗洛洛": PhroroTuanzi,
    "長離": ChangliTuanzi,
    "今汐": JinhsiTuanzi,
    "卡卡羅": CalcharoTuanzi,
    "陸赫斯": LucaixTuanzi,
    "達妮婭": DaniaTuanzi,
    "西格莉卡": SigelicaTuanzi,
    "卡提希婭": KatishiaTuanzi,
}

DEFAULT_PARTICIPANTS = [
    ParticipantSpec(KatishiaTuanzi, start_pos=1),
    ParticipantSpec(YunoTuanzi, start_pos=1),
    ParticipantSpec(JinhsiTuanzi, start_pos=1),
    ParticipantSpec(PhoebeTuanzi, start_pos=1),
    ParticipantSpec(FeixueTuanzi, start_pos=1),
    ParticipantSpec(MorningTuanzi, start_pos=1),
    ParticipantSpec(KingBuTuanzi, start_pos=32),
]


def create_default_participants() -> List[Tuanzi]:
    return [spec.create() for spec in DEFAULT_PARTICIPANTS]


def create_participants_from_states(initial_states: Dict[str, Dict[str, int]]) -> List[Tuanzi]:
    characters = []
    for name, state in initial_states.items():
        char = CHARACTER_CLASSES[name](start_pos=state["pos"])
        char.remaining_distance = state["dist"]
        if char.position >= 16:
            char.has_triggered_special = True
        characters.append(char)
    return characters


def default_initial_states() -> Dict[str, Dict[str, int]]:
    return {
        char.name: {"pos": char.position, "dist": char.remaining_distance}
        for char in create_default_participants()
    }


def competitor_names(characters: List[Tuanzi]) -> List[str]:
    return [char.name for char in characters if not isinstance(char, KingBuTuanzi)]


def default_competitor_names() -> List[str]:
    return competitor_names(create_default_participants())
