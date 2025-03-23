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
from dataclasses import dataclass, field
from typing import Dict
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock

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

FIRST_NAMES = [
    "James", "Emma", "Michael", "Sarah", "David", "Lisa", "John", "Anna", 
    "Robert", "Maria", "William", "Sofia", "Marcus", "Elena", "Thomas", "Nina",
    "Carlos", "Maya", "Hassan", "Yuki", "Igor", "Zara", "Chen", "Aisha"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Chen", "Wong", "Kim", "Singh",
    "Patel", "Ivanov", "Sato", "Cohen", "Weber", "Silva", "Murphy", "O'Connor"
]

VISITOR_TYPES = [
    {"type": "Trader", "join_chance": 0.2, "description": "A cautious trader looking for safe routes.", "ap": 3},
    {"type": "Survivor", "join_chance": 0.4, "description": "A capable survivor seeking shelter.", "ap": 4},
    {"type": "Doctor", "join_chance": 0.15, "description": "A skilled medical professional.", "ap": 2},
    {"type": "Engineer", "join_chance": 0.15, "description": "A practical problem-solver.", "ap": 2},
    {"type": "Scout", "join_chance": 0.3, "description": "An experienced wasteland scout.", "ap": 5}
]

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
            character.camp_members = data.get('camp_members', [])
            character.current_ap = data.get('current_ap', character.action_points)
            character.current_day = data.get('current_day', 1)
            character.objectives_completed = data.get('objectives_completed', 
                {"gather_basics": False, "build_shop": False, "go_adventure": False, "recruit_member": False, "three_members": False})
            
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
        
        # Create new character with all attributes
        character = Character(
            name=self.name_input.text.strip(),
            endurance=CHARACTER_PRESETS[self.selected_preset].endurance,
            scavenging=CHARACTER_PRESETS[self.selected_preset].scavenging,
            charisma=CHARACTER_PRESETS[self.selected_preset].charisma,
            combat=CHARACTER_PRESETS[self.selected_preset].combat,
            crafting=CHARACTER_PRESETS[self.selected_preset].crafting,
            resources={"wood": 0, "water": 0, "food": 0, "rope": 5},
            base_upgrades=[],
            camp_members=[],  # Initialize empty camp members list
            current_ap=CHARACTER_PRESETS[self.selected_preset].endurance * 2,
            current_day=1,
            objectives_completed={
                "gather_basics": False,
                "build_shop": False,
                "go_adventure": False,
                "recruit_member": False,
                "three_members": False
            }
        )
        
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

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

class ObjectivesPopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        
        # Check if all objectives are complete
        all_complete = all(self.character.objectives_completed.values())
        
        if all_complete:
            self.show_victory_popup()
        else:
            self.show_objectives_list()

    def show_victory_popup(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        victory_text = (
            "VICTORY ACHIEVED!!!\n\n"
            "You have beaten this demo of\n"
            "Ronovo's Zombie Vibe Builder!\n\n"
            "Thank you for playing!"
        )
        
        content.add_widget(Label(
            text=victory_text,
            font_size='24sp'
        ))
        
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        close_btn.bind(on_release=self.dismiss)
        content.add_widget(close_btn)
        
        self.content = content
        self.title = "Victory!"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False

    def show_objectives_list(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        objectives_text = (
            "1. Harvest at least 1 food and 1 water" +
            (" -DONE" if self.character.objectives_completed["gather_basics"] else "") +
            "\n\n2. Build a shop counter" +
            (" -DONE" if self.character.objectives_completed["build_shop"] else "") +
            "\n\n3. Go on an adventure" +
            (" -DONE" if self.character.objectives_completed["go_adventure"] else "") +
            "\n\n4. Recruit a new camp member" +
            (" -DONE" if self.character.objectives_completed["recruit_member"] else "") +
            "\n\n5. Have three camp members" +
            (" -DONE" if self.character.objectives_completed["three_members"] else "")
        )
        
        content.add_widget(Label(text=objectives_text))
        
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        close_btn.bind(on_release=self.dismiss)
        content.add_widget(close_btn)
        
        self.content = content
        self.title = "Current Objectives"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

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
        
        # Check if there's anything to build
        if "Shop Counter" not in self.character.base_upgrades:
            # Shop Counter button
            shop_btn = Button(
                text="Build Shop Counter (Costs: 10 wood, 2 rope)",
                size_hint_y=None,
                height='40dp'
            )
            shop_btn.bind(on_release=self.build_shop_counter)
            layout.add_widget(shop_btn)
        else:
            # Nothing to build message
            layout.add_widget(Label(
                text="More upgrades coming soon...",
                size_hint_y=None,
                height='40dp'
            ))
        
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

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

class ManageBasePopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = "Base Management"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Just show the camp members management button
        members_btn = Button(
            text="Manage Survivor Jobs",
            size_hint_y=None,
            height='40dp'
        )
        members_btn.bind(on_release=self.manage_members)
        layout.add_widget(members_btn)
        
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

    def manage_members(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        if not self.character.camp_members:
            content.add_widget(Label(text="No survivors to manage at this time..."))
        else:
            scroll_layout = GridLayout(
                cols=1,
                spacing=10,
                size_hint_y=None
            )
            scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
            
            for member in self.character.camp_members:
                member_box = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height='120dp',
                    padding=5
                )
                
                info_text = (
                    f"{member['name']} - {member['type']}\n"
                    f"Current Job: {member['mode'].title()}"
                )
                member_box.add_widget(Label(text=info_text))
                
                # Center the buttons using AnchorLayout
                anchor_layout = AnchorLayout(
                    anchor_x='center',
                    size_hint_y=None,
                    height='40dp'
                )
                
                buttons_box = BoxLayout(
                    orientation='horizontal',
                    size_hint_x=None,
                    width='310dp',
                    spacing=5
                )
                
                for mode in ['guard', 'gather', 'adventure']:
                    mode_btn = Button(
                        text=mode.title(),
                        size_hint_x=None,
                        width='100dp'
                    )
                    
                    def create_mode_callback(member_name, new_mode):
                        def set_mode(instance):
                            for m in self.character.camp_members:
                                if m['name'] == member_name:
                                    m['mode'] = new_mode
                                    self.refresh_member_management()
                        return set_mode
                    
                    mode_btn.bind(on_release=create_mode_callback(member['name'], mode))
                    buttons_box.add_widget(mode_btn)
                
                anchor_layout.add_widget(buttons_box)
                member_box.add_widget(anchor_layout)
                scroll_layout.add_widget(member_box)
            
            scroll_view = ScrollView(size_hint=(1, 0.8))
            scroll_view.add_widget(scroll_layout)
            content.add_widget(scroll_view)
        
        close_button = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(close_button)
        
        self.member_popup = Popup(
            title="Manage Survivor Jobs",
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        
        def force_close(instance):
            self.member_popup.dismiss()
            if self.member_popup.parent:
                self.member_popup.parent.remove_widget(self.member_popup)
        
        close_button.bind(on_release=force_close)
        self.member_popup.open()

    def refresh_member_management(self):
        """Refresh the member management popup"""
        if hasattr(self, 'member_popup'):
            self.member_popup.dismiss()
            self.manage_members(None)

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

class GuardReportPopup(Popup):
    def __init__(self, character, member_results, game_screen, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.member_results = member_results  # Store all results
        self.game_screen = game_screen  # Store game screen reference
        self.title = "Guard Report"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Guard Reports
        guard_text = "=== Guard Reports ===\n"
        has_guards = False
        for member in self.character.camp_members:
            if member['mode'] == 'guard':
                has_guards = True
                guard_text += f"\n{member['name']} maintained watch"
        
        if not has_guards:
            guard_text += "\nNo guards on duty today"
            
        layout.add_widget(Label(text=guard_text))
        
        # Continue button
        continue_btn = Button(
            text="Continue",
            size_hint_y=None,
            height='40dp'
        )
        continue_btn.bind(on_release=self.show_next)
        layout.add_widget(continue_btn)
        
        self.content = layout

    def show_next(self, instance):
        self.dismiss()
        ResourceReportPopup(
            self.character,
            self.member_results['gathered_resources'],
            self.member_results,
            game_screen=self.game_screen
        ).open()

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

class ResourceReportPopup(Popup):
    def __init__(self, character, gathered_resources, member_results, game_screen, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.character = character
        self.member_results = member_results  # Store complete results
        self.title = "Resource Report"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Resource Reports
        resource_text = "=== Resources Gathered ===\n"
        if sum(gathered_resources.values()) > 0:
            for resource, amount in gathered_resources.items():
                if amount > 0:
                    resource_text += f"\n{resource.title()}: {amount}"
        else:
            resource_text += "\nNo resources gathered today"
            
        layout.add_widget(Label(text=resource_text))
        
        # Continue button
        continue_btn = Button(
            text="Continue",
            size_hint_y=None,
            height='40dp'
        )
        continue_btn.bind(on_release=self.show_next)
        layout.add_widget(continue_btn)
        
        self.content = layout

    def show_next(self, instance):
        self.dismiss()
        AdventureReportPopup(
            self.character,
            self.member_results['adventures'],
            game_screen=self.game_screen
        ).open()

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

class AdventureReportPopup(Popup):
    def __init__(self, character, adventure_results, game_screen, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.character = character
        self.title = "Adventure Report"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Adventure Reports
        adventure_text = "=== Adventure Reports ===\n"
        if adventure_results:
            for report in adventure_results:
                adventure_text += f"\n{report}"
        else:
            adventure_text += "\nNo adventures undertaken today"
            
        layout.add_widget(Label(text=adventure_text))
        
        # Continue button
        continue_btn = Button(
            text="Continue",
            size_hint_y=None,
            height='40dp'
        )
        continue_btn.bind(on_release=self.show_next)
        layout.add_widget(continue_btn)
        
        self.content = layout

    def show_next(self, instance):
        self.dismiss()
        FinalDayReportPopup(self.character, self.game_screen).open()

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

class FinalDayReportPopup(Popup):
    def __init__(self, character, game_screen, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.game_screen = game_screen
        self.title = "Day End Report"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Consumption Report
        consumption_text = "=== Resource Consumption ===\n"
        total_members = len(self.character.camp_members) + 1
        food_consumed = total_members * 1
        water_consumed = total_members * 1
        
        self.character.resources['food'] = max(0, self.character.resources['food'] - food_consumed)
        self.character.resources['water'] = max(0, self.character.resources['water'] - water_consumed)
        
        consumption_text += f"\nFood consumed: {food_consumed}"
        consumption_text += f"\nWater consumed: {water_consumed}"
        consumption_text += f"\n\nRemaining Food: {self.character.resources['food']}"
        consumption_text += f"\nRemaining Water: {self.character.resources['water']}"
        
        layout.add_widget(Label(text=consumption_text))

        # Generate visitor
        self.visitor_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        self.visitor_type = random.choices(VISITOR_TYPES, weights=[v['join_chance'] for v in VISITOR_TYPES])[0]
        
        visitor_text = "\n=== Visitor Arrived ===\n"
        visitor_text += f"\n{self.visitor_name} - {self.visitor_type['type']}"
        visitor_text += f"\n{self.visitor_type['description']}"
        
        layout.add_widget(Label(text=visitor_text))
        
        # Visitor interaction buttons
        self.buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='40dp',
            spacing=10
        )
        
        # Recruit button
        self.recruit_btn = Button(
            text="Try to Recruit",
            size_hint_x=0.33
        )
        self.recruit_btn.bind(on_release=lambda x: self.try_recruit())
        self.buttons_layout.add_widget(self.recruit_btn)
        
        # Trade button - only show if shop counter is built
        if "Shop Counter" in self.character.base_upgrades:
            self.trade_btn = Button(
                text="Trade",
                size_hint_x=0.33
            )
            self.trade_btn.bind(on_release=lambda x: self.trade())
            self.buttons_layout.add_widget(self.trade_btn)
        
        continue_btn = Button(
            text="Continue",
            size_hint_x=0.33
        )
        continue_btn.bind(on_release=self.on_continue)
        self.buttons_layout.add_widget(continue_btn)
        
        layout.add_widget(self.buttons_layout)
        
        self.trade_attempts = 0
        self.trade_completed = False
        
        self.content = layout

    def try_recruit(self):
        # Calculate resource bonus (scales with total resources)
        resource_bonus = sum(self.character.resources.values()) * 0.01  # 1% per resource unit
        resource_bonus = min(resource_bonus, 0.3)  # Cap at 30% bonus
        
        # Calculate total join chance
        join_chance = (
            self.visitor_type['join_chance'] + 
            (self.character.charisma * 0.05) + 
            resource_bonus
        )
        
        if random.random() < join_chance:
            self.character.camp_members.append({
                'name': self.visitor_name,
                'type': self.visitor_type['type'],
                'mode': 'gather',
                'ap': self.visitor_type['ap']
            })
            
            if len(self.character.camp_members) == 1:
                self.character.objectives_completed['recruit_member'] = True
            
            if len(self.character.camp_members) >= 3:
                self.character.objectives_completed['three_members'] = True
            
            self.show_result(f"{self.visitor_name} has joined your camp!")
        else:
            self.show_result(f"{self.visitor_name} declined to join...")

        # Disable recruit button after attempt
        self.recruit_btn.disabled = True
        self.recruit_btn.text = "Already Attempted"

    def trade(self):
        if self.trade_completed:
            self.show_result("Trade already completed for today.")
            return
            
        self.trade_attempts += 1
        if self.trade_attempts > 3:
            self.show_result("The visitor seems annoyed and leaves...")
            if hasattr(self, 'trade_btn'):
                self.trade_btn.disabled = True
            return
            
        valid_trades = self.get_valid_trades()
        if not valid_trades:
            self.show_result("No valid trades available with your current resources.")
            return
        
        option = random.choice(valid_trades)
        self.show_trade_offer(*option)

    def get_valid_trades(self):
        valid_trades = [
            ("food", 2, "rope", 1),
            ("water", 2, "rope", 1),
            ("wood", 3, "rope", 1),
            ("rope", 1, "food", 3),
            ("rope", 1, "water", 3),
            ("rope", 1, "wood", 4),
            # New trade options
            ("food", 3, "water", 4),
            ("water", 3, "food", 4),
            ("wood", 4, "food", 3),
            ("wood", 4, "water", 3),
            ("rope", 2, "wood", 6),
            ("food", 4, "rope", 2)
        ]
        
        return [(give_resource, give_amount, get_resource, get_amount) 
                for give_resource, give_amount, get_resource, get_amount in valid_trades 
                if self.character.resources[give_resource] >= give_amount]

    def show_trade_offer(self, give_resource, give_amount, get_resource, get_amount):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"Trade Offer:\nGive {give_amount} {give_resource} for {get_amount} {get_resource}"
        ))
        
        buttons = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        
        accept_btn = Button(text="Accept")
        accept_btn.bind(on_release=lambda x: self.complete_trade(
            give_resource, give_amount, get_resource, get_amount, trade_popup
        ))
        
        decline_btn = Button(text="Decline")
        decline_btn.bind(on_release=lambda x: trade_popup.dismiss())
        
        buttons.add_widget(accept_btn)
        buttons.add_widget(decline_btn)
        content.add_widget(buttons)
        
        trade_popup = Popup(
            title="Trade Offer",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        trade_popup.open()

    def complete_trade(self, give_resource, give_amount, get_resource, get_amount, trade_popup):
        self.character.resources[give_resource] -= give_amount
        self.character.resources[get_resource] += get_amount
        self.trade_completed = True
        if hasattr(self, 'trade_btn'):
            self.trade_btn.disabled = True
        self.show_result("Trade completed successfully!")
        trade_popup.dismiss()

    def show_result(self, text):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=text))
        
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(close_btn)
        
        result_popup = Popup(
            title="Result",
            content=content,
            size_hint=(0.6, 0.4),
            auto_dismiss=False
        )
        
        close_btn.bind(on_release=result_popup.dismiss)
        result_popup.open()

    def on_continue(self, instance):
        self.character.current_day += 1
        self.character.current_ap = self.character.action_points
        
        # Save game at the start of each new day
        save_character(self.character)
        
        self.dismiss()
        Clock.schedule_once(lambda dt: self.game_screen.update_ui(), 0.1)

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

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
    def __init__(self, character, location_type, parent_popup, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.parent_popup = parent_popup
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
        if self.character.current_ap < 2:
            result = "Not enough Action Points! (Requires 2 AP)"
        else:
            self.character.current_ap -= 2
            result = self.determine_outcome(instance.location_type, instance.location)
            self.character.objectives_completed["go_adventure"] = True
            
            # Update both the game screen and adventure menu AP displays
            game_screen = App.get_running_app().root.get_screen('game_screen')
            game_screen.update_status()
            self.parent_popup.update_status()
        
        result_popup = AdventureResultPopup(text=result)
        result_popup.bind(on_dismiss=lambda x: self.parent_popup.update_status())
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

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

class AdventurePopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = "Choose Adventure Location"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Use current_ap instead of action_points
        self.status_label = Label(
            text=f"Action Points: {self.character.current_ap}\nAdventure will cost: 2 AP"
        )
        self.main_layout.add_widget(self.status_label)
        
        # Location type buttons
        city_btn = Button(
            text="City Adventures",
            size_hint_y=None,
            height='40dp'
        )
        city_btn.bind(on_release=lambda x: self.show_locations('city'))
        self.main_layout.add_widget(city_btn)
        
        woods_btn = Button(
            text="Woods Adventures",
            size_hint_y=None,
            height='40dp'
        )
        woods_btn.bind(on_release=lambda x: self.show_locations('woods'))
        self.main_layout.add_widget(woods_btn)
        
        # Close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        
        def force_close(instance):
            game_screen = App.get_running_app().root.get_screen('game_screen')
            self.dismiss()
            if self.parent:
                self.parent.remove_widget(self)
            # Only check AP if it's actually 0
            if self.character.current_ap <= 0:
                game_screen.check_ap_and_day()
                
        close_btn.bind(on_release=force_close)
        self.main_layout.add_widget(close_btn)
        
        self.content = self.main_layout

    def get_status_text(self):
        return f"Action Points: {self.character.current_ap}\nAdventure will cost: 2 AP"

    def update_status(self):
        self.status_label.text = self.get_status_text()

    def show_locations(self, location_type):
        location_popup = LocationSelectionPopup(self.character, location_type, self)
        location_popup.bind(on_dismiss=lambda x: self.update_status())
        location_popup.open()

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.character = None

    def set_character(self, character):
        self.character = character
        self.update_ui()

    def update_status(self):
        if self.character:
            self.update_ui()  # Just call update_ui instead

    def update_ui(self):
        if self.character:
            # Add debug print to verify values
            print(f"Updating UI - AP: {self.character.current_ap}/{self.character.action_points}")
            
            self.ids.counter_label.text = f"Day {self.character.current_day}\nAction Points: {self.character.current_ap}/{self.character.action_points}"
            self.ids.status_label.text = ""

    def check_ap_and_day(self):
        if self.character and self.character.current_ap <= 0:
            # Process member activities
            member_results = self.process_member_activities()
            # Start the sequence of popups with the results
            GuardReportPopup(self.character, member_results, self).open()

    def process_member_activities(self):
        results = {
            'gathered_resources': {'wood': 0, 'water': 0, 'food': 0},
            'adventures': []
        }
        
        for member in self.character.camp_members:
            if member['mode'] == 'gather':
                # Process gathering - use AP for multiple attempts
                for _ in range(member['ap']):
                    resource = random.choice(['wood', 'water', 'food'])
                    # Base 20% chance + type bonus for Survivors (30%)
                    success_chance = 0.2 + (0.1 if member['type'] == 'Survivor' else 0)
                    
                    if random.random() < success_chance:
                        amount = random.randint(1, 2)
                        results['gathered_resources'][resource] += amount
            
            elif member['mode'] == 'adventure':
                # Process adventures - one adventure per 2 AP
                adventures_possible = member['ap'] // 2
                for _ in range(adventures_possible):
                    location_type = random.choice(['city', 'woods'])
                    location = random.choice(list(ADVENTURE_SCENARIOS[location_type].keys()))
                    
                    # Base 25% chance + type bonus for Scouts (35%)
                    success_chance = 0.25 + (0.1 if member['type'] == 'Scout' else 0)
                    
                    if random.random() < success_chance:
                        outcome = 'good'
                    elif random.random() < 0.6:
                        outcome = 'neutral'
                    else:
                        outcome = 'bad'
                    
                    result = random.choice(ADVENTURE_SCENARIOS[location_type][location][outcome])
                    results['adventures'].append(f"{member['name']}: {result}")
        
        return results

    def check_resources(self):
        if not self.character:
            return
        
        manage_popup = ManageBasePopup(self.character)
        manage_popup.open()

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
        adventure_popup.bind(on_dismiss=lambda x: self.update_status())
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
        
        # Create buttons for different sections
        stats_btn = Button(
            text="Core & Derived Stats",
            size_hint_y=None,
            height='40dp'
        )
        stats_btn.bind(on_release=self.show_stats)
        layout.add_widget(stats_btn)
        
        resources_btn = Button(
            text="Resources & Upgrades",
            size_hint_y=None,
            height='40dp'
        )
        resources_btn.bind(on_release=self.show_resources)
        layout.add_widget(resources_btn)
        
        members_btn = Button(
            text="Camp Members",
            size_hint_y=None,
            height='40dp'
        )
        members_btn.bind(on_release=self.show_members)
        layout.add_widget(members_btn)
        
        # Close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        close_btn.bind(on_release=self.dismiss)
        layout.add_widget(close_btn)
        
        self.content = layout

    def show_stats(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        stats_text = (
            "=== Core Stats ===\n"
            f"Endurance (END): {self.character.endurance}\n"
            f"Scavenging (SCV): {self.character.scavenging}\n"
            f"Charisma (CHA): {self.character.charisma}\n"
            f"Combat (CMB): {self.character.combat}\n"
            f"Crafting (CRF): {self.character.crafting}\n\n"
            "=== Derived Stats ===\n"
            f"Action Points: {self.character.current_ap}/{self.character.action_points}\n"
            f"Trade Value Bonus: {self.character.trade_value_bonus:.1%}\n"
            f"Survival Chance: {self.character.survival_chance:.1%}\n"
            f"Resource Efficiency: {self.character.resource_efficiency:.1%}\n"
            f"\nCurrent Day: {self.character.current_day}"
        )
        
        content.add_widget(Label(text=stats_text))
        
        close_btn = Button(
            text="Back",
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title="Character Stats",
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_resources(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        resources_text = (
            "=== Resources ===\n"
            f"Wood: {self.character.resources['wood']}\n"
            f"Water: {self.character.resources['water']}\n"
            f"Food: {self.character.resources['food']}\n"
            f"Rope: {self.character.resources['rope']}\n\n"
            "=== Base Upgrades ===\n"
        )
        
        if self.character.base_upgrades:
            for upgrade in self.character.base_upgrades:
                resources_text += f"• {upgrade}\n"
        else:
            resources_text += "No upgrades built yet"
        
        content.add_widget(Label(text=resources_text))
        
        close_btn = Button(
            text="Back",
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title="Resources & Upgrades",
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_members(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        if not self.character.camp_members:
            members_text = "No camp members yet"
        else:
            members_text = "=== Camp Members ===\n\n"
            for member in self.character.camp_members:
                members_text += (f"Name: {member['name']}\n"
                               f"Type: {member['type']}\n"
                               f"Current Role: {member['mode'].title()}\n"
                               f"Action Points: {member['ap']}\n\n")
        
        content.add_widget(Label(text=members_text))
        
        close_btn = Button(
            text="Back",
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title="Camp Members",
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        layout.add_widget(Label(
            text='Credits for Zombie Vibe Builder v0.1',
            font_size='24sp',
            size_hint_y=None,
            height='50dp'
        ))
        
        # Credits text
        credits_text = (
            "-Ronovo for the vibes\n\n"
            "-Pretty for maintaining the vibes\n\n"
            "-Yessica for ethical advisory\n\n"
            "-Grandma WaveCoder for being a great hostage\n"
            "(For Legal Reasons, This Is A Joke)\n\n"
            "-WaveCoder for rolling with all the vibes\n"
            "of the night to make this work."
        )
        
        layout.add_widget(Label(
            text=credits_text,
            font_size='18sp'
        ))
        
        # Back button
        back_btn = Button(
            text='Back to Main Menu',
            size_hint_y=None,
            height='50dp'
        )
        
        def go_back(instance):
            self.manager.current = 'main_menu'
            
        back_btn.bind(on_release=go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

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
        "camp_members": character.camp_members,
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
        sm.add_widget(CreditsScreen(name='credits'))  # Add Credits screen
        return sm

if __name__ == '__main__':
    ZombieVibeApp().run()