from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class GameMap:
    length: int
    tile_effects: Dict[int, str]

    def create_tiles(self):
        return [[] for _ in range(self.length + 1)]

    def effect_at(self, position: int) -> Optional[str]:
        return self.tile_effects.get(position)


DEFAULT_MAP = GameMap(
    length=32,
    tile_effects={
        4: "f1", 6: "rift", 10: "f1", 14: "rift",
        16: "b1", 20: "f1", 23: "rift", 26: "b1",
        30: "b1",
    },
)
