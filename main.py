# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from pathlib import Path
import json
from character import Character, CHARACTER_PRESETS
import random
from kivy.uix.boxlayout import BoxLayout

# Set window size (default is usually 800x600, so 10% bigger would be 880x660)
Window.size = (880, 660)

ADVENTURE_SCENARIOS = {
    "city": {
        "abandoned_mall": {
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
        "residential_district": {
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
        "river_expedition": {
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
        "abandoned_campgrounds": {
            "good": [
                "You find a stockpile of preserved food!",
                "Quality camping gear - perfect for trading!",
                "Friendly survivors share their supplies."
            ],
            "neutral": [
                "You gather scattered supplies from various houses.",
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

class MainMenu(Screen):
    pass

class LoadGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_saves()

    def on_pre_enter(self):  # This is called whenever the screen is about to be shown
        self.refresh_saves()  # Refresh the save list before showing the screen

    def refresh_saves(self):
        # Clear previous saves from display
        self.ids.saves_grid.clear_widgets()
        
        # Create Characters directory if it doesn't exist
        Path("Characters").mkdir(exist_ok=True)
        
        # Get all save files
        save_files = list(Path("Characters").glob("*.json"))
        
        if not save_files:
            self.ids.saves_grid.add_widget(Label(
                text="No Saved Games Found...",
                size_hint_y=None,
                height='40dp'
            ))
        else:
            for save_file in save_files:
                btn = Button(
                    text=save_file.stem,
                    size_hint_y=None,
                    height='40dp'
                )
                btn.bind(on_release=lambda x, file=save_file: self.load_character(file))
                self.ids.saves_grid.add_widget(btn)

    def load_character(self, file_path):
        try:
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
            
            # Get the game screen and set the character
            game_screen = self.manager.get_screen('game_screen')
            game_screen.set_character(character)
            
            # Switch to game screen
            self.manager.current = 'game_screen'
            
        except Exception as e:
            popup = Popup(
                title='Error',
                content=Label(text=f'Failed to load save: {str(e)}'),
                size_hint=(None, None),
                size=(400, 200)
            )
            popup.open()

class CharacterCreationScreen(Screen):
    name_input = ObjectProperty(None)
    selected_preset = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.presets = CHARACTER_PRESETS
        
    def select_preset(self, preset_name):
        self.selected_preset = preset_name
        preset = self.presets[preset_name]
        # Update stats display
        self.ids.stats_display.text = (
            f"=== Core Stats ===\n"
            f"Endurance (END): {preset.endurance}\n"
            f"Scavenging (SCV): {preset.scavenging}\n"
            f"Charisma (CHA): {preset.charisma}\n"
            f"Combat (CMB): {preset.combat}\n"
            f"Crafting (CRF): {preset.crafting}\n\n"
            f"=== Derived Stats ===\n"
            f"Action Points (AP): {preset.action_points}\n"
            f"Trade Value Bonus: {preset.trade_value_bonus:.1%}\n"
            f"Survival Chance: {preset.survival_chance:.1%}\n"
            f"Resource Efficiency: {preset.resource_efficiency:.1%}"
        )
    
    def create_character(self):
        if not self.name_input.text or not self.selected_preset:
            popup = Popup(
                title='Error',
                content=Label(text='Please enter a name and select a class'),
                size_hint=(None, None),
                size=(400, 200)
            )
            popup.open()
            return
        
        # Create new character from preset
        character = CHARACTER_PRESETS[self.selected_preset].__class__(
            **{k: v for k, v in vars(CHARACTER_PRESETS[self.selected_preset]).items() 
               if not k.startswith('_')}
        )
        character.name = self.name_input.text.strip()
        
        try:
            if save_character(character):
                # Get the game screen and set the character
                game_screen = self.manager.get_screen('game_screen')
                game_screen.set_character(character)
                
                # Switch to game screen
                self.manager.current = 'game_screen'
        except Exception as e:
            popup = Popup(
                title='Error',
                content=Label(text=f'Failed to save character: {str(e)}'),
                size_hint=(None, None),
                size=(400, 200)
            )
            popup.open()

class ResourceGatheringPopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = "Gather Resources"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        # Create main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Status display
        self.status_label = Label(
            text=f"Action Points: {self.character.current_ap}\n"
                 f"Scavenging Skill: {self.character.scavenging}"
        )
        layout.add_widget(self.status_label)
        
        # Resource buttons
        for resource in ['wood', 'water', 'food']:
            btn = Button(
                text=f"Gather {resource.title()}",
                size_hint_y=None,
                height='40dp'
            )
            btn.resource = resource
            btn.bind(on_release=self.gather_resource)
            layout.add_widget(btn)
        
        # Close button
        self.close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        
        def force_close(instance):
            print("Attempting force close")  # Debug print
            self.dismiss()
            # Force removal from parent if dismiss doesn't work
            if self.parent:
                self.parent.remove_widget(self)
                
        self.close_btn.bind(on_release=force_close)
        layout.add_widget(self.close_btn)
        
        self.content = layout

    def gather_resource(self, instance):
        resource = instance.resource
        if self.character.current_ap <= 0:
            self._show_message("Not enough Action Points!")
            return
        
        self.character.current_ap -= 1
        
        success_chance = 0.3 + (self.character.scavenging * 0.05)
        success_chance = min(success_chance, 0.95)
        
        if random.random() < success_chance:
            amount = random.randint(1, 3) + (self.character.scavenging // 3)
            self.character.resources[resource] += amount
            message = f"Success! Found {amount} {resource}!"
            
            if resource in ['food', 'water']:
                if (self.character.resources['food'] >= 1 and 
                    self.character.resources['water'] >= 1):
                    self.character.objectives_completed['gather_basics'] = True
        else:
            message = f"No luck finding {resource} this time..."
        
        self.status_label.text = (
            f"Action Points: {self.character.current_ap}\n"
            f"Scavenging Skill: {self.character.scavenging}"
        )
        
        self._show_message(message)

    def _show_message(self, text):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=text))
        
        close_button = Button(
            text='Close',
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(close_button)
        
        result_popup = Popup(
            title='Result',
            content=content,
            size_hint=(0.6, 0.4),
            auto_dismiss=False
        )
        
        close_button.bind(on_release=result_popup.dismiss)
        result_popup.open()

class ObjectivesPopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = "Current Objectives"
        self.size_hint = (0.8, 0.8)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Display objectives with completion status
        objectives_text = (
            "1. Harvest at least 1 food and 1 water" +
            (" -DONE" if character.objectives_completed["gather_basics"] else "") +
            "\n\n2. Build a shop counter" +
            (" -DONE" if character.objectives_completed["build_shop"] else "") +
            "\n\n3. Go on an adventure" +
            (" -DONE" if character.objectives_completed["go_adventure"] else "")
        )
        
        layout.add_widget(Label(text=objectives_text))
        
        # Close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        close_btn.bind(on_release=self.dismiss)
        layout.add_widget(close_btn)
        
        self.content = layout

class BaseBuildingPopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = "Build Base Upgrades"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Display current resources
        self.resources_label = Label(
            text=f"Current Resources:\n" +
                 f"Wood: {self.character.resources['wood']}\n" +
                 f"Rope: {self.character.resources['rope']}"
        )
        layout.add_widget(self.resources_label)
        
        # Shop Counter button
        shop_btn = Button(
            text="Build Shop Counter (Costs: 10 wood, 2 rope)",
            size_hint_y=None,
            height='40dp'
        )
        shop_btn.bind(on_release=self.build_shop_counter)
        layout.add_widget(shop_btn)
        
        # Close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        
        def force_close(instance):
            self.dismiss()
            if self.parent:
                self.parent.remove_widget(self)
                
        close_btn.bind(on_release=force_close)
        layout.add_widget(close_btn)
        
        self.content = layout

    def build_shop_counter(self, instance):
        if "Shop Counter" in self.character.base_upgrades:
            self.show_result("You already have a Shop Counter!")
            return
            
        if self.character.resources["wood"] >= 10 and self.character.resources["rope"] >= 2:
            self.character.resources["wood"] -= 10
            self.character.resources["rope"] -= 2
            self.character.base_upgrades.append("Shop Counter")
            self.character.objectives_completed["build_shop"] = True
            
            # Update resources display
            self.resources_label.text = (
                f"Current Resources:\n" +
                f"Wood: {self.character.resources['wood']}\n" +
                f"Rope: {self.character.resources['rope']}"
            )
            
            self.show_result("Shop Counter built successfully!")
        else:
            self.show_result("You need 10 wood and 2 rope to build this...")

    def show_result(self, text):
        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content_layout.add_widget(Label(text=text))
        
        close_button = Button(
            text='Close',
            size_hint_y=None,
            height='40dp'
        )
        content_layout.add_widget(close_button)
        
        result_popup = Popup(
            title='Result',
            content=content_layout,
            size_hint=(0.6, 0.4),
            auto_dismiss=False
        )
        
        close_button.bind(on_release=result_popup.dismiss)
        result_popup.open()

class BaseResourcesPopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = "Base Resources"
        self.size_hint = (0.8, 0.8)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Display resources
        resources_text = (
            "=== Resources ===\n"
            f"Wood: {character.resources['wood']}\n"
            f"Water: {character.resources['water']}\n"
            f"Food: {character.resources['food']}\n"
            f"Rope: {character.resources['rope']}\n\n"
            "=== Base Upgrades ===\n"
        )
        
        if character.base_upgrades:
            for idx, upgrade in enumerate(character.base_upgrades, 1):
                resources_text += f"{idx}. {upgrade}\n"
        else:
            resources_text += "No upgrades built yet."
        
        layout.add_widget(Label(text=resources_text))
        
        # Close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        close_btn.bind(on_release=self.dismiss)
        layout.add_widget(close_btn)
        
        self.content = layout

class DayEndPopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = "Day End"
        self.size_hint = (0.8, 0.8)
        auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Day end message
        layout.add_widget(Label(
            text=f"Day {character.current_day} has ended.\n"
                 f"Your action points have been restored to {character.action_points}."
        ))
        
        # Continue button
        continue_btn = Button(
            text="Continue to Next Day",
            size_hint_y=None,
            height='40dp'
        )
        continue_btn.bind(on_release=self.start_new_day)
        layout.add_widget(continue_btn)
        
        self.content = layout

    def start_new_day(self, instance):
        self.character.refresh_day()
        self.dismiss()

class AdventureResultPopup(Popup):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.title = "Adventure Result"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text=text))
        
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        
        def force_close(instance):
            self.dismiss()
            if self.parent:
                self.parent.remove_widget(self)
                
        close_btn.bind(on_release=force_close)
        layout.add_widget(close_btn)
        
        self.content = layout

class LocationSelectionPopup(Popup):
    def __init__(self, character, location_type, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = f"Select {location_type} Location"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        locations = {
            'city': ['Abandoned Mall', 'Hospital', 'Residential District'],
            'woods': ['River Expedition', 'Ranger Station', 'Abandoned Campgrounds']
        }
        
        for location in locations[location_type]:
            btn = Button(
                text=location,
                size_hint_y=None,
                height='40dp'
            )
            btn.location = location
            btn.location_type = location_type
            btn.bind(on_release=self.start_adventure)
            layout.add_widget(btn)
        
        close_btn = Button(
            text="Back",
            size_hint_y=None,
            height='40dp'
        )
        
        def force_close(instance):
            self.dismiss()
            if self.parent:
                self.parent.remove_widget(self)
                
        close_btn.bind(on_release=force_close)
        layout.add_widget(close_btn)
        
        self.content = layout

    def start_adventure(self, instance):
        if self.character.current_ap < 2:  # Adventures cost 2 AP
            result = "Not enough Action Points! (Requires 2 AP)"
        else:
            self.character.current_ap -= 2
            result = self.determine_outcome(instance.location_type, instance.location)
            self.character.objectives_completed["go_adventure"] = True
        
        result_popup = AdventureResultPopup(text=result)
        result_popup.open()

    def determine_outcome(self, location_type, location):
        base_chance = random.random()
        
        # Adjust chance based on relevant stats
        if location_type == 'city':
            bonus = (self.character.scavenging * 0.02) + (self.character.charisma * 0.01)
        else:  # woods
            bonus = (self.character.endurance * 0.02) + (self.character.combat * 0.01)
        
        final_chance = base_chance + bonus
        
        # Get the appropriate outcome
        if final_chance > 0.8:  # Good outcome (20% + bonuses)
            outcome = ADVENTURE_SCENARIOS[location_type][location.lower().replace(' ', '_')]['good']
        elif final_chance > 0.3:  # Neutral outcome (50%)
            outcome = ADVENTURE_SCENARIOS[location_type][location.lower().replace(' ', '_')]['neutral']
        else:  # Bad outcome (30%)
            outcome = ADVENTURE_SCENARIOS[location_type][location.lower().replace(' ', '_')]['bad']
            
        return random.choice(outcome)

class AdventurePopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = "Choose Adventure Location"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Status display
        self.status_label = Label(
            text=f"Action Points: {self.character.current_ap}\n"
                 f"Adventure will cost: 2 AP"
        )
        layout.add_widget(self.status_label)
        
        # Location type buttons
        city_btn = Button(
            text="City Adventures",
            size_hint_y=None,
            height='40dp'
        )
        city_btn.bind(on_release=lambda x: self.show_locations('city'))
        layout.add_widget(city_btn)
        
        woods_btn = Button(
            text="Woods Adventures",
            size_hint_y=None,
            height='40dp'
        )
        woods_btn.bind(on_release=lambda x: self.show_locations('woods'))
        layout.add_widget(woods_btn)
        
        # Close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        
        def force_close(instance):
            self.dismiss()
            if self.parent:
                self.parent.remove_widget(self)
                
        close_btn.bind(on_release=force_close)
        layout.add_widget(close_btn)
        
        self.content = layout

    def show_locations(self, location_type):
        location_popup = LocationSelectionPopup(self.character, location_type)
        location_popup.open()

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.character = None

    def set_character(self, character):
        self.character = character
        self.update_status()

    def update_status(self):
        if self.character:
            self.ids.status_label.text = (
                f'Day: {self.character.current_day}\n'
                f'Action Points: {self.character.current_ap}/{self.character.action_points}'
            )

    def check_ap_and_day(self):
        if self.character and self.character.current_ap <= 0:
            day_end = DayEndPopup(self.character)
            day_end.bind(on_dismiss=lambda x: self.update_status())
            day_end.open()

    def check_resources(self):
        if not self.character:
            return
        
        resources_popup = BaseResourcesPopup(self.character)
        resources_popup.open()

    def gather_resources(self):
        if not self.character:
            return
        
        gathering_popup = ResourceGatheringPopup(self.character)
        gathering_popup.bind(
            on_dismiss=lambda x: (
                self.update_status(),
                self.check_ap_and_day()
            )
        )
        gathering_popup.open()

    def go_adventure(self):
        if not self.character:
            return
        
        adventure_popup = AdventurePopup(self.character)
        adventure_popup.bind(
            on_dismiss=lambda x: (
                self.update_status(),
                self.check_ap_and_day()
            )
        )
        adventure_popup.open()

    def build_base(self):
        if not self.character:
            return
        
        building_popup = BaseBuildingPopup(self.character)
        building_popup.bind(
            on_dismiss=lambda x: (
                self.update_status(),
                self.check_ap_and_day()
            )
        )
        building_popup.open()

    def check_character(self):
        if not self.character:
            return
        
        status_popup = CharacterStatusPopup(self.character)
        status_popup.open()

    def show_objectives(self):
        if not self.character:
            return
        
        objectives_popup = ObjectivesPopup(self.character)
        objectives_popup.open()

    def quit_to_menu(self):
        if self.character:
            save_character(self.character)
            
            # Create layout for popup content
            content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            # Add save confirmation message
            content_layout.add_widget(Label(text='Game progress saved successfully!'))
            
            # Create close button
            close_button = Button(
                text='Close',
                size_hint_y=None,
                height='40dp'
            )
            content_layout.add_widget(close_button)
            
            # Create popup
            popup = Popup(
                title='Saved!',
                content=content_layout,
                size_hint=(0.6, 0.4),
                auto_dismiss=False  # Makes them use the close button
            )
            
            # Bind close button to both dismiss popup and switch screens
            def on_close(instance):
                popup.dismiss()
                self.manager.current = 'main_menu'
                
            close_button.bind(on_release=on_close)
            
            popup.open()
        else:
            self.manager.current = 'main_menu'

class CharacterStatusPopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = f"Character Status - {character.name}"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Character class
        class_label = Label(
            text=f"Class: {determine_character_class(character)}",
            size_hint_y=None,
            height='40dp'
        )
        layout.add_widget(class_label)
        
        # Core Stats
        core_stats = Label(
            text=(
                "=== Core Stats ===\n"
                f"Endurance (END): {character.endurance}\n"
                f"Scavenging (SCV): {character.scavenging}\n"
                f"Charisma (CHA): {character.charisma}\n"
                f"Combat (CMB): {character.combat}\n"
                f"Crafting (CRF): {character.crafting}"
            ),
            size_hint_y=None,
            height='150dp'
        )
        layout.add_widget(core_stats)
        
        # Derived Stats
        derived_stats = Label(
            text=(
                "=== Derived Stats ===\n"
                f"Action Points: {character.current_ap}/{character.action_points}\n"
                f"Trade Value Bonus: {character.trade_value_bonus:.1%}\n"
                f"Survival Chance: {character.survival_chance:.1%}\n"
                f"Resource Efficiency: {character.resource_efficiency:.1%}"
            ),
            size_hint_y=None,
            height='150dp'
        )
        layout.add_widget(derived_stats)
        
        # Current Day
        day_label = Label(
            text=f"Current Day: {character.current_day}",
            size_hint_y=None,
            height='40dp'
        )
        layout.add_widget(day_label)
        
        # Resources
        resources = Label(
            text=(
                "=== Resources ===\n"
                f"Wood: {character.resources['wood']}\n"
                f"Water: {character.resources['water']}\n"
                f"Food: {character.resources['food']}\n"
                f"Rope: {character.resources['rope']}"
            ),
            size_hint_y=None,
            height='150dp'
        )
        layout.add_widget(resources)
        
        # Base Upgrades
        upgrades_text = "=== Base Upgrades ===\n"
        if character.base_upgrades:
            for upgrade in character.base_upgrades:
                upgrades_text += f"• {upgrade}\n"
        else:
            upgrades_text += "No upgrades built yet"
        
        upgrades = Label(
            text=upgrades_text,
            size_hint_y=None,
            height='100dp'
        )
        layout.add_widget(upgrades)
        
        # Close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        
        def force_close(instance):
            self.dismiss()
            if self.parent:
                self.parent.remove_widget(self)
                
        close_btn.bind(on_release=force_close)
        layout.add_widget(close_btn)
        
        self.content = layout

def save_character(character):
    Path("Characters").mkdir(exist_ok=True)
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
    return True

class ZombieVibeApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name='main_menu'))
        sm.add_widget(CharacterCreationScreen(name='character_creation'))
        sm.add_widget(LoadGameScreen(name='load_game'))
        sm.add_widget(GameScreen(name='game_screen'))
        return sm

if __name__ == '__main__':
    ZombieVibeApp().run()