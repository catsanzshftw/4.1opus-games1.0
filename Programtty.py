import pygame
import math
import random
import json
from enum import Enum, auto
from typing import List, Dict, Tuple, Optional

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)

# Game States
class GameState(Enum):
    INTRO = auto()
    OVERWORLD = auto()
    BATTLE = auto()
    DIALOGUE = auto()
    MENU = auto()
    CHAPTER_COMPLETE = auto()
    GAME_OVER = auto()
    VICTORY = auto()

# Battle Actions
class BattleAction(Enum):
    JUMP = auto()
    HAMMER = auto()
    ITEM = auto()
    RUN = auto()
    SPECIAL = auto()
    PARTNER = auto()

class Partner:
    """Partner character class"""
    def __init__(self, name, color, hp, ability):
        self.name = name
        self.color = color
        self.max_hp = hp
        self.hp = hp
        self.ability = ability
        self.level = 1
        
    def use_ability(self, target):
        """Use partner's special ability"""
        damage = 3 + self.level
        return damage

class Enemy:
    """Enemy class"""
    def __init__(self, name, hp, attack, defense, color, exp_reward):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.color = color
        self.exp_reward = exp_reward
        self.x = 0
        self.y = 0
        self.animation_timer = 0
        
    def take_damage(self, damage):
        """Enemy takes damage"""
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage
        
    def is_defeated(self):
        """Check if enemy is defeated"""
        return self.hp <= 0

