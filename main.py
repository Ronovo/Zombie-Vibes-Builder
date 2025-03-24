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
from kivy.graphics import Color, Rectangle

# Set window size (default is usually 800x600, so 10% bigger would be 880x660)
Window.size = (880, 660)

@dataclass
class Treasure:
    name: str
    category: str
    value: int
    location_found: str
    description: str
    day_found: int  # To track when it was found

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

LOCATION_TREASURES = {
    "hospital": [
        Treasure("Sealed Antibiotics", "Medical", 500, "Hospital", "A rare find of untouched medicine", 0),
        # ... more treasures
    ],
    "mall": [
        Treasure("Working Laptop", "Electronics", 600, "Mall", "Still has some charge!", 0),
        # ... more treasures
    ],
    # ... more locations
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
            character.shop_inventory = data.get('shop_inventory', {"wood": 0, "water": 0, "food": 0, "rope": 0})
            
            # Load treasures
            character.treasures = [
                Treasure(
                    name=t['name'],
                    category=t['category'],
                    value=t['value'],
                    location_found=t['location_found'],
                    description=t['description'],
                    day_found=t['day_found']
                ) for t in data.get('treasures', [])
            ]
            
            character.shop_treasures = [
                Treasure(
                    name=t['name'],
                    category=t['category'],
                    value=t['value'],
                    location_found=t['location_found'],
                    description=t['description'],
                    day_found=t['day_found']
                ) for t in data.get('shop_treasures', [])
            ]
            
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
            camp_members=[],
            current_ap=CHARACTER_PRESETS[self.selected_preset].endurance * 2,
            current_day=1,
            objectives_completed={
                "gather_basics": False,
                "build_shop": False,
                "go_adventure": False,
                "recruit_member": False,
                "three_members": False
            },
            treasures=[],  # Initialize empty treasures list
            shop_treasures=[]  # Initialize empty shop treasures list
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
        # Create a single layout for victory content
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
        
        # Set popup properties with the single content layout
        self.content = content
        self.title = "Victory!"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False

    def show_objectives_list(self):
        # Create a single layout for objectives content
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
        
        # Set popup properties with the single content layout
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
        
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.refresh_content()
        self.content = self.main_layout

    def refresh_content(self):
        # Clear existing widgets
        self.main_layout.clear_widgets()
        
        # Display current resources
        self.resources_label = Label(
            text=f"Current Resources:\n" +
                 f"Wood: {self.character.resources['wood']}\n" +
                 f"Rope: {self.character.resources['rope']}"
        )
        self.main_layout.add_widget(self.resources_label)
        
        # Only show build options if shop counter isn't built
        if "Shop Counter" not in self.character.base_upgrades:
            shop_btn = Button(
                text="Build Shop Counter (Costs: 10 wood, 2 rope)",
                size_hint_y=None,
                height='40dp'
            )
            shop_btn.bind(on_release=self.build_shop_counter)
            self.main_layout.add_widget(shop_btn)
        else:
            self.main_layout.add_widget(Label(
                text="Future upgrades coming soon...",
                size_hint_y=None,
                height='40dp'
            ))
        
        # Close button with force close
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        
        def force_close(instance):
            self.dismiss()
            # Force removal from parent if dismiss doesn't work
            if self.parent:
                self.parent.remove_widget(self)
            # Update the game screen
            game_screen = App.get_running_app().root.get_screen('game_screen')
            game_screen.update_ui()
                
        close_btn.bind(on_release=force_close)
        self.main_layout.add_widget(close_btn)

    def build_shop_counter(self, instance):
        if "Shop Counter" in self.character.base_upgrades:
            self.show_result("You already have a Shop Counter!")
            return
            
        if self.character.resources["wood"] >= 10 and self.character.resources["rope"] >= 2:
            self.character.resources["wood"] -= 10
            self.character.resources["rope"] -= 2
            self.character.base_upgrades.append("Shop Counter")
            self.character.objectives_completed["build_shop"] = True
            
            # Refresh the content instead of reinitializing
            self.refresh_content()
            
            self.show_result("Shop Counter built successfully!")
        else:
            self.show_result("You need 10 wood and 2 rope to build this...")

    def show_result(self, text):
        # Create a single BoxLayout as the sole content widget
        content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10,
            size_hint_y=None,
            height='100dp'
        )
        
        # Add message label to the layout
        content.add_widget(Label(
            text=text,
            size_hint_y=None,
            height='40dp'
        ))
        
        # Add close button to the layout
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(close_btn)
        
        # Create popup with the BoxLayout as its only content
        popup = Popup(
            title="Result",
            content=content,  # Single content widget
            size_hint=(0.6, 0.4),
            auto_dismiss=False
        )
        
        # Bind close button
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

class ManageBasePopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = "Base Management"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Show shop management if counter is built
        if "Shop Counter" in self.character.base_upgrades:
            shop_btn = Button(
                text="Manage Shop Counter",
                size_hint_y=None,
                height='40dp'
            )
            shop_btn.bind(on_release=self.manage_shop)
            layout.add_widget(shop_btn)
        
        # Camp members management button
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
        close_btn.bind(on_release=self.dismiss)
        layout.add_widget(close_btn)
        
        self.content = layout

    def manage_shop(self, instance):
        ShopManagementPopup(self.character).open()

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
        print(f"Debug: Initializing GuardReportPopup with results: {member_results}")
        super().__init__(**kwargs)
        self.character = character
        self.member_results = member_results
        self.game_screen = game_screen
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
        self.trade_attempts = 0
        self.trade_completed = False
        
        # Store visitor info as instance variables
        self.visitor_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        self.visitor_type = random.choices(VISITOR_TYPES, weights=[v['join_chance'] for v in VISITOR_TYPES])[0]
        
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

        visitor_text = "\n=== Visitor Arrived ===\n"
        visitor_text += f"\n{self.visitor_name} - {self.visitor_type['type']}"
        visitor_text += f"\n{self.visitor_type['description']}"
        
        layout.add_widget(Label(text=visitor_text))
        
        # Visitor interaction buttons
        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='40dp',
            spacing=10
        )
        
        # Recruit button
        self.recruit_btn = Button(
            text="Try to Recruit",
            size_hint_x=0.33  # Adjusted for 3 buttons instead of 4
        )
        self.recruit_btn.bind(on_release=lambda x: self.try_recruit())
        buttons_layout.add_widget(self.recruit_btn)
        
        # Personal Trade button
        self.personal_trade_btn = Button(
            text="Personal Trade",
            size_hint_x=0.33
        )
        self.personal_trade_btn.bind(on_release=lambda x: self.personal_trade())
        buttons_layout.add_widget(self.personal_trade_btn)
        
        continue_btn = Button(
            text="Continue",
            size_hint_x=0.33
        )
        continue_btn.bind(on_release=self.on_continue)
        buttons_layout.add_widget(continue_btn)
        
        layout.add_widget(buttons_layout)
        self.content = layout

    def personal_trade(self):
        if self.trade_completed:
            self.show_result("Already completed a trade today.")
            return
            
        self.trade_attempts += 1
        if self.trade_attempts > 3:
            self.show_result("The visitor seems annoyed and leaves...")
            self.personal_trade_btn.disabled = True
            return
            
        # Original trade options (from personal inventory)
        trade_options = [
            ("food", 2, "rope", 1),
            ("water", 2, "rope", 1),
            ("wood", 3, "rope", 1),
            ("rope", 1, "food", 3),
            ("rope", 1, "water", 3),
            ("rope", 1, "wood", 4),
            ("food", 3, "water", 4),
            ("water", 3, "food", 4),
            ("wood", 4, "food", 3),
            ("wood", 4, "water", 3),
            ("rope", 2, "wood", 6),
            ("food", 4, "rope", 2)
        ]
        
        valid_trades = [(give_resource, give_amount, get_resource, get_amount) 
                       for give_resource, give_amount, get_resource, get_amount in trade_options 
                       if self.character.resources[give_resource] >= give_amount]
        
        if not valid_trades:
            self.show_result("No valid trades available with your current resources.")
            return
        
        option = random.choice(valid_trades)
        self.show_trade_offer(*option, is_shop_trade=False)

    def show_trade_offer(self, give_resource, give_amount, get_resource, get_amount, is_shop_trade=False):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        source = "shop" if is_shop_trade else "inventory"
        content.add_widget(Label(
            text=f"Trade Offer (from {source}):\nGive {give_amount} {give_resource} for {get_amount} {get_resource}"
        ))
        
        buttons = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        
        accept_btn = Button(text="Accept")
        accept_btn.bind(on_release=lambda x: self.complete_trade(
            give_resource, give_amount, get_resource, get_amount, trade_popup, is_shop_trade
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

    def complete_trade(self, give_resource, give_amount, get_resource, get_amount, trade_popup, is_shop_trade=False):
        if is_shop_trade:
            self.character.shop_inventory[give_resource] -= give_amount
            self.character.resources[get_resource] += get_amount
        else:
            self.character.resources[give_resource] -= give_amount
            self.character.resources[get_resource] += get_amount
            
        self.trade_completed = True
        self.personal_trade_btn.disabled = True
        
        self.show_result("Trade completed successfully!")
        trade_popup.dismiss()

    def on_continue(self, instance):
        self.character.current_day += 1
        self.character.current_ap = self.character.action_points
        
        # Save game at the start of each new day
        save_character(self.character)
        
        self.dismiss()
        Clock.schedule_once(lambda dt: self.game_screen.update_ui(), 0.1)

    def show_result(self, text):
        # Create a single BoxLayout to hold all content
        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add the message label
        message_label = Label(text=text)
        content_layout.add_widget(message_label)
        
        # Add the close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        content_layout.add_widget(close_btn)
        
        # Create the popup with the layout as its single content widget
        result_popup = Popup(
            title="Result",
            content=content_layout,  # Use the layout as the single content widget
            size_hint=(0.6, 0.4),
            auto_dismiss=False
        )
        
        # Bind the close button
        close_btn.bind(on_release=result_popup.dismiss)
        
        # Open the popup
        result_popup.open()

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()  # Update main screen UI when closing
        super().dismiss(*args)

    def try_recruit(self):  # Remove parameters since we're using instance variables
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

class AdventureResultPopup(Popup):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.title = "Adventure Result"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        # Create a single layout for all content
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add the result text
        layout.add_widget(Label(text=text))
        
        # Add close button
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
        
        # Set the layout as the single content widget
        self.content = layout

class LocationSelectionPopup(Popup):
    def __init__(self, character, location_type, parent_popup, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.parent_popup = parent_popup
        self.title = f"Select {location_type} Location"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        # Create a single main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Store AP label as instance variable
        self.ap_label = Label(
            text=self.get_ap_text(),
            size_hint_y=None,
            height='40dp'
        )
        self.main_layout.add_widget(self.ap_label)
        
        # Add location buttons
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
            self.main_layout.add_widget(btn)
        
        # Add close button
        close_btn = Button(
            text="Back",
            size_hint_y=None,
            height='40dp'
        )
        close_btn.bind(on_release=self.dismiss)
        self.main_layout.add_widget(close_btn)
        
        # Set the main layout as the single content widget
        self.content = self.main_layout

    def get_ap_text(self):
        return f"Action Points: {self.character.current_ap}\nAdventure will cost: 2 AP"

    def update_ap_display(self):
        self.ap_label.text = self.get_ap_text()

    def start_adventure(self, instance):
        if self.character.current_ap < 2:
            result = "Not enough Action Points! (Requires 2 AP)"
        else:
            self.character.current_ap -= 2
            result = self.determine_outcome(instance.location_type, instance.location)
            self.character.objectives_completed["go_adventure"] = True
            
            # Update displays
            self.update_ap_display()
            if self.parent_popup:
                self.parent_popup.update_status()
            
            # Update game screen and check for random trader
            game_screen = App.get_running_app().root.get_screen('game_screen')
            game_screen.update_ui()
            game_screen.check_random_trader()
        
        result_popup = AdventureResultPopup(text=result)
        result_popup.bind(on_dismiss=self.on_result_dismiss)
        result_popup.open()

    def on_result_dismiss(self, instance):
        """Handle result popup dismissal without recursion"""
        if self.character.current_ap <= 0:
            # Dismiss this popup first
            self.dismiss()
            # Then the parent popup if it exists
            if self.parent_popup:
                self.parent_popup.dismiss()
            # Finally, trigger the day end sequence directly
            Clock.schedule_once(lambda dt: App.get_running_app().root.get_screen('game_screen').check_ap_and_day(), 0.1)

    def check_ap(self):
        if self.character.current_ap <= 0:
            self.dismiss()
            self.parent_popup.dismiss()
            game_screen = App.get_running_app().root.get_screen('game_screen')
            game_screen.check_ap_and_day()

    def determine_outcome(self, location_type, location):
        base_chance = random.random()
        
        # Calculate skill bonus based on location type
        if location_type == 'city':
            skill_bonus = (self.character.scavenging * 0.02) + (self.character.charisma * 0.01)
        else:  # woods
            skill_bonus = (self.character.endurance * 0.02) + (self.character.combat * 0.01)
        
        # Exceptional roll (increased to 20% for testing)
        exceptional_chance = 0.20 + (self.character.scavenging * 0.01)
        if base_chance < exceptional_chance:
            # Found a treasure!
            if location_type == 'city':
                if location == 'Hospital':
                    treasure = Treasure(
                        "Sealed Antibiotics", "Medical", 500,
                        "Hospital", "A rare find of untouched medicine",
                        self.character.current_day
                    )
                elif location == 'Abandoned Mall':
                    treasure = Treasure(
                        "Working Laptop", "Electronics", 600,
                        "Mall", "Still has some charge!",
                        self.character.current_day
                    )
                else:  # Residential District
                    treasure = Treasure(
                        "Fine Jewelry", "Luxury", 400,
                        "House", "Someone's precious memories...",
                        self.character.current_day
                    )
            else:  # woods locations
                if location == 'Ranger Station':
                    treasure = Treasure(
                        "Military GPS", "Electronics", 450,
                        "Ranger Station", "Still works perfectly!",
                        self.character.current_day
                    )
                elif location == 'River Expedition':
                    treasure = Treasure(
                        "Gold Nuggets", "Valuables", 700,
                        "River", "Nature's treasure!",
                        self.character.current_day
                    )
                else:  # Abandoned Campgrounds
                    treasure = Treasure(
                        "Vintage Camping Gear", "Equipment", 350,
                        "Campgrounds", "They don't make them like this anymore",
                        self.character.current_day
                    )
            
            if not hasattr(self.character, 'treasures'):
                self.character.treasures = []
            self.character.treasures.append(treasure)
            return f"EXCEPTIONAL FIND! You discovered {treasure.name}! ({treasure.description})"

        # Regular outcome rolls
        final_chance = base_chance + skill_bonus
        if final_chance > 0.8:  # Good outcome (20%)
            outcome = random.choice([
                self.generate_resource_find('good'),
                self.generate_friendly_encounter(),
                self.generate_resource_find('good')  # Higher chance for resources
            ])
        elif final_chance > 0.3:  # Neutral outcome (50%)
            outcome = random.choice([
                self.generate_resource_find('neutral'),
                "You find nothing of value, but stay safe.",
                "The area is quiet, allowing for a thorough search."
            ])
        else:  # Bad outcome (30%)
            outcome = random.choice([
                self.generate_zombie_encounter(),
                self.generate_bandit_encounter(),
                self.generate_accident()
            ])
        
        return outcome

    def generate_resource_find(self, quality):
        resource = random.choice(['wood', 'water', 'food', 'rope'])
        if quality == 'good':
            amount = random.randint(3, 5)
        else:  # neutral
            amount = random.randint(1, 2)
        
        self.character.resources[resource] += amount
        return f"You found {amount} {resource}!"

    def generate_friendly_encounter(self):
        visitor_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        visitor_type = random.choices(VISITOR_TYPES, weights=[v['join_chance'] for v in VISITOR_TYPES])[0]
        
        # Store visitor info for potential recruitment
        self.current_visitor = {
            'name': visitor_name,
            'type': visitor_type['type'],
            'description': visitor_type['description'],
            'ap': visitor_type['ap']
        }
        
        # Schedule the visitor interaction popup
        Clock.schedule_once(lambda dt: self.show_visitor_popup(), 0.1)
        
        return f"You meet {visitor_name}, a {visitor_type['type']}..."

    def generate_zombie_encounter(self):
        # Lose some resources running away
        resource = random.choice(['food', 'water', 'wood', 'rope'])
        amount = random.randint(1, 2)
        if self.character.resources[resource] >= amount:
            self.character.resources[resource] -= amount
            return f"Zombies force you to drop {amount} {resource} while escaping!"
        else:
            self.character.current_ap = max(0, self.character.current_ap - 1)
            return "Zombies appear! You escape, but lose 1 AP from exhaustion!"

    def generate_bandit_encounter(self):
        # Bandits steal resources
        resource = random.choice(['food', 'water', 'wood', 'rope'])
        amount = random.randint(2, 3)
        if self.character.resources[resource] >= amount:
            self.character.resources[resource] -= amount
            return f"Bandits rob you of {amount} {resource}!"
        else:
            self.character.resources[resource] = 0
            return f"Bandits take all your {resource}!"

    def generate_accident(self):
        # Random accident that costs AP
        self.character.current_ap = max(0, self.character.current_ap - 1)
        return random.choice([
            "You twist your ankle! (-1 AP)",
            "You get lost and waste time! (-1 AP)",
            "The weather turns bad! (-1 AP)"
        ])

    def show_visitor_popup(self):
        if not hasattr(self, 'current_visitor'):
            return
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"You've met {self.current_visitor['name']}\n"
                 f"Type: {self.current_visitor['type']}"
        ))
        
        buttons = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        
        recruit_btn = Button(text="Try to Recruit")
        recruit_btn.bind(on_release=lambda x: self.try_recruit_visitor(visitor_popup))
        
        trade_btn = Button(text="Trade")
        trade_btn.bind(on_release=lambda x: self.try_trade_visitor(visitor_popup))
        
        ignore_btn = Button(text="Ignore")
        ignore_btn.bind(on_release=lambda x: visitor_popup.dismiss())
        
        buttons.add_widget(recruit_btn)
        buttons.add_widget(trade_btn)
        buttons.add_widget(ignore_btn)
        content.add_widget(buttons)
        
        visitor_popup = Popup(
            title="New Encounter!",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        visitor_popup.open()

    def try_recruit_visitor(self, popup):
        if not hasattr(self, 'current_visitor'):
            return
        
        # Use same recruitment logic as before
        resource_bonus = sum(self.character.resources.values()) * 0.01
        resource_bonus = min(resource_bonus, 0.3)
        
        join_chance = 0.3 + (self.character.charisma * 0.05) + resource_bonus
        
        if random.random() < join_chance:
            self.character.camp_members.append({
                'name': self.current_visitor['name'],
                'type': self.current_visitor['type'],
                'mode': 'gather',  # Default mode
                'ap': self.current_visitor['ap']
            })
            result = f"{self.current_visitor['name']} has joined your camp!"
            
            if len(self.character.camp_members) == 1:
                self.character.objectives_completed['recruit_member'] = True
            if len(self.character.camp_members) >= 3:
                self.character.objectives_completed['three_members'] = True
        else:
            result = f"{self.current_visitor['name']} declined to join..."
        
        popup.dismiss()
        self.show_result(result)

    def try_trade_visitor(self, popup):
        if not hasattr(self, 'current_visitor'):
            return
            
        trade_options = [
            ("food", 2, "rope", 1),
            ("water", 2, "rope", 1),
            ("wood", 3, "rope", 1),
            ("rope", 1, "food", 3),
            ("rope", 1, "water", 3),
            ("rope", 1, "wood", 4)
        ]
        
        valid_trades = [(give_resource, give_amount, get_resource, get_amount) 
                        for give_resource, give_amount, get_resource, get_amount in trade_options 
                        if self.character.resources[give_resource] >= give_amount]
        
        if not valid_trades:
            popup.dismiss()
            self.show_result("You don't have enough resources to trade.")
            return
        
        option = random.choice(valid_trades)
        popup.dismiss()
        self.show_trade_offer(*option)

    def show_trade_offer(self, give_resource, give_amount, get_resource, get_amount):
        # Create a single main layout for all content
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add the trade offer text
        main_layout.add_widget(Label(
            text=f"{self.current_visitor['name']} wants to buy {give_amount} {give_resource} for {get_amount} {get_resource}"
        ))
        
        # Create a buttons layout
        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='40dp',
            spacing=10
        )
        
        # Create and add buttons
        accept_btn = Button(text="Accept")
        accept_btn.bind(on_release=lambda x: self.complete_random_trade(
            give_resource, give_amount, get_resource, get_amount, trade_popup
        ))
        
        bargain_btn = Button(text="Bargain")
        bargain_btn.bind(on_release=lambda x: self.attempt_bargain(
            give_resource, give_amount, get_resource, get_amount, trade_popup
        ))
        
        decline_btn = Button(text="Decline")
        decline_btn.bind(on_release=lambda x: trade_popup.dismiss())
        
        # Add buttons to the button layout
        buttons_layout.add_widget(accept_btn)
        buttons_layout.add_widget(bargain_btn)
        buttons_layout.add_widget(decline_btn)
        
        # Add the buttons layout to the main layout
        main_layout.add_widget(buttons_layout)
        
        # Create the popup with the main layout as its single content
        trade_popup = Popup(
            title="Trade Offer",
            content=main_layout,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        trade_popup.open()

    def attempt_bargain(self, sell_resource, sell_amount, pay_resource, pay_amount, popup):
        # Base 30% chance + 5% per charisma point
        success_chance = 0.3 + (self.character.charisma * 0.05)
        
        if random.random() < success_chance:
            # Increase offer by 20-40%
            increase = random.uniform(0.2, 0.4)
            new_amount = int(pay_amount * (1 + increase))
            self.show_result(
                f"{self.current_visitor['name']} agrees to increase their offer to {new_amount} {pay_resource}!"
            )
            # Show new trade offer
            self.show_trade_offer(self.current_visitor['name'], sell_resource, sell_amount, pay_resource, new_amount)
        else:
            self.show_result(f"{self.current_visitor['name']} becomes annoyed and leaves...")
        popup.dismiss()

    def complete_random_trade(self, sell_resource, sell_amount, pay_resource, pay_amount, popup):
        self.character.resources[sell_resource] -= sell_amount
        self.character.resources[pay_resource] += pay_amount
        popup.dismiss()
        self.show_result(f"Trade completed! Received {pay_amount} {pay_resource}")

    def show_result(self, text):
        # Create a single BoxLayout to hold all content
        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add the message label
        message_label = Label(text=text)
        content_layout.add_widget(message_label)
        
        # Add the close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        content_layout.add_widget(close_btn)
        
        # Create the popup with the layout as its single content widget
        result_popup = Popup(
            title="Result",
            content=content_layout,  # Use the layout as the single content widget
            size_hint=(0.6, 0.4),
            auto_dismiss=False
        )
        
        # Bind the close button
        close_btn.bind(on_release=result_popup.dismiss)
        
        # Open the popup
        result_popup.open()

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
            print(f"Debug: Triggering day end with AP: {self.character.current_ap}")
            # Schedule the day end sequence after a short delay to allow popups to close
            Clock.schedule_once(lambda dt: self.show_day_end_sequence(), 0.1)

    def show_day_end_sequence(self):
        """Show the day end sequence without recursion"""
        member_results = self.process_member_activities()
        print(f"Debug: Member results: {member_results}")
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
                self.check_ap_and_day(),
                self.check_random_trader()
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
                self.check_random_trader()
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

    def check_random_trader(self):
        if random.random() < 0.3:  # 30% chance for trader
            if random.random() < 0.4:  # 40% chance to sell treasure instead of buy
                self.show_treasure_sale_offer()
            else:
                # Existing shop trade logic
                if "Shop Counter" in self.character.base_upgrades:
                    if any(self.character.shop_inventory.values()):
                        self.show_random_trade_popup()
                    else:
                        self.show_result("Someone visited but there was nothing to trade...they have left.")

    def show_treasure_sale_offer(self):
        visitor_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        # Generate a random treasure
        treasure_types = [
            ("Ancient Coin Collection", "Collectible", random.randint(100, 300)),
            ("Medical Supplies", "Medical", random.randint(200, 400)),
            ("Preserved Food Cache", "Supplies", random.randint(150, 250)),
            ("Rare Book", "Collectible", random.randint(50, 150)),
            ("Tool Set", "Equipment", random.randint(100, 200))
        ]
        
        treasure_name, category, value = random.choice(treasure_types)
        asking_price = int(value * random.uniform(0.8, 1.2))  # Vary the asking price
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"{visitor_name} offers to sell you {treasure_name}\n"
                 f"Category: {category}\n"
                 f"Asking Price: {asking_price} credits"
        ))
        
        buttons = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        
        def buy_treasure(popup):
            if self.character.money >= asking_price:
                self.character.money -= asking_price
                new_treasure = Treasure(
                    treasure_name, category, value,
                    "Purchased", f"Bought from {visitor_name}",
                    self.character.current_day
                )
                self.character.treasures.append(new_treasure)
                self.show_result(f"You purchased {treasure_name}!")
            else:
                self.show_result("Not enough credits!")
            popup.dismiss()
        
        buy_btn = Button(text="Buy")
        buy_btn.bind(on_release=lambda x: buy_treasure(trade_popup))
        
        decline_btn = Button(text="Decline")
        decline_btn.bind(on_release=lambda x: trade_popup.dismiss())
        
        buttons.add_widget(buy_btn)
        buttons.add_widget(decline_btn)
        content.add_widget(buttons)
        
        trade_popup = Popup(
            title="Treasure For Sale",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        trade_popup.open()

    def show_random_trade_popup(self):
        visitor_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        # Generate trade offer
        valid_trades = self.get_valid_shop_trades()
        if not valid_trades:
            self.show_result("Someone visited but there was nothing to trade...they have left.")
            return
            
        trade_offer = random.choice(valid_trades)
        
        if trade_offer[0] == 'treasure':
            # Handle treasure trade
            _, treasure, pay_resource, initial_offer = trade_offer
            self.show_treasure_trade_offer(visitor_name, treasure, pay_resource, initial_offer)
        else:
            # Handle regular resource trade
            sell_resource, sell_amount, pay_resource, pay_amount = trade_offer
            self.show_regular_trade_offer(visitor_name, sell_resource, sell_amount, pay_resource, pay_amount)

    def show_treasure_trade_offer(self, visitor_name, treasure, pay_resource, initial_offer):
        self.current_bargain_attempts = 0
        self.max_bargain_attempts = 3
        self.current_treasure = treasure
        self.current_pay_resource = pay_resource
        self.initial_offer = initial_offer
        self.current_offer = initial_offer
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Visitor's interest text
        interest_text = (
            f"{visitor_name} is interested in your {treasure.name}!\n"
            f"Value: {treasure.value} credits\n"
            f"They offer {initial_offer} {pay_resource} (worth {initial_offer * self.character.resource_values[pay_resource]} credits)"
        )
        content.add_widget(Label(text=interest_text))
        
        # Payment options
        payment_layout = BoxLayout(orientation='vertical', spacing=5)
        
        # Option 1: Full resource payment
        option1_btn = Button(
            text=f"Accept {initial_offer} {pay_resource}",
            size_hint_y=None,
            height='40dp'
        )
        option1_btn.bind(on_release=lambda x: self.complete_treasure_trade(
            [(pay_resource, initial_offer, initial_offer * self.character.resource_values[pay_resource])],
            0, trade_popup
        ))
        payment_layout.add_widget(option1_btn)
        
        # Option 2: Full credits payment
        option2_btn = Button(
            text=f"Accept {treasure.value} credits",
            size_hint_y=None,
            height='40dp'
        )
        option2_btn.bind(on_release=lambda x: self.complete_treasure_trade(
            [], treasure.value, trade_popup
        ))
        payment_layout.add_widget(option2_btn)
        
        # Option 3: Mixed payment (half resources, half credits)
        half_resource_amount = initial_offer // 2
        half_credit_amount = treasure.value // 2
        if half_resource_amount > 0:
            option3_btn = Button(
                text=f"Accept {half_resource_amount} {pay_resource} + {half_credit_amount} credits",
                size_hint_y=None,
                height='40dp'
            )
            option3_btn.bind(on_release=lambda x: self.complete_treasure_trade(
                [(pay_resource, half_resource_amount, half_resource_amount * self.character.resource_values[pay_resource])],
                half_credit_amount, trade_popup
            ))
            payment_layout.add_widget(option3_btn)
        
        content.add_widget(payment_layout)
        
        # Bargaining button
        bargain_btn = Button(
            text=f"Bargain ({self.max_bargain_attempts} attempts left)",
            size_hint_y=None,
            height='40dp'
        )
        bargain_btn.bind(on_release=lambda x: self.attempt_treasure_bargain(
            bargain_btn, payment_layout, trade_popup
        ))
        content.add_widget(bargain_btn)
        
        # Decline button
        decline_btn = Button(
            text="Decline",
            size_hint_y=None,
            height='40dp'
        )
        decline_btn.bind(on_release=lambda x: trade_popup.dismiss())
        content.add_widget(decline_btn)
        
        trade_popup = Popup(
            title="Treasure Trade Offer",
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        trade_popup.open()

    def attempt_treasure_bargain(self, bargain_btn, payment_layout, popup):
        self.current_bargain_attempts += 1
        
        # Calculate bargaining success chance based on charisma
        success_chance = 0.3 + (self.character.charisma * 0.05)  # 30% base + 5% per charisma
        
        if random.random() < success_chance:
            # Successful bargain increases offer by 10-20%
            increase = random.uniform(0.1, 0.2)
            self.current_offer = int(self.current_offer * (1 + increase))
            
            # Update payment options
            payment_layout.clear_widgets()
            
            # Option 1: Full resource payment
            option1_btn = Button(
                text=f"Accept {self.current_offer} {self.current_pay_resource}",
                size_hint_y=None,
                height='40dp'
            )
            option1_btn.bind(on_release=lambda x: self.complete_treasure_trade(
                [(self.current_pay_resource, self.current_offer, self.current_offer * self.character.resource_values[self.current_pay_resource])],
                0, popup
            ))
            payment_layout.add_widget(option1_btn)
            
            # Option 2: Full credits payment
            option2_btn = Button(
                text=f"Accept {self.current_treasure.value} credits",
                size_hint_y=None,
                height='40dp'
            )
            option2_btn.bind(on_release=lambda x: self.complete_treasure_trade(
                [], self.current_treasure.value, popup
            ))
            payment_layout.add_widget(option2_btn)
            
            # Option 3: Mixed payment
            half_resource_amount = self.current_offer // 2
            half_credit_amount = self.current_treasure.value // 2
            if half_resource_amount > 0:
                option3_btn = Button(
                    text=f"Accept {half_resource_amount} {self.current_pay_resource} + {half_credit_amount} credits",
                    size_hint_y=None,
                    height='40dp'
                )
                option3_btn.bind(on_release=lambda x: self.complete_treasure_trade(
                    [(self.current_pay_resource, half_resource_amount, half_resource_amount * self.character.resource_values[self.current_pay_resource])],
                    half_credit_amount, popup
                ))
                payment_layout.add_widget(option3_btn)
            
            self.show_result("They agree to increase their offer!")
        else:
            self.show_result("They refuse to increase their offer...")
        
        # Update or disable bargain button
        remaining_attempts = self.max_bargain_attempts - self.current_bargain_attempts
        if remaining_attempts > 0:
            bargain_btn.text = f"Bargain ({remaining_attempts} attempts left)"
        else:
            bargain_btn.disabled = True
            bargain_btn.text = "No more bargaining"
            
        # Chance for trader to leave if pushed too hard
        if self.current_bargain_attempts >= 2 and random.random() < 0.3:
            self.show_result("The trader becomes annoyed and leaves...")
            popup.dismiss()

    def complete_treasure_trade(self, resource_payments, credit_payment, popup):
        # Check if player has enough credits
        if credit_payment > self.character.money:
            self.show_result("Not enough credits!")
            return
            
        # Check if player has enough resources
        for resource, amount, _ in resource_payments:
            if self.character.resources[resource] < amount:
                self.show_result(f"Not enough {resource}!")
                return
        
        # Remove treasure from shop
        self.character.shop_treasures.remove(self.current_treasure)
        
        # Process resource payments
        for resource, amount, _ in resource_payments:
            self.character.resources[resource] += amount
            
        # Process credit payment
        self.character.money -= credit_payment
        
        popup.dismiss()
        result_text = f"Trade completed! Sold {self.current_treasure.name} for:\n"
        for resource, amount, _ in resource_payments:
            result_text += f"• {amount} {resource}\n"
        if credit_payment > 0:
            result_text += f"• {credit_payment} credits"
        self.show_result(result_text)

    def show_regular_trade_offer(self, visitor_name, sell_resource, sell_amount, pay_resource, pay_amount):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Calculate total value of the trade
        total_value = sell_amount * self.character.resource_values[sell_resource]
        
        content.add_widget(Label(
            text=f"{visitor_name} wants to buy {sell_amount} {sell_resource}\n"
                 f"Total value: {total_value} credits\n"
                 f"They offer: {pay_amount} {pay_resource} (worth {pay_amount * self.character.resource_values[pay_resource]} credits)"
        ))
        
        # Add payment options
        payment_layout = BoxLayout(orientation='vertical', spacing=5)
        
        # Option 1: Full resource payment
        option1_btn = Button(
            text=f"Accept {pay_amount} {pay_resource}",
            size_hint_y=None,
            height='40dp'
        )
        option1_btn.bind(on_release=lambda x: self.complete_mixed_trade(
            sell_resource, sell_amount,
            [(pay_resource, pay_amount, pay_amount * self.character.resource_values[pay_resource])],
            0, trade_popup
        ))
        payment_layout.add_widget(option1_btn)
        
        # Option 2: Full credits payment
        option2_btn = Button(
            text=f"Accept {total_value} credits",
            size_hint_y=None,
            height='40dp'
        )
        option2_btn.bind(on_release=lambda x: self.complete_mixed_trade(
            sell_resource, sell_amount, [], total_value, trade_popup
        ))
        payment_layout.add_widget(option2_btn)
        
        # Option 3: Mixed payment (half resources, half credits)
        half_resource_amount = pay_amount // 2
        half_credit_amount = total_value // 2
        if half_resource_amount > 0:
            option3_btn = Button(
                text=f"Accept {half_resource_amount} {pay_resource} + {half_credit_amount} credits",
                size_hint_y=None,
                height='40dp'
            )
            option3_btn.bind(on_release=lambda x: self.complete_mixed_trade(
                sell_resource, sell_amount,
                [(pay_resource, half_resource_amount, half_resource_amount * self.character.resource_values[pay_resource])],
                half_credit_amount, trade_popup
            ))
            payment_layout.add_widget(option3_btn)
        
        content.add_widget(payment_layout)
        
        # Decline button
        decline_btn = Button(
            text="Decline",
            size_hint_y=None,
            height='40dp'
        )
        decline_btn.bind(on_release=lambda x: trade_popup.dismiss())
        content.add_widget(decline_btn)
        
        trade_popup = Popup(
            title="Shop Visitor",
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        trade_popup.open()

    def complete_mixed_trade(self, sell_resource, sell_amount, resource_payments, credit_payment, popup):
        # Check if player has enough credits
        if credit_payment > self.character.money:
            self.show_result("Not enough credits!")
            return
            
        # Check if player has enough resources
        for resource, amount, _ in resource_payments:
            if self.character.resources[resource] < amount:
                self.show_result(f"Not enough {resource}!")
                return
        
        # Complete the trade
        self.character.shop_inventory[sell_resource] -= sell_amount
        
        # Process resource payments
        for resource, amount, _ in resource_payments:
            self.character.resources[resource] += amount
            
        # Process credit payment
        self.character.money -= credit_payment
        
        popup.dismiss()
        result_text = f"Trade completed! Sold {sell_amount} {sell_resource} for:\n"
        for resource, amount, _ in resource_payments:
            result_text += f"• {amount} {resource}\n"
        if credit_payment > 0:
            result_text += f"• {credit_payment} credits"
        self.show_result(result_text)

    def get_valid_shop_trades(self):
        valid_trades = []
        for sell_resource, amount in self.character.shop_inventory.items():
            if amount > 0:
                for pay_resource, rate in self.character.shop_prices[sell_resource].items():
                    sell_amount = min(random.randint(1, 3), amount)
                    pay_amount = int(sell_amount * rate * random.uniform(1.0, 1.5))
                    valid_trades.append((sell_resource, sell_amount, pay_resource, pay_amount))
        return valid_trades

    def show_result(self, text):
        # Create a single BoxLayout to hold all content
        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add the message label
        message_label = Label(text=text)
        content_layout.add_widget(message_label)
        
        # Add the close button
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height='40dp'
        )
        content_layout.add_widget(close_btn)
        
        # Create the popup with the layout as its single content widget
        result_popup = Popup(
            title="Result",
            content=content_layout,  # Use the layout as the single content widget
            size_hint=(0.6, 0.4),
            auto_dismiss=False
        )
        
        # Bind the close button
        close_btn.bind(on_release=result_popup.dismiss)
        
        # Open the popup
        result_popup.open()

    def close_all_popups(self):
        # Add this method to the GameScreen class
        for widget in Window.children[:]:
            if isinstance(widget, Popup):
                widget.dismiss()

class CharacterStatusPopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = f"Character Status - {character.name}"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        # Create a single main layout
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
        
        # Set the main layout as the single content widget
        self.content = layout

    def show_stats(self, instance):
        # Create a single layout for stats content
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Find character's class by comparing stats with presets
        character_class = "Unknown"
        for preset_name, preset in CHARACTER_PRESETS.items():
            if (preset.endurance == self.character.endurance and
                preset.scavenging == self.character.scavenging and
                preset.charisma == self.character.charisma and
                preset.combat == self.character.combat and
                preset.crafting == self.character.crafting):
                character_class = preset_name
                break
        
        stats_text = (
            f"Character Class: {character_class}\n\n"
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
        
        # Create popup with the single content layout
        popup = Popup(
            title="Character Stats",
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_resources(self, instance):
        # Create a single layout for resources content
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
            resources_text += "No upgrades built yet\n"
        
        # Add treasures section
        if hasattr(self.character, 'treasures') and self.character.treasures:
            resources_text += "\n=== Personal Treasures ===\n"
            for treasure in self.character.treasures:
                resources_text += (f"• {treasure.name}\n"
                                 f"  Value: {treasure.value}\n"
                                 f"  Found: {treasure.location_found} (Day {treasure.day_found})\n"
                                 f"  {treasure.description}\n")
        
        if hasattr(self.character, 'shop_treasures') and self.character.shop_treasures:
            resources_text += "\n=== Shop Display Treasures ===\n"
            for treasure in self.character.shop_treasures:
                resources_text += (f"• {treasure.name}\n"
                                 f"  Value: {treasure.value}\n"
                                 f"  Found: {treasure.location_found} (Day {treasure.day_found})\n"
                                 f"  {treasure.description}\n")
        
        content.add_widget(Label(text=resources_text))
        
        close_btn = Button(
            text="Back",
            size_hint_y=None,
            height='40dp'
        )
        content.add_widget(close_btn)
        
        # Create popup with the single content layout
        popup = Popup(
            title="Resources & Upgrades",
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_members(self, instance):
        # Create a single layout for members content
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
        
        # Create popup with the single content layout
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

class ShopManagementPopup(Popup):
    def __init__(self, character, **kwargs):
        super().__init__(**kwargs)
        self.character = character
        self.title = "Shop Management"
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = False
        self.setup_content()

    def setup_content(self):
        # Create a single main layout for the entire popup
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Create ScrollView for the content
        scroll_view = ScrollView()
        content_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Store these as instance variables so refresh_display can access them
        self.content_layout = content_layout
        self.main_layout = main_layout
        
        # Personal Storage Section
        personal_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
        personal_layout.add_widget(Label(text='Personal Storage', size_hint_y=None, height=30))
        self.personal_display = Label(size_hint_y=None, height=170)
        personal_layout.add_widget(self.personal_display)
        content_layout.add_widget(personal_layout)

        # Shop Counter Section
        shop_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
        shop_layout.add_widget(Label(text='Shop Counter', size_hint_y=None, height=30))
        self.shop_display = Label(size_hint_y=None, height=170)
        shop_layout.add_widget(self.shop_display)
        content_layout.add_widget(shop_layout)

        # Resource Management Section
        manage_layout = GridLayout(cols=4, spacing=5, size_hint_y=None)
        manage_layout.bind(minimum_height=manage_layout.setter('height'))
        self.manage_layout = manage_layout
        content_layout.add_widget(manage_layout)

        # Treasure Management Section
        treasure_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        treasure_layout.bind(minimum_height=treasure_layout.setter('height'))
        
        treasure_header = Label(
            text='Treasure Management',
            size_hint_y=None,
            height=30,
            bold=True
        )
        treasure_layout.add_widget(treasure_header)
        
        self.treasure_display = Label(size_hint_y=None)
        self.treasure_display.bind(texture_size=lambda *x: setattr(self.treasure_display, 'height', self.treasure_display.texture_size[1]))
        treasure_layout.add_widget(self.treasure_display)
        
        content_layout.add_widget(treasure_layout)
        self.treasure_layout = treasure_layout

        # Add close button
        close_button = Button(
            text='Close',
            size_hint_y=None,
            height=50
        )
        close_button.bind(on_release=self.dismiss)

        # Add ScrollView and close button to main layout
        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        main_layout.add_widget(close_button)

        # Set the popup content
        self.content = main_layout
        
        # Initial display refresh
        self.refresh_display()

    def refresh_display(self):
        # Clear the management layout
        self.manage_layout.clear_widgets()
        
        # Update personal storage display
        personal_text = "Personal Storage:\n"
        for resource, amount in self.character.resources.items():
            personal_text += f"{resource.title()}: {amount}\n"
        self.personal_display.text = personal_text

        # Update shop counter display
        shop_text = "Shop Counter:\n"
        for resource, amount in self.character.shop_inventory.items():
            shop_text += f"{resource.title()}: {amount}\n"
        self.shop_display.text = shop_text

        # Rebuild resource management buttons
        for resource in self.character.resources.keys():
            # Resource label
            self.manage_layout.add_widget(Label(
                text=resource.title(),
                size_hint_y=None,
                height=40
            ))
            
            # Remove from shop button (now first)
            remove_btn = Button(
                text="-",
                size_hint_y=None,
                height=40,
                background_color=(1, 0, 0, 1)  # Red
            )
            remove_btn.resource = resource
            remove_btn.bind(on_release=self.remove_from_shop)
            self.manage_layout.add_widget(remove_btn)
            
            # Add to shop button (now second)
            add_btn = Button(
                text="+",
                size_hint_y=None,
                height=40,
                background_color=(0, 1, 0, 1)  # Green
            )
            add_btn.resource = resource
            add_btn.bind(on_release=self.add_to_shop)
            self.manage_layout.add_widget(add_btn)
            
            # Amount in shop label
            self.manage_layout.add_widget(Label(
                text=str(self.character.shop_inventory[resource]),
                size_hint_y=None,
                height=40
            ))

        # Check if there are any treasures to manage
        has_personal_treasures = hasattr(self.character, 'treasures') and len(self.character.treasures) > 0
        has_shop_treasures = hasattr(self.character, 'shop_treasures') and len(self.character.shop_treasures) > 0
        
        # Only show treasure section if there are treasures to manage
        if has_personal_treasures or has_shop_treasures:
            # Show treasure section header
            self.treasure_layout.opacity = 1
            self.treasure_layout.height = None  # Reset height to show content
            
            # Add treasure management buttons
            if has_personal_treasures:
                for treasure in self.character.treasures:
                    add_btn = Button(
                        text=f"Add {treasure.name} to Shop",
                        size_hint_y=None,
                        height=40,
                        background_color=(0, 0, 1, 1)  # Blue
                    )
                    add_btn.treasure = treasure
                    add_btn.bind(on_release=self.add_treasure_to_shop)
                    self.manage_layout.add_widget(add_btn)

            if has_shop_treasures:
                for treasure in self.character.shop_treasures:
                    remove_btn = Button(
                        text=f"Return {treasure.name} to Inventory",
                        size_hint_y=None,
                        height=40,
                        background_color=(1, 0.5, 0, 1)  # Orange
                    )
                    remove_btn.treasure = treasure
                    remove_btn.bind(on_release=self.remove_treasure_from_shop)
                    self.manage_layout.add_widget(remove_btn)
        else:
            # Hide treasure section completely
            self.treasure_layout.opacity = 0
            self.treasure_layout.height = 0

    def add_to_shop(self, instance):
        resource = instance.resource
        if self.character.resources[resource] > 0:
            self.character.resources[resource] -= 1
            self.character.shop_inventory[resource] += 1
            self.refresh_display()

    def remove_from_shop(self, instance):
        resource = instance.resource
        if self.character.shop_inventory[resource] > 0:
            self.character.shop_inventory[resource] -= 1
            self.character.resources[resource] += 1
            self.refresh_display()

    def add_treasure_to_shop(self, instance):
        treasure = instance.treasure
        if treasure in self.character.treasures:
            self.character.treasures.remove(treasure)
            if not hasattr(self.character, 'shop_treasures'):
                self.character.shop_treasures = []
            self.character.shop_treasures.append(treasure)
            self.refresh_display()

    def remove_treasure_from_shop(self, instance):
        treasure = instance.treasure
        if treasure in self.character.shop_treasures:
            self.character.shop_treasures.remove(treasure)
            if not hasattr(self.character, 'treasures'):
                self.character.treasures = []
            self.character.treasures.append(treasure)
            self.refresh_display()

    def dismiss(self, *args):
        game_screen = App.get_running_app().root.get_screen('game_screen')
        game_screen.update_ui()
        super().dismiss(*args)

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
        "objectives_completed": character.objectives_completed,
        "shop_inventory": character.shop_inventory,
        "treasures": [
            {
                "name": t.name,
                "category": t.category,
                "value": t.value,
                "location_found": t.location_found,
                "description": t.description,
                "day_found": t.day_found
            } for t in (character.treasures if hasattr(character, 'treasures') else [])
        ],
        "shop_treasures": [
            {
                "name": t.name,
                "category": t.category,
                "value": t.value,
                "location_found": t.location_found,
                "description": t.description,
                "day_found": t.day_found
            } for t in (character.shop_treasures if hasattr(character, 'shop_treasures') else [])
        ]
    }
    
    file_path = f"Characters/{character.name}.json"
    with open(file_path, 'w') as f:
        json.dump(character_data, f, indent=4)
    return True

def check_random_trade(character):
    if "Shop Counter" in character.base_upgrades and any(character.shop_inventory.values()):
        if random.random() < 0.3:  # 30% chance for trade opportunity
            return generate_trade_offer(character)
    return None

def generate_trade_offer(character):
    # Only consider resources that are in the shop
    available_resources = [r for r, amt in character.shop_inventory.items() if amt > 0]
    if not available_resources:
        return None
        
    selling_resource = random.choice(available_resources)
    selling_amount = min(random.randint(1, 3), character.shop_inventory[selling_resource])
    
    # Calculate payment options based on shop_prices
    payment_options = character.shop_prices[selling_resource]
    payment_resource = random.choice(list(payment_options.keys()))
    payment_amount = int(selling_amount * rate * random.uniform(1.0, 1.5))
    
    return {
        'sell': (selling_resource, selling_amount),
        'payment': (payment_resource, payment_amount)
    }

def sell_treasure(self, treasure):
    self.character.money += treasure.value
    self.character.treasures.remove(treasure)

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