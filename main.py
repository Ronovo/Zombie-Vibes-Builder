import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict
from random import random, choice

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

    def __post_init__(self):
        self.current_ap = self.action_points

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

    def refresh_day(self):
        self.current_ap = self.action_points
        self.current_day += 1

CHARACTER_PRESETS = {
    "Survivor": Character(
        name="",
        endurance=8,    # Primary
        scavenging=4,   # Secondary
        charisma=2,
        combat=4,       # Secondary
        crafting=2
    ),
    "Scavenger": Character(
        name="",
        endurance=4,    # Secondary
        scavenging=8,   # Primary
        charisma=3,
        combat=2,
        crafting=3
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

# First, let's create our scenario dictionaries
ADVENTURE_SCENARIOS = {
    "city": {
        "mall": {
            "good": [
                "You discover a cache of valuable electronics!",
                "You find an untouched storage area full of preserved goods!",
                "A friendly group of traders welcomes you to their temporary camp."
            ],
            "neutral": [
                "You find some common supplies. Better than nothing.",
                "The area is picked clean but at least it was safe.",
                "You exchange information with neutral scavengers."
            ],
            "bad": [
                "Part of the ceiling collapses, forcing you to retreat.",
                "A small horde of zombies notices you.",
                "Local bandits demand you leave their territory."
            ]
        },
        "hospital": {
            "good": [
                "You find a stash of valuable medical supplies!",
                "Untouched medical equipment - perfect for trading!",
                "You meet a grateful doctor who promises to visit your base."
            ],
            "neutral": [
                "You salvage some basic first aid supplies.",
                "The darkness limits your search, but you stay safe.",
                "You have a peaceful standoff with other scavengers."
            ],
            "bad": [
                "The air feels wrong here - better leave quickly.",
                "Zombies have you cornered in the pharmacy.",
                "You knock over some chemicals and retreat from the fumes."
            ]
        },
        "residential": {
            "good": [
                "You find a well-preserved food cache!",
                "A garage full of useful tools and materials!",
                "You help a family in need - they won't forget this."
            ],
            "neutral": [
                "You gather scattered supplies from various houses.",
                "Most houses are looted, but you stay hopeful.",
                "Cautious residents watch you from afar."
            ],
            "bad": [
                "A pack of dogs guards this neighborhood.",
                "Armed residents make it clear you're not welcome.",
                "The floorboards give way beneath you."
            ]
        }
    },
    "woods": {
        "river": {
            "good": [
                "You discover a clean water source!",
                "Abandoned camping supplies in pristine condition!",
                "You find an excellent fishing spot!"
            ],
            "neutral": [
                "You collect a bit of water - it's something.",
                "You spot some animal tracks but nothing else.",
                "You share the river with peaceful hunters."
            ],
            "bad": [
                "You lose your way in the thick forest.",
                "This water doesn't look safe to drink.",
                "Something large is stalking you..."
            ]
        },
        "ranger_station": {
            "good": [
                "You find detailed maps of the area!",
                "A cache of survival gear - jackpot!",
                "The radio still works - this could be valuable!"
            ],
            "neutral": [
                "You find some basic camping supplies.",
                "The station is empty but provides good shelter.",
                "Other explorers share some useful information."
            ],
            "bad": [
                "You've stumbled upon a bear's den.",
                "An old trap nearly catches you.",
                "The station's roof looks ready to cave in."
            ]
        },
        "campground": {
            "good": [
                "You find a stockpile of preserved food!",
                "Quality camping gear - perfect for trading!",
                "Friendly survivors share their supplies."
            ],
            "neutral": [
                "You gather scattered camping supplies.",
                "The campground is empty but peaceful.",
                "Some supplies are salvageable, some ruined."
            ],
            "bad": [
                "This camp is already claimed - and guarded.",
                "Zombies are shambling through the camp.",
                "Smoke in the distance - forest fire!"
            ]
        }
    }
}

def create_character_directory():
    Path("Characters").mkdir(exist_ok=True)

def display_character_stats(character: Character):
    print("\n=== Core Stats ===")
    print(f"Endurance (END): {character.endurance}")
    print(f"Scavenging (SCV): {character.scavenging}")
    print(f"Charisma (CHA): {character.charisma}")
    print(f"Combat (CMB): {character.combat}")
    print(f"Crafting (CRF): {character.crafting}")
    
    print("\n=== Derived Stats ===")
    print(f"Action Points (AP): {character.action_points}")
    print(f"Trade Value Bonus: {character.trade_value_bonus:.1%}")
    print(f"Survival Chance: {character.survival_chance:.1%}")
    print(f"Resource Efficiency: {character.resource_efficiency:.1%}")

def create_character() -> Character:
    while True:
        print("\n=== Character Presets ===")
        for idx, preset_name in enumerate(CHARACTER_PRESETS.keys(), 1):
            print(f"{idx}. {preset_name}")
        
        try:
            choice = int(input("\nSelect a preset (1-6): "))
            if 1 <= choice <= 6:
                preset_name = list(CHARACTER_PRESETS.keys())[choice - 1]
                selected_preset = CHARACTER_PRESETS[preset_name]
                
                print(f"\nYou selected: {preset_name}")
                display_character_stats(selected_preset)
                
                confirm = input("\nDo you want to use this preset? (y/n): ").lower()
                if confirm == 'y':
                    return selected_preset
            else:
                print("\nInvalid choice! Please select 1-6.")
        except ValueError:
            print("\nPlease enter a valid number!")

def save_character(character: Character):
    create_character_directory()
    character_data = {
        "name": character.name,
        "endurance": character.endurance,
        "scavenging": character.scavenging,
        "charisma": character.charisma,
        "combat": character.combat,
        "crafting": character.crafting,
        "resources": character.resources,
        "base_upgrades": character.base_upgrades,
        "current_ap": character.current_ap,
        "current_day": character.current_day,
        "objectives_completed": character.objectives_completed
    }
    
    file_path = f"Characters/{character.name}.json"
    with open(file_path, 'w') as f:
        json.dump(character_data, f, indent=4)
    print(f"\nCharacter '{character.name}' saved successfully!")

def load_characters():
    create_character_directory()
    character_files = list(Path("Characters").glob("*.json"))
    
    if not character_files:
        print("\nNo Saved Games Found...")
        return None
    
    print("\nAvailable Characters:")
    for idx, char_file in enumerate(character_files, 1):
        name = char_file.stem  # Gets filename without extension
        print(f"{idx}. {name}")
    
    return character_files

def load_character_from_json(file_path: Path) -> Character:
    with open(file_path, 'r') as f:
        data = json.load(f)
    character = Character(
        name=data['name'],
        endurance=data['endurance'],
        scavenging=data['scavenging'],
        charisma=data['charisma'],
        combat=data['combat'],
        crafting=data['crafting']
    )
    character.resources = data.get('resources', {"wood": 0, "water": 0, "food": 0, "rope": 5})
    character.base_upgrades = data.get('base_upgrades', [])
    character.current_ap = data.get('current_ap', character.action_points)
    character.current_day = data.get('current_day', 1)
    character.objectives_completed = data.get('objectives_completed', 
        {"gather_basics": False, "build_shop": False, "go_adventure": False})
    return character

def determine_character_class(character: Character) -> str:
    # Find which preset this character most closely matches
    stats = [
        character.endurance,
        character.scavenging,
        character.charisma,
        character.combat,
        character.crafting
    ]
    max_stat = max(stats)
    
    if all(stat == stats[0] for stat in stats):
        return "Jack of All Trades"
    
    match stats.index(max_stat):
        case 0: return "Survivor"
        case 1: return "Scavenger"
        case 2: return "Trader"
        case 3: return "Fighter"
        case 4: return "Engineer"

def display_menu():
    print("\n" + "="*40)
    print("    Zombie Vibe Builder v0.1")
    print("="*40)
    print("\n1. Start New Game")
    print("2. Load Game")
    print("3. Credits")
    print("4. Quit")
    print("\n" + "="*40)

def display_game_menu(character: Character):
    print("\n" + "="*40)
    print("    Zombie Vibe Builder v0.1")
    print("="*40)
    print(f"\nDay: {character.current_day}")
    print(f"Action Points: {character.current_ap}/{character.action_points}")
    print("\n1. Look for Resources")
    print("2. Go on an Adventure")
    print("3. Build Base Upgrades")
    print("4. Check Character")
    print("5. Objectives")
    print("6. Check Base Resources")
    print("7. Quit to Main Menu")
    print("\n" + "="*40)

def display_objectives(character: Character):
    print("\n=== Current Objectives ===")
    print("1. Harvest at least 1 food and 1 water" + 
          (" -DONE" if character.objectives_completed["gather_basics"] else ""))
    print("2. Build a shop counter" + 
          (" -DONE" if character.objectives_completed["build_shop"] else ""))
    print("3. Go on an adventure" + 
          (" -DONE" if character.objectives_completed["go_adventure"] else ""))

def check_objectives(character: Character):
    # Check gather basics objective
    if character.resources["food"] >= 1 and character.resources["water"] >= 1:
        character.objectives_completed["gather_basics"] = True

def check_ap_and_day(character: Character):
    if character.current_ap <= 0:
        print("\nOut of Action Points! Starting new day...")
        character.refresh_day()
        input("\nPress Enter to continue...")

def gather_resources(character: Character):
    if character.current_ap <= 0:
        print("\nNot enough Action Points! Rest to recover.")
        return

    print("\n=== Gather Resources ===")
    print("Available resources to gather:")
    print("1. Wood")
    print("2. Water")
    print("3. Food")
    print("4. Cancel")

    try:
        choice = int(input("\nWhat would you like to gather? (1-4): "))
        
        if choice == 4:
            return

        if choice in [1, 2, 3]:
            character.current_ap -= 1
            
            # Base chance is 30% + 5% per scavenging point
            success_chance = 0.3 + (character.scavenging * 0.05)
            success_chance = min(success_chance, 0.95)  # Cap at 95%
            
            resource_map = {1: "wood", 2: "water", 3: "food"}
            resource = resource_map[choice]
            
            import random
            if random.random() < success_chance:
                # Base amount is 1-3 + scavenging bonus
                amount = random.randint(1, 3) + (character.scavenging // 3)
                character.resources[resource] += amount
                print(f"\nSuccess! Found {amount} {resource}!")
            else:
                print("\nNo luck this time...")

            print(f"\nAction Points remaining: {character.current_ap}")
            check_objectives(character)
            check_ap_and_day(character)
        else:
            print("\nInvalid choice!")
    except ValueError:
        print("\nPlease enter a valid number!")

def display_character_status(character: Character):
    print(f"\nCharacter Status - {character.name}")
    char_class = determine_character_class(character)
    print(f"Class: {char_class}")
    print(f"Action Points: {character.current_ap}/{character.action_points}")
    
    print("\n=== Resources ===")
    for resource, amount in character.resources.items():
        print(f"{resource.capitalize()}: {amount}")
    
    print("\n=== Stats ===")
    display_character_stats(character)

def display_base_resources(character: Character):
    print("\n=== Base Resources ===")
    print("\nResources:")
    for resource, amount in character.resources.items():
        print(f"{resource.capitalize()}: {amount}")
    
    print("\nBase Upgrades:")
    if character.base_upgrades:
        for idx, upgrade in enumerate(character.base_upgrades, 1):
            print(f"{idx}. {upgrade}")
    else:
        print("No upgrades built yet.")

def check_build_requirements(character: Character, wood_needed: int, rope_needed: int) -> bool:
    return (character.resources["wood"] >= wood_needed and 
            character.resources["rope"] >= rope_needed)

def build_base_upgrade(character: Character):
    print("\n=== Build Base Upgrades ===")
    print("\nAvailable Upgrades:")
    print("1. Shop Counter (Costs: 10 wood, 2 rope)")
    print("2. Cancel")

    try:
        choice = int(input("\nWhat would you like to build? (1-2): "))
        
        match choice:
            case 1:
                if "Shop Counter" in character.base_upgrades:
                    print("\nYou already have a Shop Counter!")
                    return

                if check_build_requirements(character, 10, 2):
                    confirm = input("\nBuild Shop Counter? (y/n): ").lower()
                    if confirm == 'y':
                        character.resources["wood"] -= 10
                        character.resources["rope"] -= 2
                        character.base_upgrades.append("Shop Counter")
                        character.objectives_completed["build_shop"] = True
                        print("\nShop Counter built successfully!")
                else:
                    print("\nYou need 10 wood and 2 rope to build this...")
            
            case 2:
                return
            
            case _:
                print("\nInvalid choice!")
    
    except ValueError:
        print("\nPlease enter a valid number!")

def determine_outcome(character: Character, location: str) -> str:
    # Base chances: 20% good, 50% neutral, 30% bad
    roll = random()
    
    # Adjust based on relevant stats
    if location in ["mall", "hospital", "residential"]:
        # City locations benefit from Scavenging and Charisma
        bonus = (character.scavenging * 0.02) + (character.charisma * 0.01)
    else:
        # Woods locations benefit from Survival and Combat
        bonus = (character.endurance * 0.02) + (character.combat * 0.01)
    
    roll += bonus
    
    if roll > 0.8:
        return "good"
    elif roll > 0.3:
        return "neutral"
    else:
        return "bad"

def go_on_adventure(character: Character):
    if character.current_ap < 2:
        print("\nNot enough Action Points! (Requires 2 AP)")
        return

    while True:
        print("\n=== Choose Adventure Location ===")
        print("1. City")
        print("2. Woods")
        print("3. Cancel")

        try:
            location_choice = int(input("\nWhere would you like to go? (1-3): "))
            
            if location_choice == 3:
                return
                
            if location_choice in [1, 2]:
                location_type = "city" if location_choice == 1 else "woods"
                
                print(f"\n=== Choose {location_type.title()} Location ===")
                if location_type == "city":
                    print("1. Abandoned Mall")
                    print("2. Hospital")
                    print("3. Residential District")
                else:
                    print("1. River Expedition")
                    print("2. Ranger Station")
                    print("3. Abandoned Campground")
                print("4. Go Back")

                sub_choice = int(input("\nWhere would you like to explore? (1-4): "))
                
                if sub_choice == 4:
                    continue
                    
                if sub_choice in [1, 2, 3]:
                    # Map sub_choice to location name
                    location_map = {
                        "city": {1: "mall", 2: "hospital", 3: "residential"},
                        "woods": {1: "river", 2: "ranger_station", 3: "campground"}
                    }
                    
                    location = location_map[location_type][sub_choice]
                    outcome = determine_outcome(character, location)
                    
                    print("\n" + "="*40)
                    print(choice(ADVENTURE_SCENARIOS[location_type][location][outcome]))
                    print("="*40)
                    
                    character.current_ap -= 2
                    character.objectives_completed["go_adventure"] = True
                    print(f"\nAction Points remaining: {character.current_ap}")
                    check_ap_and_day(character)
                    return
                
            print("\nInvalid choice!")
        except ValueError:
            print("\nPlease enter a valid number!")

def play_game(character: Character):
    while True:
        display_game_menu(character)
        try:
            choice = int(input("\nEnter your choice (1-7): "))
            
            match choice:
                case 1:
                    gather_resources(character)
                
                case 2:
                    go_on_adventure(character)
                
                case 3:
                    build_base_upgrade(character)
                
                case 4:
                    display_character_status(character)
                    input("\nPress Enter to continue...")
                
                case 5:
                    display_objectives(character)
                    input("\nPress Enter to continue...")
                
                case 6:
                    display_base_resources(character)
                    input("\nPress Enter to continue...")
                
                case 7:
                    print("\nSaving and returning to main menu...")
                    save_character(character)
                    return
                
                case _:
                    print("\nInvalid choice! Please select 1-7.")
        
        except ValueError:
            print("\nPlease enter a valid number!")

def main():
    while True:
        display_menu()
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            
            match choice:
                case 1:
                    print("\nStarting new game...")
                    
                    player_name = input("Enter your character name: ").strip()
                    if player_name:
                        character = create_character()
                        character.name = player_name
                        save_character(character)
                        play_game(character)  # Start the game with new character
                    else:
                        print("Invalid name!")
                
                case 2:
                    print("\nLoading game...")
                    character_files = load_characters()
                    if character_files:
                        try:
                            char_choice = int(input("\nSelect a character (or 0 to cancel): "))
                            if 0 < char_choice <= len(character_files):
                                selected_file = character_files[char_choice - 1]
                                character = load_character_from_json(selected_file)
                                char_class = determine_character_class(character)
                                print(f"\nLoaded character: {character.name}")
                                print(f"Character Class: {char_class}")
                                display_character_stats(character)
                                input("\nPress Enter to start game...")
                                play_game(character)  # Start the game with loaded character
                            elif char_choice == 0:
                                print("\nLoad cancelled.")
                            else:
                                print("\nInvalid selection!")
                        except ValueError:
                            print("\nPlease enter a valid number!")
                
                case 3:
                    print("\nDisplaying credits...")
                    # Add credits display logic here
                
                case 4:
                    print("\nThanks for playing! Goodbye!")
                    break
                
                case _:
                    print("\nInvalid choice! Please select 1-4.")
        
        except ValueError:
            print("\nPlease enter a valid number!")

if __name__ == "__main__":
    main()