class Mario:
    """Main character class"""
    def __init__(self):
        self.x = 100
        self.y = 400
        self.vx = 0
        self.vy = 0
        self.width = 40
        self.height = 60
        self.facing_right = True
        self.jumping = False
        self.on_ground = True
        
        # Stats
        self.level = 1
        self.max_hp = 10
        self.hp = 10
        self.max_fp = 5
        self.fp = 5
        self.attack = 3
        self.defense = 0
        self.exp = 0
        self.exp_to_next = 100
        self.coins = 0
        self.star_points = 0
        
        # Animation
        self.animation_timer = 0
        self.walking = False
        
        # Abilities
        self.has_hammer = False
        self.has_super_jump = False
        self.badges = []
        
    def update(self, platforms):
        """Update Mario's position and physics"""
        # Apply gravity
        if not self.on_ground:
            self.vy += GRAVITY
            
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Check ground collision
        self.on_ground = False
        for platform in platforms:
            if self.check_platform_collision(platform):
                self.on_ground = True
                self.vy = 0
                self.y = platform['y'] - self.height
                
        # Keep in bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        
        # Animation
        if abs(self.vx) > 0:
            self.animation_timer += 1
            self.walking = True
        else:
            self.walking = False
            
    def check_platform_collision(self, platform):
        """Check collision with platform"""
        return (self.x < platform['x'] + platform['width'] and
                self.x + self.width > platform['x'] and
                self.y + self.height > platform['y'] and
                self.y < platform['y'] + platform['height'] and
                self.vy >= 0)
                
    def jump(self):
        """Make Mario jump"""
        if self.on_ground:
            self.vy = JUMP_STRENGTH
            self.on_ground = False
            self.jumping = True
            
    def move_left(self):
        """Move Mario left"""
        self.vx = -5
        self.facing_right = False
        
    def move_right(self):
        """Move Mario right"""
        self.vx = 5
        self.facing_right = True
        
    def stop(self):
        """Stop horizontal movement"""
        self.vx = 0
        
    def level_up(self):
        """Level up Mario"""
        self.level += 1
        self.max_hp += 5
        self.hp = self.max_hp
        self.max_fp += 3
        self.fp = self.max_fp
        self.attack += 1
        self.exp = 0
        self.exp_to_next = self.level * 100
        
    def draw(self, screen):
        """Draw Mario with paper effect"""
        # Body (paper-thin when turning)
        width_mod = abs(math.sin(self.animation_timer * 0.1)) * 10 if self.walking else 0
        body_width = self.width - width_mod
        
        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 128), 
                           (self.x - 5, self.y + self.height - 5, 
                            self.width + 10, 10))
        
        # Main body
        pygame.draw.rect(screen, RED, 
                        (self.x + width_mod//2, self.y + 20, 
                         body_width, 30))
        
        # Overalls
        pygame.draw.rect(screen, BLUE, 
                        (self.x + width_mod//2, self.y + 35, 
                         body_width, 25))
        
        # Head
        pygame.draw.circle(screen, (255, 220, 177), 
                          (int(self.x + self.width//2), int(self.y + 15)), 
                          15)
        
        # Hat
        pygame.draw.rect(screen, RED, 
                        (self.x + 10 + width_mod//2, self.y, 
                         20 - width_mod//2, 10))
        
        # Mustache
        pygame.draw.rect(screen, BLACK, 
                        (self.x + 12, self.y + 18, 16, 3))
        
        # Eyes
        eye_x = self.x + 25 if self.facing_right else self.x + 15
        pygame.draw.circle(screen, BLACK, (eye_x, self.y + 12), 2)

class Chapter:
    """Chapter/Level class"""
    def __init__(self, number, name, description, boss=None):
        self.number = number
        self.name = name
        self.description = description
        self.boss = boss
        self.completed = False
        self.star_piece_collected = False
        self.enemies = []
        self.npcs = []
        self.platforms = []
        self.items = []
        self.background_color = BLACK
        
    def generate_level(self):
        """Generate level layout"""
        # Create platforms based on chapter
        if self.number == 1:
            # Goomba Road
            self.background_color = (135, 206, 235)  # Sky blue
            self.platforms = [
                {'x': 0, 'y': 500, 'width': SCREEN_WIDTH, 'height': 100},
                {'x': 200, 'y': 400, 'width': 150, 'height': 20},
                {'x': 400, 'y': 350, 'width': 100, 'height': 20},
                {'x': 600, 'y': 300, 'width': 200, 'height': 20},
            ]
            self.enemies = [
                Enemy("Goomba", 5, 2, 0, BROWN, 10),
                Enemy("Goomba", 5, 2, 0, BROWN, 10),
                Enemy("Paragoomba", 7, 3, 0, BROWN, 15),
            ]
            
        elif self.number == 2:
            # Koopa Fortress
            self.background_color = (70, 70, 100)
            self.platforms = [
                {'x': 0, 'y': 550, 'width': SCREEN_WIDTH, 'height': 50},
                {'x': 100, 'y': 450, 'width': 200, 'height': 20},
                {'x': 400, 'y': 400, 'width': 150, 'height': 20},
                {'x': 650, 'y': 350, 'width': 200, 'height': 20},
                {'x': 300, 'y': 250, 'width': 400, 'height': 20},
            ]
            self.enemies = [
                Enemy("Koopa Troopa", 8, 3, 1, GREEN, 20),
                Enemy("Koopa Troopa", 8, 3, 1, GREEN, 20),
                Enemy("Hammer Bro", 12, 5, 1, GREEN, 30),
            ]
            
        elif self.number == 3:
            # Dry Dry Desert
            self.background_color = (255, 220, 100)
            self.platforms = [
                {'x': 0, 'y': 520, 'width': SCREEN_WIDTH, 'height': 80},
                {'x': 150, 'y': 420, 'width': 100, 'height': 20},
                {'x': 350, 'y': 370, 'width': 150, 'height': 20},
                {'x': 600, 'y': 420, 'width': 100, 'height': 20},
                {'x': 800, 'y': 320, 'width': 150, 'height': 20},
            ]
            self.enemies = [
                Enemy("Pokey", 10, 4, 2, YELLOW, 25),
                Enemy("Bandit", 8, 5, 1, PURPLE, 20),
                Enemy("Swooper", 6, 3, 0, PURPLE, 15),
            ]
            
        elif self.number == 4:
            # Shy Guy's Toy Box
            self.background_color = (255, 100, 200)
            self.platforms = [
                {'x': 0, 'y': 500, 'width': SCREEN_WIDTH, 'height': 100},
                {'x': 100, 'y': 400, 'width': 120, 'height': 20},
                {'x': 300, 'y': 350, 'width': 100, 'height': 20},
                {'x': 500, 'y': 300, 'width': 150, 'height': 20},
                {'x': 750, 'y': 250, 'width': 200, 'height': 20},
            ]
            self.enemies = [
                Enemy("Shy Guy", 7, 3, 1, RED, 18),
                Enemy("Shy Guy", 7, 3, 1, BLUE, 18),
                Enemy("Groove Guy", 9, 4, 1, PURPLE, 25),
                Enemy("Sky Guy", 8, 3, 0, WHITE, 20),
            ]
            
        elif self.number == 5:
            # Lavalava Island
            self.background_color = (100, 50, 0)
            self.platforms = [
                {'x': 0, 'y': 550, 'width': SCREEN_WIDTH, 'height': 50},
                {'x': 200, 'y': 450, 'width': 100, 'height': 20},
                {'x': 400, 'y': 400, 'width': 200, 'height': 20},
                {'x': 700, 'y': 350, 'width': 150, 'height': 20},
                {'x': 300, 'y': 280, 'width': 300, 'height': 20},
            ]
            self.enemies = [
                Enemy("Lava Bubble", 6, 4, 0, ORANGE, 15),
                Enemy("Putrid Piranha", 12, 5, 2, GREEN, 30),
                Enemy("Spike Top", 10, 4, 3, RED, 25),
            ]
            
        elif self.number == 6:
            # Flower Fields
            self.background_color = (150, 255, 150)
            self.platforms = [
                {'x': 0, 'y': 500, 'width': SCREEN_WIDTH, 'height': 100},
                {'x': 150, 'y': 400, 'width': 150, 'height': 20},
                {'x': 400, 'y': 350, 'width': 100, 'height': 20},
                {'x': 600, 'y': 300, 'width': 200, 'height': 20},
                {'x': 200, 'y': 250, 'width': 100, 'height': 20},
            ]
            self.enemies = [
                Enemy("Dayzee", 8, 3, 1, YELLOW, 20),
                Enemy("Monty Mole", 10, 4, 2, BROWN, 25),
                Enemy("Lakitu", 12, 5, 1, WHITE, 30),
            ]
            
        elif self.number == 7:
            # Crystal Palace
            self.background_color = (200, 200, 255)
            self.platforms = [
                {'x': 0, 'y': 520, 'width': SCREEN_WIDTH, 'height': 80},
                {'x': 100, 'y': 420, 'width': 200, 'height': 20},
                {'x': 400, 'y': 370, 'width': 150, 'height': 20},
                {'x': 650, 'y': 320, 'width': 200, 'height': 20},
                {'x': 300, 'y': 220, 'width': 300, 'height': 20},
            ]
            self.enemies = [
                Enemy("Crystal Bit", 5, 3, 2, WHITE, 15),
                Enemy("Frost Piranha", 14, 6, 2, BLUE, 35),
                Enemy("Duplighost", 15, 5, 1, WHITE, 40),
            ]
            
        elif self.number == 8:
            # Bowser's Castle
            self.background_color = (50, 0, 0)
            self.platforms = [
                {'x': 0, 'y': 550, 'width': SCREEN_WIDTH, 'height': 50},
                {'x': 150, 'y': 450, 'width': 150, 'height': 20},
                {'x': 400, 'y': 400, 'width': 100, 'height': 20},
                {'x': 600, 'y': 350, 'width': 150, 'height': 20},
                {'x': 850, 'y': 300, 'width': 100, 'height': 20},
                {'x': 300, 'y': 250, 'width': 400, 'height': 20},
            ]
            self.enemies = [
                Enemy("Koopatrol", 18, 7, 4, BLACK, 50),
                Enemy("Magikoopa", 15, 6, 2, BLUE, 45),
                Enemy("Hammer Bro Elite", 20, 8, 3, GREEN, 60),
            ]
            self.boss = Enemy("Bowser", 50, 10, 5, BLACK, 200)

class Battle:
    """Battle system class"""
    def __init__(self, mario, enemies, partners):
        self.mario = mario
        self.enemies = enemies[:]
        self.partners = partners
        self.current_partner = partners[0] if partners else None
        self.turn = "player"
        self.selected_action = None
        self.selected_target = 0
        self.battle_log = []
        self.action_timer = 0
        self.victory = False
        self.defeat = False
        
    def execute_action(self, action, target_index=0):
        """Execute battle action"""
        if action == BattleAction.JUMP:
            if target_index < len(self.enemies):
                damage = self.mario.attack + random.randint(1, 3)
                actual_damage = self.enemies[target_index].take_damage(damage)
                self.battle_log.append(f"Mario jumps on {self.enemies[target_index].name} for {actual_damage} damage!")
                
        elif action == BattleAction.HAMMER and self.mario.has_hammer:
            if target_index < len(self.enemies):
                damage = self.mario.attack + 2 + random.randint(1, 3)
                actual_damage = self.enemies[target_index].take_damage(damage)
                self.battle_log.append(f"Mario hammers {self.enemies[target_index].name} for {actual_damage} damage!")
                
        elif action == BattleAction.PARTNER and self.current_partner:
            if target_index < len(self.enemies):
                damage = self.current_partner.use_ability(self.enemies[target_index])
                actual_damage = self.enemies[target_index].take_damage(damage)
                self.battle_log.append(f"{self.current_partner.name} attacks for {actual_damage} damage!")
                
        elif action == BattleAction.ITEM:
            # Use item (heal for now)
            heal = 5
            self.mario.hp = min(self.mario.max_hp, self.mario.hp + heal)
            self.battle_log.append(f"Mario uses Mushroom and recovers {heal} HP!")
            
        # Remove defeated enemies
        defeated = [e for e in self.enemies if e.is_defeated()]
        for enemy in defeated:
            self.battle_log.append(f"{enemy.name} is defeated!")
            self.mario.exp += enemy.exp_reward
            self.mario.coins += random.randint(1, 5)
            self.enemies.remove(enemy)
            
        # Check victory
        if not self.enemies:
            self.victory = True
            
    def enemy_turn(self):
        """Execute enemy turns"""
        for enemy in self.enemies:
            damage = max(1, enemy.attack - self.mario.defense)
            self.mario.hp -= damage
            self.battle_log.append(f"{enemy.name} attacks Mario for {damage} damage!")
            
            if self.mario.hp <= 0:
                self.defeat = True
                break

class PaperMario:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("📜 PAPER MARIO 64 📜")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        # Game state
        self.state = GameState.INTRO
        self.previous_state = None
        
        # Game objects
        self.mario = Mario()
        self.current_chapter = 1
        self.chapters = self.init_chapters()
        self.partners = self.init_partners()
        self.current_partner_index = 0
        
        # Battle
        self.current_battle = None
        
        # Dialogue
        self.dialogue_text = ""
        self.dialogue_character = ""
        self.dialogue_index = 0
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Animation timers
        self.intro_timer = 0
        self.transition_timer = 0
        
    def init_chapters(self):
        """Initialize all chapters"""
        chapters = [
            Chapter(1, "Goomba Road", "The adventure begins! Rescue Goomba Village from the Goomba King!"),
            Chapter(2, "Koopa Fortress", "Storm the fortress and defeat the Koopa Bros!"),
            Chapter(3, "Dry Dry Desert", "Explore the scorching desert and find the hidden ruins!"),
            Chapter(4, "Shy Guy's Toy Box", "Enter the mysterious toy box and stop General Guy!"),
            Chapter(5, "Lavalava Island", "Journey to the volcanic island and calm the volcano!"),
            Chapter(6, "Flower Fields", "Save the beautiful flower fields from Huff N. Puff!"),
            Chapter(7, "Crystal Palace", "Navigate the frozen palace and defeat the Crystal King!"),
            Chapter(8, "Bowser's Castle", "The final showdown with Bowser to save Princess Peach!"),
        ]
        for chapter in chapters:
            chapter.generate_level()
        return chapters
        
    def init_partners(self):
        """Initialize partner characters"""
        return [
            Partner("Goombario", BROWN, 10, "Headbonk"),
            Partner("Kooper", BLUE, 12, "Shell Toss"),
            Partner("Bombette", PINK, 15, "Bomb"),
            Partner("Parakarry", YELLOW, 11, "Air Lift"),
            Partner("Bow", WHITE, 10, "Spook"),
            Partner("Watt", YELLOW, 8, "Electro Dash"),
            Partner("Sushie", PURPLE, 14, "Squirt"),
            Partner("Lakilester", WHITE, 13, "Spiny Flip"),
        ]
        
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.INTRO:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.OVERWORLD
                        
                elif self.state == GameState.OVERWORLD:
                    if event.key == pygame.K_LEFT:
                        self.mario.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.mario.move_right()
                    elif event.key == pygame.K_SPACE:
                        self.mario.jump()
                    elif event.key == pygame.K_b:
                        # Start battle with random enemy
                        if self.chapters[self.current_chapter - 1].enemies:
                            self.start_battle()
                    elif event.key == pygame.K_p:
                        # Switch partner
                        self.current_partner_index = (self.current_partner_index + 1) % len(self.partners)
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
                        
                elif self.state == GameState.BATTLE:
                    if event.key == pygame.K_1:
                        self.current_battle.execute_action(BattleAction.JUMP, 0)
                        self.current_battle.turn = "enemy"
                    elif event.key == pygame.K_2 and self.mario.has_hammer:
                        self.current_battle.execute_action(BattleAction.HAMMER, 0)
                        self.current_battle.turn = "enemy"
                    elif event.key == pygame.K_3:
                        self.current_battle.execute_action(BattleAction.PARTNER, 0)
                        self.current_battle.turn = "enemy"
                    elif event.key == pygame.K_4:
                        self.current_battle.execute_action(BattleAction.ITEM)
                        self.current_battle.turn = "enemy"
                    elif event.key == pygame.K_5:
                        # Run from battle
                        self.state = GameState.OVERWORLD
                        self.current_battle = None
                        
                elif self.state == GameState.DIALOGUE:
                    if event.key == pygame.K_SPACE:
                        self.state = self.previous_state
                        
                elif self.state == GameState.MENU:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                        self.state = GameState.OVERWORLD
                        
                elif self.state == GameState.CHAPTER_COMPLETE:
                    if event.key == pygame.K_SPACE:
                        self.next_chapter()
                        
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.__init__()
                        
            elif event.type == pygame.KEYUP:
                if self.state == GameState.OVERWORLD:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        self.mario.stop()
                        
        return True
        
    def start_battle(self):
        """Start a battle"""
        chapter = self.chapters[self.current_chapter - 1]
        if chapter.enemies:
            # Take some enemies for battle
            num_enemies = min(3, len(chapter.enemies))
            battle_enemies = random.sample(chapter.enemies, num_enemies)
            self.current_battle = Battle(self.mario, battle_enemies, 
                                        [self.partners[self.current_partner_index]])
            self.state = GameState.BATTLE
            
    def next_chapter(self):
        """Move to next chapter"""
        if self.current_chapter < len(self.chapters):
            self.current_chapter += 1
            self.mario.x = 100
            self.mario.y = 400
            self.state = GameState.OVERWORLD
            
            # Give rewards
            self.mario.star_points += 1
            self.mario.level_up()
            
            # New ability every 2 chapters
            if self.current_chapter == 2:
                self.mario.has_hammer = True
                self.show_dialogue("New Ability!", "You got the Hammer! Press 2 in battle to use it!")
            elif self.current_chapter == 4:
                self.mario.has_super_jump = True
                self.show_dialogue("New Ability!", "You got the Super Jump!")
        else:
            self.state = GameState.VICTORY
            
    def show_dialogue(self, character, text):
        """Show dialogue"""
        self.dialogue_character = character
        self.dialogue_text = text
        self.previous_state = self.state
        self.state = GameState.DIALOGUE
        
    def update(self):
        """Update game logic"""
        if self.state == GameState.INTRO:
            self.intro_timer += 1
            
        elif self.state == GameState.OVERWORLD:
            # Update Mario
            chapter = self.chapters[self.current_chapter - 1]
            self.mario.update(chapter.platforms)
            
            # Check if chapter is complete (reach right side)
            if self.mario.x > SCREEN_WIDTH - 100:
                self.state = GameState.CHAPTER_COMPLETE
                chapter.completed = True
                
            # Check if Mario fell
            if self.mario.y > SCREEN_HEIGHT:
                self.mario.hp -= 1
                self.mario.x = 100
                self.mario.y = 400
                if self.mario.hp <= 0:
                    self.state = GameState.GAME_OVER
                    
            # Random battles
            if random.random() < 0.005 and chapter.enemies:
                self.start_battle()
                
        elif self.state == GameState.BATTLE:
            if self.current_battle:
                self.current_battle.action_timer += 1
                
                # Handle enemy turn
                if self.current_battle.turn == "enemy" and self.current_battle.action_timer > 60:
                    self.current_battle.enemy_turn()
                    self.current_battle.turn = "player"
                    self.current_battle.action_timer = 0
                    
                # Check battle end
                if self.current_battle.victory:
                    self.state = GameState.OVERWORLD
                    self.current_battle = None
                    # Level up check
                    if self.mario.exp >= self.mario.exp_to_next:
                        self.mario.level_up()
                        self.show_dialogue("Level Up!", f"Mario reached level {self.mario.level}!")
                elif self.current_battle.defeat:
                    self.state = GameState.GAME_OVER
                    
    def draw_intro(self):
        """Draw intro screen"""
        self.screen.fill(BLACK)
        
        # Animated title
        title_y = 100 + math.sin(self.intro_timer * 0.05) * 20
        title = "PAPER MARIO 64"
        title_surface = self.font_large.render(title, True, RED)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, title_y))
        self.screen.blit(title_surface, title_rect)
        
        # Paper effect on title
        for i in range(3):
            offset = i * 2
            shadow_surface = self.font_large.render(title, True, (100, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(SCREEN_WIDTH//2 + offset, title_y + offset))
            self.screen.blit(shadow_surface, shadow_rect)
        
        # Subtitle
        subtitle = "The Thousand-Year Adventure"
        sub_surface = self.font_medium.render(subtitle, True, WHITE)
        sub_rect = sub_surface.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(sub_surface, sub_rect)
        
        # Start prompt
        if self.intro_timer % 60 < 40:
            start_text = "PRESS SPACE TO START"
            start_surface = self.font_small.render(start_text, True, YELLOW)
            start_rect = start_surface.get_rect(center=(SCREEN_WIDTH//2, 400))
            self.screen.blit(start_surface, start_rect)
            
        # Draw paper Mario
        mario_x = SCREEN_WIDTH//2 - 20
        mario_y = 300
        # Body
        pygame.draw.rect(self.screen, RED, (mario_x, mario_y + 20, 40, 30))
        pygame.draw.rect(self.screen, BLUE, (mario_x, mario_y + 35, 40, 25))
        # Head
        pygame.draw.circle(self.screen, (255, 220, 177), (mario_x + 20, mario_y + 15), 15)
        # Hat
        pygame.draw.rect(self.screen, RED, (mario_x + 10, mario_y, 20, 10))
        
    def draw_overworld(self):
        """Draw overworld"""
        chapter = self.chapters[self.current_chapter - 1]
        
        # Background
        self.screen.fill(chapter.background_color)
        
        # Draw clouds for outdoor chapters
        if self.current_chapter in [1, 3, 6]:
            for i in range(5):
                cloud_x = (i * 200 + self.intro_timer) % (SCREEN_WIDTH + 100) - 50
                cloud_y = 50 + i * 30
                self.draw_cloud(cloud_x, cloud_y)
                
        # Draw platforms
        for platform in chapter.platforms:
            # Main platform
            pygame.draw.rect(self.screen, BROWN, 
                           (platform['x'], platform['y'], 
                            platform['width'], platform['height']))
            # Paper edge effect
            pygame.draw.rect(self.screen, BLACK, 
                           (platform['x'], platform['y'], 
                            platform['width'], platform['height']), 2)
                            
        # Draw chapter elements
        if self.current_chapter == 1:
            # Draw trees
            for i in range(3):
                tree_x = 200 + i * 300
                tree_y = 430
                self.draw_tree(tree_x, tree_y)
                
        elif self.current_chapter == 3:
            # Draw cacti
            for i in range(4):
                cactus_x = 150 + i * 200
                cactus_y = 470
                self.draw_cactus(cactus_x, cactus_y)
                
        # Draw Mario
        self.mario.draw(self.screen)
        
        # Draw partner following
        if self.partners:
            partner = self.partners[self.current_partner_index]
            partner_x = self.mario.x - 60
            partner_y = self.mario.y + 20
            pygame.draw.circle(self.screen, partner.color, 
                             (partner_x + 20, partner_y + 10), 15)
            # Partner name
            name_surface = self.font_tiny.render(partner.name, True, WHITE)
            self.screen.blit(name_surface, (partner_x, partner_y - 20))
            
        # Draw HUD
        self.draw_hud()
        
        # Chapter info
        chapter_text = f"Chapter {chapter.number}: {chapter.name}"
        chapter_surface = self.font_medium.render(chapter_text, True, WHITE)
        self.screen.blit(chapter_surface, (20, 20))
        
    def draw_battle(self):
        """Draw battle screen"""
        if not self.current_battle:
            return
            
        # Battle background
        self.screen.fill((100, 100, 150))
        
        # Stage
        pygame.draw.rect(self.screen, BROWN, 
                        (50, 400, SCREEN_WIDTH - 100, 200))
        pygame.draw.rect(self.screen, BLACK, 
                        (50, 400, SCREEN_WIDTH - 100, 200), 3)
                        
        # Draw Mario
        mario_x = 200
        mario_y = 450
        # Body
        pygame.draw.rect(self.screen, RED, (mario_x, mario_y + 20, 40, 30))
        pygame.draw.rect(self.screen, BLUE, (mario_x, mario_y + 35, 40, 25))
        # Head
        pygame.draw.circle(self.screen, (255, 220, 177), 
                          (mario_x + 20, mario_y + 15), 15)
        # Hat
        pygame.draw.rect(self.screen, RED, (mario_x + 10, mario_y, 20, 10))
        
        # Draw partner
        if self.current_battle.current_partner:
            partner = self.current_battle.current_partner
            pygame.draw.circle(self.screen, partner.color, 
                             (mario_x - 80, mario_y + 30), 20)
                             
        # Draw enemies
        enemy_x = 600
        for i, enemy in enumerate(self.current_battle.enemies):
            enemy_y = 450 + i * 50
            # Enemy body
            pygame.draw.rect(self.screen, enemy.color, 
                           (enemy_x, enemy_y, 50, 50))
            pygame.draw.rect(self.screen, BLACK, 
                           (enemy_x, enemy_y, 50, 50), 2)
            # HP bar
            hp_percent = enemy.hp / enemy.max_hp
            pygame.draw.rect(self.screen, RED, 
                           (enemy_x, enemy_y - 20, 50, 5))
            pygame.draw.rect(self.screen, GREEN, 
                           (enemy_x, enemy_y - 20, int(50 * hp_percent), 5))
            # Name
            name_surface = self.font_tiny.render(enemy.name, True, WHITE)
            self.screen.blit(name_surface, (enemy_x, enemy_y - 40))
            
        # Draw action menu
        menu_y = 100
        menu_surface = self.font_medium.render("ACTIONS", True, WHITE)
        self.screen.blit(menu_surface, (50, menu_y))
        
        actions = [
            "1 - Jump",
            "2 - Hammer" if self.mario.has_hammer else "2 - [Locked]",
            "3 - Partner",
            "4 - Item",
            "5 - Run"
        ]
        
        for i, action in enumerate(actions):
            action_surface = self.font_small.render(action, True, WHITE)
            self.screen.blit(action_surface, (50, menu_y + 50 + i * 35))
            
        # Battle log
        log_y = 250
        for i, message in enumerate(self.current_battle.battle_log[-3:]):
            log_surface = self.font_tiny.render(message, True, YELLOW)
            self.screen.blit(log_surface, (400, log_y + i * 25))
            
        # Stats
        self.draw_battle_stats()
        
    def draw_battle_stats(self):
        """Draw battle statistics"""
        # Mario stats
        stats_x = 50
        stats_y = 500
        
        hp_text = f"HP: {self.mario.hp}/{self.mario.max_hp}"
        hp_surface = self.font_small.render(hp_text, True, WHITE)
        self.screen.blit(hp_surface, (stats_x, stats_y))
        
        fp_text = f"FP: {self.mario.fp}/{self.mario.max_fp}"
        fp_surface = self.font_small.render(fp_text, True, BLUE)
        self.screen.blit(fp_surface, (stats_x, stats_y + 30))
        
        # Partner HP
        if self.current_battle.current_partner:
            partner = self.current_battle.current_partner
            partner_hp = f"{partner.name}: {partner.hp}/{partner.max_hp}"
            partner_surface = self.font_small.render(partner_hp, True, partner.color)
            self.screen.blit(partner_surface, (stats_x, stats_y + 60))
            
    def draw_hud(self):
        """Draw HUD overlay"""
        # HP/FP bar background
        pygame.draw.rect(self.screen, BLACK, (10, SCREEN_HEIGHT - 80, 200, 70))
        pygame.draw.rect(self.screen, WHITE, (10, SCREEN_HEIGHT - 80, 200, 70), 2)
        
        # HP
        hp_percent = self.mario.hp / self.mario.max_hp
        pygame.draw.rect(self.screen, RED, (20, SCREEN_HEIGHT - 70, 180, 20))
        pygame.draw.rect(self.screen, GREEN, 
                        (20, SCREEN_HEIGHT - 70, int(180 * hp_percent), 20))
        hp_text = f"HP: {self.mario.hp}/{self.mario.max_hp}"
        hp_surface = self.font_tiny.render(hp_text, True, WHITE)
        self.screen.blit(hp_surface, (25, SCREEN_HEIGHT - 70))
        
        # FP
        fp_percent = self.mario.fp / self.mario.max_fp
        pygame.draw.rect(self.screen, BLUE, (20, SCREEN_HEIGHT - 40, 180, 20))
        pygame.draw.rect(self.screen, (0, 150, 255), 
                        (20, SCREEN_HEIGHT - 40, int(180 * fp_percent), 20))
        fp_text = f"FP: {self.mario.fp}/{self.mario.max_fp}"
        fp_surface = self.font_tiny.render(fp_text, True, WHITE)
        self.screen.blit(fp_surface, (25, SCREEN_HEIGHT - 40))
        
        # Stats
        level_text = f"Lv: {self.mario.level}"
        level_surface = self.font_small.render(level_text, True, WHITE)
        self.screen.blit(level_surface, (220, SCREEN_HEIGHT - 70))
        
        coins_text = f"Coins: {self.mario.coins}"
        coins_surface = self.font_tiny.render(coins_text, True, YELLOW)
        self.screen.blit(coins_surface, (220, SCREEN_HEIGHT - 40))
        
        star_text = f"★ {self.mario.star_points}"
        star_surface = self.font_small.render(star_text, True, YELLOW)
        self.screen.blit(star_surface, (320, SCREEN_HEIGHT - 70))
        
    def draw_menu(self):
        """Draw pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Menu box
        menu_rect = pygame.Rect(200, 100, 600, 500)
        pygame.draw.rect(self.screen, BROWN, menu_rect)
        pygame.draw.rect(self.screen, WHITE, menu_rect, 3)
        
        # Title
        title_surface = self.font_large.render("PAUSE MENU", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Stats
        stats = [
            f"Level: {self.mario.level}",
            f"HP: {self.mario.hp}/{self.mario.max_hp}",
            f"FP: {self.mario.fp}/{self.mario.max_fp}",
            f"Attack: {self.mario.attack}",
            f"Defense: {self.mario.defense}",
            f"Coins: {self.mario.coins}",
            f"Star Points: {self.mario.star_points}",
            f"EXP: {self.mario.exp}/{self.mario.exp_to_next}",
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.font_small.render(stat, True, WHITE)
            self.screen.blit(stat_surface, (250, 220 + i * 35))
            
        # Partners
        partner_text = "Partners:"
        partner_surface = self.font_medium.render(partner_text, True, YELLOW)
        self.screen.blit(partner_surface, (550, 220))
        
        for i, partner in enumerate(self.partners[:4]):
            p_surface = self.font_small.render(partner.name, True, partner.color)
            self.screen.blit(p_surface, (550, 270 + i * 30))
            
        # Instructions
        inst_text = "Press ESC or M to return"
        inst_surface = self.font_small.render(inst_text, True, WHITE)
        inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH//2, 550))
        self.screen.blit(inst_surface, inst_rect)
        
    def draw_dialogue(self):
        """Draw dialogue box"""
        # Dialogue box
        dialogue_rect = pygame.Rect(50, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 100, 150)
        pygame.draw.rect(self.screen, BROWN, dialogue_rect)
        pygame.draw.rect(self.screen, WHITE, dialogue_rect, 3)
        
        # Character name
        if self.dialogue_character:
            name_surface = self.font_medium.render(self.dialogue_character, True, WHITE)
            self.screen.blit(name_surface, (70, SCREEN_HEIGHT - 190))
            
        # Dialogue text
        text_surface = self.font_small.render(self.dialogue_text, True, WHITE)
        self.screen.blit(text_surface, (70, SCREEN_HEIGHT - 140))
        
        # Continue prompt
        prompt = "Press SPACE to continue"
        prompt_surface = self.font_tiny.render(prompt, True, YELLOW)
        self.screen.blit(prompt_surface, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 70))
        
    def draw_chapter_complete(self):
        """Draw chapter complete screen"""
        self.screen.fill(BLACK)
        
        # Star animation
        star_y = 200 + math.sin(self.intro_timer * 0.1) * 20
        self.draw_star(SCREEN_WIDTH//2, star_y, 50, YELLOW)
        
        # Text
        complete_text = f"Chapter {self.current_chapter} Complete!"
        complete_surface = self.font_large.render(complete_text, True, WHITE)
        complete_rect = complete_surface.get_rect(center=(SCREEN_WIDTH//2, 350))
        self.screen.blit(complete_surface, complete_rect)
        
        # Rewards
        rewards_text = "You got a Star Point!"
        rewards_surface = self.font_medium.render(rewards_text, True, YELLOW)
        rewards_rect = rewards_surface.get_rect(center=(SCREEN_WIDTH//2, 420))
        self.screen.blit(rewards_surface, rewards_rect)
        
        # Continue
        cont_text = "Press SPACE to continue"
        cont_surface = self.font_small.render(cont_text, True, WHITE)
        cont_rect = cont_surface.get_rect(center=(SCREEN_WIDTH//2, 500))
        self.screen.blit(cont_surface, cont_rect)
        
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(BLACK)
        
        go_text = "GAME OVER"
        go_surface = self.font_large.render(go_text, True, RED)
        go_rect = go_surface.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(go_surface, go_rect)
        
        restart_text = "Press R to restart"
        restart_surface = self.font_medium.render(restart_text, True, WHITE)
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH//2, 400))
        self.screen.blit(restart_surface, restart_rect)
        
    def draw_victory(self):
        """Draw victory screen"""
        self.screen.fill(BLACK)
        
        # Animated rainbow text
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        victory_text = "VICTORY!"
        for i, char in enumerate(victory_text):
            color = colors[(self.intro_timer // 10 + i) % len(colors)]
            char_surface = self.font_large.render(char, True, color)
            x = SCREEN_WIDTH//2 - 150 + i * 40
            y = 200 + math.sin(self.intro_timer * 0.1 + i) * 20
            self.screen.blit(char_surface, (x, y))
            
        # Credits
        credits = [
            "You saved the Mushroom Kingdom!",
            f"Final Level: {self.mario.level}",
            f"Star Points Collected: {self.mario.star_points}",
            f"Total Coins: {self.mario.coins}",
            "",
            "Thanks for playing!",
        ]
        
        for i, credit in enumerate(credits):
            credit_surface = self.font_small.render(credit, True, WHITE)
            credit_rect = credit_surface.get_rect(center=(SCREEN_WIDTH//2, 350 + i * 40))
            self.screen.blit(credit_surface, credit_rect)
            
    def draw_cloud(self, x, y):
        """Draw a paper cloud"""
        pygame.draw.ellipse(self.screen, WHITE, (x, y, 80, 40))
        pygame.draw.ellipse(self.screen, WHITE, (x + 20, y - 10, 60, 40))
        pygame.draw.ellipse(self.screen, WHITE, (x + 40, y, 70, 35))
        
    def draw_tree(self, x, y):
        """Draw a paper tree"""
        # Trunk
        pygame.draw.rect(self.screen, BROWN, (x - 10, y, 20, 40))
        # Leaves
        pygame.draw.circle(self.screen, GREEN, (x, y - 20), 30)
        pygame.draw.circle(self.screen, GREEN, (x - 20, y - 10), 25)
        pygame.draw.circle(self.screen, GREEN, (x + 20, y - 10), 25)
        
    def draw_cactus(self, x, y):
        """Draw a paper cactus"""
        # Main body
        pygame.draw.rect(self.screen, GREEN, (x - 15, y - 40, 30, 60))
        # Arms
        pygame.draw.rect(self.screen, GREEN, (x - 35, y - 20, 20, 15))
        pygame.draw.rect(self.screen, GREEN, (x + 15, y - 30, 20, 15))
        # Spikes
        for i in range(5):
            spike_y = y - 35 + i * 10
            pygame.draw.line(self.screen, WHITE, (x - 15, spike_y), (x - 18, spike_y), 2)
            pygame.draw.line(self.screen, WHITE, (x + 15, spike_y), (x + 18, spike_y), 2)
            
    def draw_star(self, x, y, size, color):
        """Draw a star"""
        points = []
        for i in range(10):
            angle = math.pi * 2 * i / 10
            if i % 2 == 0:
                radius = size
            else:
                radius = size * 0.5
            px = x + math.cos(angle - math.pi/2) * radius
            py = y + math.sin(angle - math.pi/2) * radius
            points.append((px, py))
        pygame.draw.polygon(self.screen, color, points)
        
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update
            self.update()
            self.intro_timer += 1
            
            # Draw
            if self.state == GameState.INTRO:
                self.draw_intro()
            elif self.state == GameState.OVERWORLD:
                self.draw_overworld()
            elif self.state == GameState.BATTLE:
                self.draw_battle()
            elif self.state == GameState.MENU:
                self.draw_overworld()  # Draw world in background
                self.draw_menu()
            elif self.state == GameState.DIALOGUE:
                if self.previous_state == GameState.OVERWORLD:
                    self.draw_overworld()
                elif self.previous_state == GameState.BATTLE:
                    self.draw_battle()
                self.draw_dialogue()
            elif self.state == GameState.CHAPTER_COMPLETE:
                self.draw_chapter_complete()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.VICTORY:
                self.draw_victory()
                
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

# Run the game
if __name__ == "__main__":
    print("🌟 PAPER MARIO 64 🌟")
    print("=" * 40)
    print("CONTROLS:")
    print("  Arrow Keys - Move")
    print("  SPACE - Jump / Confirm")
    print("  M - Menu")
    print("  P - Switch Partner")
    print("  B - Start Battle (debug)")
    print("\nBATTLE CONTROLS:")
    print("  1 - Jump Attack")
    print("  2 - Hammer (Chapter 2+)")
    print("  3 - Partner Attack")
    print("  4 - Use Item")
    print("  5 - Run Away")
    print("=" * 40)
    print("Starting game...")
    
    game = PaperMario()
    game.run()
