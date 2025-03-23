# character.py
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Character:
    name: str
    endurance: int
    scavenging: int
    charisma: int
    combat: int
    crafting: int
    resources: Dict[str, int] = field(default_factory=lambda: {
        "wood": 0,
        "water": 0,
        "food": 0,
        "rope": 5
    })
    base_upgrades: list[str] = field(default_factory=list)
    current_ap: int = 0
    current_day: int = 1
    objectives_completed: Dict[str, bool] = field(default_factory=lambda: {
        "gather_basics": False,
        "build_shop": False,
        "go_adventure": False
    })
    camp_members: list = field(default_factory=list)

    def __post_init__(self):
        self.current_ap = self.action_points

    def refresh_day(self):
        self.current_ap = self.action_points
        self.current_day += 1

    @property
    def action_points(self) -> int:
        return self.endurance * 2

    @property
    def trade_value_bonus(self) -> float:
        return self.charisma * 0.1  # 10% bonus per point

    @property
    def survival_chance(self) -> float:
        return (self.combat * 0.6 + self.endurance * 0.4) * 0.1  # 10% per weighted point

    @property
    def resource_efficiency(self) -> float:
        return self.crafting * 0.15  # 15% bonus per point

# Character presets
CHARACTER_PRESETS = {
    "Survivor": Character(
        name="",
        endurance=8,    # Primary
        scavenging=4,   # Secondary
        charisma=2,
        combat=4,       # Secondary
        crafting=2,
        camp_members=[]
    ),
    "Scavenger": Character(
        name="",
        endurance=4,    # Secondary
        scavenging=8,   # Primary
        charisma=3,
        combat=2,
        crafting=3,
        camp_members=[]
    ),
    "Trader": Character(
        name="",
        endurance=3,
        scavenging=4,   # Secondary
        charisma=8,     # Primary
        combat=2,
        crafting=3
    ),
    "Fighter": Character(
        name="",
        endurance=4,    # Secondary
        scavenging=2,
        charisma=2,
        combat=8,       # Primary
        crafting=4      # Secondary
    ),
    "Engineer": Character(
        name="",
        endurance=3,
        scavenging=4,   # Secondary
        charisma=2,
        combat=3,
        crafting=8      # Primary
    ),
    "Jack of All Trades": Character(
        name="",
        endurance=5,
        scavenging=5,
        charisma=5,
        combat=5,
        crafting=5
    )
}