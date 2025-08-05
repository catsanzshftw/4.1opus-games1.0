import pygame
import math
import random
import json
from enum import Enum, auto
from typing import List, Dict, Tuple, Optional

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

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
DARK_PURPLE = (75, 0, 130)
GOLD = (255, 215, 0)

class MusicGenerator:
    """Generates OST for both Paper Mario games"""
    def __init__(self):
        self.sample_rate = 22050
        self.current_track = None
        self.tracks = {}
        self.init_tracks()
        self.playing = False
        self.volume = 0.3
        
    def init_tracks(self):
        """Initialize all music tracks"""
        # Note frequencies (C4-B5)
        self.notes = {
            'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13,
            'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00,
            'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
            'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25,
            'E5': 659.25, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99,
            'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77,
            'REST': 0
        }
        
    def generate_wave(self, frequency, duration, wave_type='square'):
        """Generate a waveform"""
        import numpy as np
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)
        
        if frequency == 0:  # Rest
            return np.zeros(samples)
            
        if wave_type == 'square':
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == 'sine':
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == 'triangle':
            wave = 2 * np.arcsin(np.sin(2 * np.pi * frequency * t)) / np.pi
        elif wave_type == 'sawtooth':
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        else:
            wave = np.sin(2 * np.pi * frequency * t)
            
        # Apply envelope (ADSR)
        envelope = np.ones(samples)
        attack = int(samples * 0.05)
        decay = int(samples * 0.1)
        release = int(samples * 0.2)
        
        # Attack
        envelope[:attack] = np.linspace(0, 1, attack)
        # Decay
        envelope[attack:attack+decay] = np.linspace(1, 0.7, decay)
        # Sustain at 0.7
        # Release
        envelope[-release:] = np.linspace(0.7, 0, release)
        
        return wave * envelope * 16000 * self.volume
        
    def generate_melody(self, notes, durations, wave_type='square'):
        """Generate a melody from notes and durations"""
        import numpy as np
        melody = np.array([])
        
        for note, duration in zip(notes, durations):
            if note in self.notes:
                freq = self.notes[note]
                wave = self.generate_wave(freq, duration, wave_type)
                melody = np.concatenate([melody, wave])
                
        return melody.astype(np.int16)
        
    def generate_pm64_title(self):
        """Generate Paper Mario 64 title theme"""
        # Main melody - cheerful and bouncy
        melody_notes = [
            'C5', 'E5', 'G5', 'E5', 'C5', 'G4', 'E4', 'G4',
            'D5', 'F5', 'A5', 'F5', 'D5', 'A4', 'F4', 'A4',
            'E5', 'G5', 'B5', 'G5', 'E5', 'B4', 'G4', 'B4',
            'C5', 'E5', 'G5', 'C5', 'REST', 'C5', 'C5', 'REST'
        ]
        melody_durations = [0.2] * len(melody_notes)
        
        # Bass line
        bass_notes = [
            'C4', 'REST', 'C4', 'REST', 'G4', 'REST', 'G4', 'REST',
            'F4', 'REST', 'F4', 'REST', 'D4', 'REST', 'D4', 'REST',
            'E4', 'REST', 'E4', 'REST', 'G4', 'REST', 'G4', 'REST',
            'C4', 'REST', 'G4', 'REST', 'C4', 'REST', 'REST', 'REST'
        ]
        bass_durations = [0.2] * len(bass_notes)
        
        melody = self.generate_melody(melody_notes, melody_durations, 'square')
        bass = self.generate_melody(bass_notes, bass_durations, 'triangle')
        
        # Mix channels
        import numpy as np
        max_len = max(len(melody), len(bass))
        mixed = np.zeros(max_len, dtype=np.int16)
        mixed[:len(melody)] += melody // 2
        mixed[:len(bass)] += bass // 3
        
        return mixed
        
    def generate_ttyd_title(self):
        """Generate TTYD title theme - more orchestral and mysterious"""
        # Main melody - mysterious and grand
        melody_notes = [
            'A4', 'C5', 'E5', 'A5', 'G5', 'F5', 'E5', 'D5',
            'C5', 'B4', 'A4', 'G4', 'F4', 'E4', 'D4', 'C4',
            'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5', 'D5',
            'E5', 'REST', 'E5', 'REST', 'A5', 'REST', 'REST', 'REST'
        ]
        melody_durations = [0.3, 0.3, 0.3, 0.6, 0.3, 0.3, 0.3, 0.3,
                           0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.6,
                           0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2,
                           0.6, 0.2, 0.6, 0.2, 0.8, 0.4, 0.4, 0.4]
        
        melody = self.generate_melody(melody_notes, melody_durations, 'sine')
        return melody
        
    def generate_battle_music(self, game='PM64'):
        """Generate battle music"""
        if game == 'PM64':
            # Energetic PM64 battle theme
            notes = [
                'C5', 'C5', 'REST', 'C5', 'REST', 'G4', 'E5', 'REST',
                'G5', 'REST', 'E5', 'REST', 'C5', 'REST', 'G4', 'REST',
                'E4', 'REST', 'A4', 'REST', 'B4', 'REST', 'A#4', 'A4',
                'G4', 'E5', 'G5', 'A5', 'F5', 'G5', 'REST', 'E5'
            ]
            durations = [0.15] * len(notes)
        else:
            # TTYD battle theme - more intense
            notes = [
                'E5', 'D#5', 'E5', 'B4', 'D5', 'C5', 'A4', 'REST',
                'C4', 'E4', 'A4', 'B4', 'REST', 'E4', 'G#4', 'B4',
                'C5', 'REST', 'E4', 'E5', 'D#5', 'E5', 'D#5', 'E5',
                'B4', 'D5', 'C5', 'A4', 'REST', 'REST', 'REST', 'REST'
            ]
            durations = [0.125] * len(notes)
            
        return self.generate_melody(notes, durations, 'square')
        
    def generate_chapter_music(self, chapter_num, game='PM64'):
        """Generate chapter-specific music"""
        import numpy as np
        
        if game == 'PM64':
            if chapter_num == 1:  # Goomba Village - peaceful
                notes = ['C5', 'E5', 'G5', 'E5'] * 4 + ['F5', 'A5', 'C5', 'A4'] * 2
                wave_type = 'sine'
            elif chapter_num == 2:  # Koopa Fortress - march-like
                notes = ['G4', 'G4', 'D5', 'D5', 'B4', 'B4', 'G4', 'REST'] * 2
                wave_type = 'square'
            elif chapter_num == 3:  # Desert - mysterious
                notes = ['D4', 'F4', 'A4', 'G4', 'F4', 'E4', 'D4', 'REST'] * 2
                wave_type = 'triangle'
            elif chapter_num == 4:  # Toy Box - playful
                notes = ['E5', 'C5', 'G4', 'C5'] * 3 + ['D5', 'B4', 'G4', 'REST']
                wave_type = 'square'
            elif chapter_num == 5:  # Lavalava Island - tropical
                notes = ['A4', 'C5', 'E5', 'D5', 'C5', 'B4', 'A4', 'G4'] * 2
                wave_type = 'sine'
            elif chapter_num == 6:  # Flower Fields - serene
                notes = ['F5', 'E5', 'D5', 'C5', 'B4', 'C5', 'D5', 'E5'] * 2
                wave_type = 'sine'
            elif chapter_num == 7:  # Crystal Palace - cold
                notes = ['B4', 'C#5', 'D5', 'E5', 'F#5', 'E5', 'D5', 'REST'] * 2
                wave_type = 'triangle'
            else:  # Bowser's Castle - ominous
                notes = ['E4', 'F4', 'E4', 'F4', 'E4', 'B4', 'A4', 'G4'] * 2
                wave_type = 'sawtooth'
        else:  # TTYD
            if chapter_num == 1:  # Rogueport - mysterious port town
                notes = ['A4', 'E5', 'C5', 'B4', 'A4', 'G4', 'F4', 'E4'] * 2
                wave_type = 'sine'
            elif chapter_num == 2:  # Boggly Woods - forest mystery
                notes = ['D5', 'F5', 'A5', 'G5', 'F5', 'E5', 'D5', 'C5'] * 2
                wave_type = 'triangle'
            elif chapter_num == 3:  # Glitzville - showtime
                notes = ['C5', 'E5', 'G5', 'B5', 'A5', 'G5', 'F5', 'E5'] * 2
                wave_type = 'square'
            elif chapter_num == 4:  # Twilight Town - spooky
                notes = ['E4', 'G4', 'B4', 'A#4', 'A4', 'G#4', 'G4', 'REST'] * 2
                wave_type = 'triangle'
            elif chapter_num == 5:  # Keelhaul Key - pirate adventure
                notes = ['G4', 'B4', 'D5', 'G5', 'F5', 'E5', 'D5', 'C5'] * 2
                wave_type = 'square'
            elif chapter_num == 6:  # Excess Express - mystery
                notes = ['C#5', 'E5', 'G#5', 'F#5', 'E5', 'D#5', 'C#5', 'B4'] * 2
                wave_type = 'sine'
            elif chapter_num == 7:  # Moon - space
                notes = ['A5', 'G5', 'F5', 'E5', 'D5', 'C5', 'B4', 'A4'] * 2
                wave_type = 'triangle'
            else:  # Palace of Shadow - final
                notes = ['E4', 'F4', 'G4', 'A4', 'B4', 'C5', 'D5', 'E5'] * 2
                wave_type = 'sawtooth'
                
        durations = [0.25] * len(notes)
        return self.generate_melody(notes, durations, wave_type)
        
    def generate_boss_music(self, game='PM64'):
        """Generate boss battle music"""
        if game == 'PM64':
            # Bowser's theme
            notes = [
                'E4', 'E4', 'E4', 'REST', 'C4', 'E4', 'G4', 'REST',
                'G3', 'REST', 'REST', 'REST', 'G4', 'F#4', 'F4', 'D#4',
                'E4', 'REST', 'G#3', 'A3', 'C4', 'REST', 'A3', 'C4', 'D4'
            ]
        else:
            # Shadow Queen theme
            notes = [
                'A3', 'A3', 'E4', 'A3', 'G3', 'F3', 'E3', 'D3',
                'C3', 'REST', 'C3', 'D3', 'E3', 'F3', 'G3', 'A3',
                'B3', 'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'REST'
            ]
            
        durations = [0.2] * len(notes)
        return self.generate_melody(notes, durations, 'sawtooth')
        
    def generate_victory_fanfare(self):
        """Generate victory music"""
        notes = [
            'C5', 'C5', 'C5', 'C5', 'G#4', 'A#4', 'C5', 'REST',
            'A#4', 'C5', 'REST', 'REST', 'REST', 'REST', 'REST', 'REST'
        ]
        durations = [0.1, 0.1, 0.1, 0.4, 0.2, 0.2, 0.6, 0.2,
                     0.4, 0.8, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
        return self.generate_melody(notes, durations, 'square')
        
    def play_track(self, track_name, game='PM64', chapter=1):
        """Play a specific music track"""
        try:
            import numpy as np
            
            if track_name == 'title':
                if game == 'PM64':
                    music_data = self.generate_pm64_title()
                else:
                    music_data = self.generate_ttyd_title()
            elif track_name == 'battle':
                music_data = self.generate_battle_music(game)
            elif track_name == 'boss':
                music_data = self.generate_boss_music(game)
            elif track_name == 'victory':
                music_data = self.generate_victory_fanfare()
            elif track_name == 'chapter':
                music_data = self.generate_chapter_music(chapter, game)
            else:
                return
                
            # Convert to stereo
            stereo_data = np.zeros((len(music_data), 2), dtype=np.int16)
            stereo_data[:, 0] = music_data
            stereo_data[:, 1] = music_data
            
            # Create and play sound
            sound = pygame.sndarray.make_sound(stereo_data)
            sound.set_volume(self.volume)
            sound.play(-1)  # Loop indefinitely
            self.current_track = sound
            self.playing = True
            
        except ImportError:
            # If numpy isn't available, music won't play but game continues
            print("Music system requires NumPy. Install with: pip install numpy")
            self.playing = False
            
    def stop(self):
        """Stop current music"""
        if self.current_track:
            self.current_track.stop()
            self.playing = False
            
    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.current_track:
            self.current_track.set_volume(self.volume)

# Game States
class GameState(Enum):
    INTRO = auto()
    GAME_SELECT = auto()
    OVERWORLD = auto()
    BATTLE = auto()
    DIALOGUE = auto()
    MENU = auto()
    CHAPTER_COMPLETE = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    AUDIENCE = auto()

# Battle Actions
class BattleAction(Enum):
    JUMP = auto()
    HAMMER = auto()
    ITEM = auto()
    RUN = auto()
    SPECIAL = auto()
    PARTNER = auto()
    STYLISH = auto()
    APPEAL = auto()

# Paper Modes (TTYD)
class PaperMode(Enum):
    NORMAL = auto()
    PLANE = auto()
    TUBE = auto()
    BOAT = auto()
    THIN = auto()

class Audience:
    """TTYD Audience system"""
    def __init__(self):
        self.size = 50
        self.max_size = 200
        self.excitement = 50
        self.members = []
        self.star_power = 0
        self.max_star_power = 100
        
    def add_member(self):
        if self.size < self.max_size:
            self.size += 1
            
    def remove_member(self):
        if self.size > 0:
            self.size -= 1
            
    def increase_excitement(self, amount):
        self.excitement = min(100, self.excitement + amount)
        if self.excitement > 80:
            self.add_member()
            
    def decrease_excitement(self, amount):
        self.excitement = max(0, self.excitement - amount)
        if self.excitement < 20:
            self.remove_member()
            
    def generate_star_power(self, amount):
        self.star_power = min(self.max_star_power, self.star_power + amount)

class Partner:
    """Enhanced partner character class"""
    def __init__(self, name, color, hp, ability, game):
        self.name = name
        self.color = color
        self.max_hp = hp
        self.hp = hp
        self.ability = ability
        self.level = 1
        self.game = game  # PM64 or TTYD
        self.rank = 0  # TTYD rank system
        
    def use_ability(self, target):
        """Use partner's special ability"""
        damage = 3 + self.level + (self.rank * 2)
        return damage
        
    def upgrade(self):
        """TTYD upgrade system"""
        if self.rank < 2:
            self.rank += 1
            self.max_hp += 10
            self.hp = self.max_hp

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
        self.status_effects = []
        
    def take_damage(self, damage):
        """Enemy takes damage"""
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        return actual_damage
        
    def is_defeated(self):
        """Check if enemy is defeated"""
        return self.hp <= 0

class Mario:
    """Enhanced main character class"""
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
        self.max_bp = 3  # Badge Points (TTYD)
        self.bp = 3
        self.attack = 3
        self.defense = 0
        self.exp = 0
        self.exp_to_next = 100
        self.coins = 0
        self.star_points = 0
        self.shine_sprites = 0  # TTYD collectibles
        
        # Animation
        self.animation_timer = 0
        self.walking = False
        
        # Abilities
        self.has_hammer = False
        self.has_super_jump = False
        self.has_spin_jump = False  # TTYD
        self.has_spring_jump = False  # TTYD
        self.badges = []
        self.paper_mode = PaperMode.NORMAL
        
        # TTYD mechanics
        self.stylish_moves = []
        self.crystal_stars = []
        self.star_pieces = []
        
    def update(self, platforms):
        """Update Mario's position and physics"""
        # Apply gravity
        if not self.on_ground:
            self.vy += GRAVITY
            
        # Paper mode physics (TTYD)
        if self.paper_mode == PaperMode.PLANE:
            self.vy = max(-3, self.vy)  # Slower falling
        elif self.paper_mode == PaperMode.TUBE:
            self.speed = 7  # Faster rolling
            
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
        """Enhanced level up with choice system"""
        self.level += 1
        # Player would choose HP, FP, or BP
        self.max_hp += 5
        self.hp = self.max_hp
        self.max_fp += 3
        self.fp = self.max_fp
        self.attack += 1
        self.exp = 0
        self.exp_to_next = self.level * 100
        
    def switch_paper_mode(self, mode):
        """TTYD paper transformations"""
        self.paper_mode = mode
        
    def draw(self, screen):
        """Draw Mario with paper effect"""
        # Body (paper-thin when turning)
        width_mod = abs(math.sin(self.animation_timer * 0.1)) * 10 if self.walking else 0
        
        # Apply paper mode visual changes
        if self.paper_mode == PaperMode.THIN:
            width_mod = self.width - 5  # Very thin
        elif self.paper_mode == PaperMode.PLANE:
            # Draw as paper plane
            points = [
                (self.x, self.y + 30),
                (self.x + 40, self.y + 20),
                (self.x + 20, self.y + 40)
            ]
            pygame.draw.polygon(screen, RED, points)
            return
        elif self.paper_mode == PaperMode.TUBE:
            # Draw as tube/cylinder
            pygame.draw.ellipse(screen, RED, 
                              (self.x, self.y + 20, 40, 40))
            return
            
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
    """Enhanced Chapter/Level class for both games"""
    def __init__(self, number, name, description, game="PM64", boss=None):
        self.number = number
        self.name = name
        self.description = description
        self.game = game  # PM64 or TTYD
        self.boss = boss
        self.completed = False
        self.star_piece_collected = False
        self.crystal_star_collected = False  # TTYD
        self.enemies = []
        self.npcs = []
        self.platforms = []
        self.items = []
        self.background_color = BLACK
        self.special_mechanics = []  # TTYD special features
        
    def generate_level(self):
        """Generate level layout based on chapter and game"""
        if self.game == "PM64":
            self.generate_pm64_level()
        else:
            self.generate_ttyd_level()
            
    def generate_pm64_level(self):
        """Generate Paper Mario 64 levels"""
        if self.number == 1:
            # Goomba Road
            self.background_color = (135, 206, 235)
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
            ]
            self.enemies = [
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
            ]
            self.enemies = [
                Enemy("Pokey", 10, 4, 2, YELLOW, 25),
                Enemy("Bandit", 8, 5, 1, PURPLE, 20),
            ]
        elif self.number == 4:
            # Shy Guy's Toy Box
            self.background_color = (255, 100, 200)
            self.platforms = [
                {'x': 0, 'y': 500, 'width': SCREEN_WIDTH, 'height': 100},
                {'x': 100, 'y': 400, 'width': 120, 'height': 20},
                {'x': 300, 'y': 350, 'width': 100, 'height': 20},
                {'x': 500, 'y': 300, 'width': 150, 'height': 20},
            ]
            self.enemies = [
                Enemy("Shy Guy", 7, 3, 1, RED, 18),
                Enemy("Groove Guy", 9, 4, 1, PURPLE, 25),
            ]
        elif self.number == 5:
            # Lavalava Island
            self.background_color = (100, 50, 0)
            self.platforms = [
                {'x': 0, 'y': 550, 'width': SCREEN_WIDTH, 'height': 50},
                {'x': 200, 'y': 450, 'width': 100, 'height': 20},
                {'x': 400, 'y': 400, 'width': 200, 'height': 20},
            ]
            self.enemies = [
                Enemy("Lava Bubble", 6, 4, 0, ORANGE, 15),
                Enemy("Putrid Piranha", 12, 5, 2, GREEN, 30),
            ]
        elif self.number == 6:
            # Flower Fields
            self.background_color = (150, 255, 150)
            self.platforms = [
                {'x': 0, 'y': 500, 'width': SCREEN_WIDTH, 'height': 100},
                {'x': 150, 'y': 400, 'width': 150, 'height': 20},
                {'x': 400, 'y': 350, 'width': 100, 'height': 20},
            ]
            self.enemies = [
                Enemy("Dayzee", 8, 3, 1, YELLOW, 20),
                Enemy("Monty Mole", 10, 4, 2, BROWN, 25),
            ]
        elif self.number == 7:
            # Crystal Palace
            self.background_color = (200, 200, 255)
            self.platforms = [
                {'x': 0, 'y': 520, 'width': SCREEN_WIDTH, 'height': 80},
                {'x': 100, 'y': 420, 'width': 200, 'height': 20},
                {'x': 400, 'y': 370, 'width': 150, 'height': 20},
            ]
            self.enemies = [
                Enemy("Crystal Bit", 5, 3, 2, WHITE, 15),
                Enemy("Frost Piranha", 14, 6, 2, BLUE, 35),
            ]
        elif self.number == 8:
            # Bowser's Castle
            self.background_color = (50, 0, 0)
            self.platforms = [
                {'x': 0, 'y': 550, 'width': SCREEN_WIDTH, 'height': 50},
                {'x': 150, 'y': 450, 'width': 150, 'height': 20},
                {'x': 400, 'y': 400, 'width': 100, 'height': 20},
            ]
            self.enemies = [
                Enemy("Koopatrol", 18, 7, 4, BLACK, 50),
                Enemy("Magikoopa", 15, 6, 2, BLUE, 45),
            ]
            self.boss = Enemy("Bowser", 50, 10, 5, BLACK, 200)
            
    def generate_ttyd_level(self):
        """Generate TTYD levels"""
        if self.number == 1:
            # Rogueport/Petalburg
            self.background_color = (100, 150, 200)
            self.platforms = [
                {'x': 0, 'y': 550, 'width': SCREEN_WIDTH, 'height': 50},
                {'x': 150, 'y': 450, 'width': 200, 'height': 20},
                {'x': 450, 'y': 400, 'width': 150, 'height': 20},
            ]
            self.enemies = [
                Enemy("Goomba", 6, 2, 0, BROWN, 12),
                Enemy("Koopa", 8, 3, 1, GREEN, 18),
                Enemy("Fuzzy", 5, 2, 0, BLACK, 10),
            ]
            self.special_mechanics = ["Paper Mode Tutorial"]
        elif self.number == 2:
            # Boggly Woods
            self.background_color = (50, 100, 50)
            self.platforms = [
                {'x': 0, 'y': 520, 'width': SCREEN_WIDTH, 'height': 80},
                {'x': 200, 'y': 420, 'width': 100, 'height': 20},
                {'x': 400, 'y': 350, 'width': 200, 'height': 20},
            ]
            self.enemies = [
                Enemy("X-Naut", 10, 4, 1, WHITE, 25),
                Enemy("Pider", 7, 3, 0, PURPLE, 15),
                Enemy("Dark Puff", 9, 4, 0, DARK_PURPLE, 20),
            ]
            self.special_mechanics = ["Punies", "Great Tree"]
        elif self.number == 3:
            # Glitzville
            self.background_color = (255, 215, 0)
            self.platforms = [
                {'x': 0, 'y': 500, 'width': SCREEN_WIDTH, 'height': 100},
                {'x': 300, 'y': 400, 'width': 400, 'height': 20},
            ]
            self.enemies = [
                Enemy("Iron Cleft", 15, 5, 4, GRAY, 35),
                Enemy("Shady Koopa", 10, 4, 2, GREEN, 25),
                Enemy("KP Koopa", 8, 3, 1, YELLOW, 20),
            ]
            self.special_mechanics = ["Fighting Ring", "Ranked Battles"]
        elif self.number == 4:
            # Twilight Town
            self.background_color = (100, 50, 150)
            self.platforms = [
                {'x': 0, 'y': 550, 'width': SCREEN_WIDTH, 'height': 50},
                {'x': 100, 'y': 450, 'width': 150, 'height': 20},
                {'x': 350, 'y': 400, 'width': 200, 'height': 20},
                {'x': 650, 'y': 350, 'width': 150, 'height': 20},
            ]
            self.enemies = [
                Enemy("Hyper Goomba", 12, 5, 1, BROWN, 30),
                Enemy("Crazee Dayzee", 10, 4, 1, YELLOW, 25),
                Enemy("Duplighost", 15, 5, 1, WHITE, 40),
            ]
            self.special_mechanics = ["Bell Tower", "Shadow Curse"]
        elif self.number == 5:
            # Keelhaul Key
            self.background_color = (0, 150, 200)
            self.platforms = [
                {'x': 0, 'y': 520, 'width': SCREEN_WIDTH, 'height': 80},
                {'x': 200, 'y': 420, 'width': 150, 'height': 20},
                {'x': 500, 'y': 370, 'width': 200, 'height': 20},
            ]
            self.enemies = [
                Enemy("Ember", 8, 4, 0, ORANGE, 18),
                Enemy("Bulky Bob-omb", 18, 6, 2, BLACK, 40),
                Enemy("Paratroopa", 10, 4, 1, GREEN, 22),
            ]
            self.special_mechanics = ["Pirate Ship", "Treasure Hunt"]
        elif self.number == 6:
            # Poshley Heights
            self.background_color = (200, 150, 255)
            self.platforms = [
                {'x': 0, 'y': 500, 'width': SCREEN_WIDTH, 'height': 100},
                {'x': 150, 'y': 400, 'width': 200, 'height': 20},
                {'x': 450, 'y': 350, 'width': 150, 'height': 20},
            ]
            self.enemies = [
                Enemy("Dark Boo", 13, 5, 1, DARK_PURPLE, 30),
                Enemy("Chain Chomp", 20, 7, 3, BLACK, 50),
                Enemy("Ice Puff", 11, 4, 1, BLUE, 25),
            ]
            self.special_mechanics = ["Excess Express", "Mystery"]
        elif self.number == 7:
            # Fahr Outpost/Moon
            self.background_color = (20, 20, 60)
            self.platforms = [
                {'x': 0, 'y': 550, 'width': SCREEN_WIDTH, 'height': 50},
                {'x': 100, 'y': 450, 'width': 100, 'height': 20},
                {'x': 300, 'y': 400, 'width': 150, 'height': 20},
                {'x': 550, 'y': 350, 'width': 200, 'height': 20},
            ]
            self.enemies = [
                Enemy("Moon Cleft", 12, 5, 3, GRAY, 35),
                Enemy("Z-Yux", 15, 6, 2, WHITE, 40),
                Enemy("Elite X-Naut", 18, 7, 3, RED, 50),
            ]
            self.special_mechanics = ["X-Naut Fortress", "Moon Base"]
        elif self.number == 8:
            # Palace of Shadow
            self.background_color = (25, 0, 50)
            self.platforms = [
                {'x': 0, 'y': 550, 'width': SCREEN_WIDTH, 'height': 50},
                {'x': 150, 'y': 450, 'width': 150, 'height': 20},
                {'x': 400, 'y': 400, 'width': 100, 'height': 20},
                {'x': 600, 'y': 350, 'width': 150, 'height': 20},
            ]
            self.enemies = [
                Enemy("Dark Wizzerd", 20, 8, 2, DARK_PURPLE, 60),
                Enemy("Phantom Ember", 16, 6, 1, PURPLE, 45),
                Enemy("Swoopula", 14, 5, 1, BLACK, 35),
            ]
            self.boss = Enemy("Shadow Queen", 80, 12, 5, DARK_PURPLE, 500)
            self.special_mechanics = ["Final Boss", "1000-Year Door"]

class Battle:
    """Enhanced battle system with TTYD mechanics"""
    def __init__(self, mario, enemies, partners, audience=None):
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
        
        # TTYD additions
        self.audience = audience or Audience()
        self.stylish_timer = 0
        self.action_commands_succeeded = 0
        self.battle_stage = "normal"  # Can change for special battles
        
    def execute_action(self, action, target_index=0):
        """Execute battle action with enhanced mechanics"""
        success = self.check_action_command()  # TTYD timing mechanic
        
        if action == BattleAction.JUMP:
            if target_index < len(self.enemies):
                damage = self.mario.attack + random.randint(1, 3)
                if success:
                    damage += 2
                    self.audience.increase_excitement(10)
                actual_damage = self.enemies[target_index].take_damage(damage)
                self.battle_log.append(f"Mario jumps on {self.enemies[target_index].name} for {actual_damage} damage!")
                
        elif action == BattleAction.HAMMER and self.mario.has_hammer:
            if target_index < len(self.enemies):
                damage = self.mario.attack + 3 + random.randint(1, 3)
                if success:
                    damage += 3
                    self.audience.increase_excitement(15)
                actual_damage = self.enemies[target_index].take_damage(damage)
                self.battle_log.append(f"Mario hammers {self.enemies[target_index].name} for {actual_damage} damage!")
                
        elif action == BattleAction.STYLISH:
            # TTYD Stylish moves
            self.perform_stylish_move()
            
        elif action == BattleAction.APPEAL:
            # TTYD Appeal to audience
            self.audience.increase_excitement(20)
            self.audience.generate_star_power(10)
            self.battle_log.append("Mario appeals to the audience!")
            
        elif action == BattleAction.PARTNER and self.current_partner:
            if target_index < len(self.enemies):
                damage = self.current_partner.use_ability(self.enemies[target_index])
                if success:
                    damage += 2
                actual_damage = self.enemies[target_index].take_damage(damage)
                self.battle_log.append(f"{self.current_partner.name} attacks for {actual_damage} damage!")
                
        elif action == BattleAction.ITEM:
            heal = 5
            self.mario.hp = min(self.mario.max_hp, self.mario.hp + heal)
            self.battle_log.append(f"Mario uses Mushroom and recovers {heal} HP!")
            
        # Remove defeated enemies
        defeated = [e for e in self.enemies if e.is_defeated()]
        for enemy in defeated:
            self.battle_log.append(f"{enemy.name} is defeated!")
            self.mario.exp += enemy.exp_reward
            self.mario.coins += random.randint(1, 5)
            self.audience.increase_excitement(25)
            self.enemies.remove(enemy)
            
        # Check victory
        if not self.enemies:
            self.victory = True
            self.audience.generate_star_power(50)
            
    def check_action_command(self):
        """TTYD action command timing check"""
        # Simplified - would be more complex with actual timing
        return random.random() < 0.7
        
    def perform_stylish_move(self):
        """TTYD stylish move system"""
        self.stylish_timer = 30
        self.audience.increase_excitement(30)
        self.audience.generate_star_power(20)
        self.battle_log.append("Stylish!")
        
    def enemy_turn(self):
        """Execute enemy turns"""
        for enemy in self.enemies:
            damage = max(1, enemy.attack - self.mario.defense)
            # Superguard chance (TTYD)
            if random.random() < 0.1:
                self.battle_log.append(f"Mario superguards!")
                self.audience.increase_excitement(20)
                damage = 0
            else:
                self.mario.hp -= damage
                self.battle_log.append(f"{enemy.name} attacks Mario for {damage} damage!")
            
            if self.mario.hp <= 0:
                self.defeat = True
                break

class PaperMarioComplete:
    """Main game class combining both games"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("📜 PAPER MARIO COMPLETE COLLECTION 📜")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        # Game state
        self.state = GameState.INTRO
        self.previous_state = None
        self.selected_game = None  # PM64 or TTYD
        
        # Game objects
        self.mario = Mario()
        self.current_chapter = 1
        self.chapters = []
        self.partners = []
        self.current_partner_index = 0
        
        # Battle
        self.current_battle = None
        self.audience = Audience()  # TTYD feature
        
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
        
    def init_chapters(self, game):
        """Initialize chapters based on selected game"""
        chapters = []
        
        if game == "PM64":
            chapter_data = [
                (1, "Goomba Road", "Rescue Goomba Village!"),
                (2, "Koopa Fortress", "Defeat the Koopa Bros!"),
                (3, "Dry Dry Desert", "Find the hidden ruins!"),
                (4, "Shy Guy's Toy Box", "Stop General Guy!"),
                (5, "Lavalava Island", "Calm the volcano!"),
                (6, "Flower Fields", "Save the flower fields!"),
                (7, "Crystal Palace", "Navigate the frozen palace!"),
                (8, "Bowser's Castle", "Final showdown with Bowser!"),
            ]
        else:  # TTYD
            chapter_data = [
                (1, "Rogueport", "Find the first Crystal Star!"),
                (2, "Boggly Woods", "Help the Punies!"),
                (3, "Glitzville", "Become the champion!"),
                (4, "Twilight Town", "Solve the bell curse!"),
                (5, "Keelhaul Key", "Find pirate treasure!"),
                (6, "Poshley Heights", "Mystery on the Express!"),
                (7, "X-Naut Fortress", "To the moon!"),
                (8, "Palace of Shadow", "Stop the Shadow Queen!"),
            ]
            
        for num, name, desc in chapter_data:
            chapter = Chapter(num, name, desc, game)
            chapter.generate_level()
            chapters.append(chapter)
            
        return chapters
        
    def init_partners(self, game):
        """Initialize partners based on selected game"""
        if game == "PM64":
            return [
                Partner("Goombario", BROWN, 10, "Headbonk", "PM64"),
                Partner("Kooper", BLUE, 12, "Shell Toss", "PM64"),
                Partner("Bombette", PINK, 15, "Bomb", "PM64"),
                Partner("Parakarry", YELLOW, 11, "Air Lift", "PM64"),
                Partner("Bow", WHITE, 10, "Spook", "PM64"),
                Partner("Watt", YELLOW, 8, "Electro Dash", "PM64"),
                Partner("Sushie", PURPLE, 14, "Squirt", "PM64"),
                Partner("Lakilester", WHITE, 13, "Spiny Flip", "PM64"),
            ]
        else:  # TTYD
            return [
                Partner("Goombella", BROWN, 12, "Headbonk", "TTYD"),
                Partner("Koops", GREEN, 15, "Shell Shield", "TTYD"),
                Partner("Flurrie", PINK, 18, "Gale Force", "TTYD"),
                Partner("Yoshi", GREEN, 10, "Ground Pound", "TTYD"),
                Partner("Vivian", PURPLE, 15, "Shade Fist", "TTYD"),
                Partner("Bobbery", BLACK, 20, "Bomb Squad", "TTYD"),
                Partner("Ms. Mowz", WHITE, 12, "Kiss Thief", "TTYD"),
            ]
        
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.INTRO:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.GAME_SELECT
                        
                elif self.state == GameState.GAME_SELECT:
                    if event.key == pygame.K_1:
                        self.selected_game = "PM64"
                        self.chapters = self.init_chapters("PM64")
                        self.partners = self.init_partners("PM64")
                        self.state = GameState.OVERWORLD
                    elif event.key == pygame.K_2:
                        self.selected_game = "TTYD"
                        self.chapters = self.init_chapters("TTYD")
                        self.partners = self.init_partners("TTYD")
                        self.state = GameState.OVERWORLD
                        
                elif self.state == GameState.OVERWORLD:
                    if event.key == pygame.K_LEFT:
                        self.mario.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.mario.move_right()
                    elif event.key == pygame.K_SPACE:
                        self.mario.jump()
                    elif event.key == pygame.K_b:
                        if self.chapters[self.current_chapter - 1].enemies:
                            self.start_battle()
                    elif event.key == pygame.K_p:
                        self.current_partner_index = (self.current_partner_index + 1) % len(self.partners)
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
                    # TTYD paper modes
                    elif event.key == pygame.K_1 and self.selected_game == "TTYD":
                        self.mario.switch_paper_mode(PaperMode.PLANE)
                    elif event.key == pygame.K_2 and self.selected_game == "TTYD":
                        self.mario.switch_paper_mode(PaperMode.TUBE)
                    elif event.key == pygame.K_3 and self.selected_game == "TTYD":
                        self.mario.switch_paper_mode(PaperMode.THIN)
                    elif event.key == pygame.K_0:
                        self.mario.switch_paper_mode(PaperMode.NORMAL)
                        
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
                        self.state = GameState.OVERWORLD
                        self.current_battle = None
                    # TTYD battle options
                    elif event.key == pygame.K_6 and self.selected_game == "TTYD":
                        self.current_battle.execute_action(BattleAction.STYLISH)
                        self.current_battle.turn = "enemy"
                    elif event.key == pygame.K_7 and self.selected_game == "TTYD":
                        self.current_battle.execute_action(BattleAction.APPEAL)
                        self.current_battle.turn = "enemy"
                        
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
            num_enemies = min(3, len(chapter.enemies))
            battle_enemies = random.sample(chapter.enemies, num_enemies)
            
            if self.selected_game == "TTYD":
                self.current_battle = Battle(self.mario, battle_enemies, 
                                           [self.partners[self.current_partner_index]], 
                                           self.audience)
            else:
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
            if self.selected_game == "PM64":
                self.mario.star_points += 1
            else:
                self.mario.crystal_stars.append(f"Crystal Star {self.current_chapter}")
                
            self.mario.level_up()
            
            # New abilities
            if self.current_chapter == 2:
                self.mario.has_hammer = True
                self.show_dialogue("New Ability!", "You got the Hammer!")
            elif self.current_chapter == 4 and self.selected_game == "TTYD":
                self.mario.has_spin_jump = True
                self.show_dialogue("New Ability!", "You got the Spin Jump!")
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
            chapter = self.chapters[self.current_chapter - 1]
            self.mario.update(chapter.platforms)
            
            # Check if chapter is complete
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
                
                if self.current_battle.turn == "enemy" and self.current_battle.action_timer > 60:
                    self.current_battle.enemy_turn()
                    self.current_battle.turn = "player"
                    self.current_battle.action_timer = 0
                    
                if self.current_battle.victory:
                    self.state = GameState.OVERWORLD
                    self.current_battle = None
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
        title = "PAPER MARIO"
        title2 = "COMPLETE COLLECTION"
        
        # Draw with paper effect
        for i in range(3):
            offset = i * 2
            shadow_surface = self.font_large.render(title, True, (100 - i*20, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(SCREEN_WIDTH//2 + offset, title_y + offset))
            self.screen.blit(shadow_surface, shadow_rect)
            
        title_surface = self.font_large.render(title, True, RED)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, title_y))
        self.screen.blit(title_surface, title_rect)
        
        title2_surface = self.font_medium.render(title2, True, GOLD)
        title2_rect = title2_surface.get_rect(center=(SCREEN_WIDTH//2, title_y + 80))
        self.screen.blit(title2_surface, title2_rect)
        
        # Features
        features = "16 CHAPTERS • 2 GAMES • 1 ADVENTURE"
        feat_surface = self.font_small.render(features, True, WHITE)
        feat_rect = feat_surface.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(feat_surface, feat_rect)
        
        # Start prompt
        if self.intro_timer % 60 < 40:
            start_text = "PRESS SPACE TO START"
            start_surface = self.font_small.render(start_text, True, YELLOW)
            start_rect = start_surface.get_rect(center=(SCREEN_WIDTH//2, 400))
            self.screen.blit(start_surface, start_rect)
            
    def draw_game_select(self):
        """Draw game selection screen"""
        self.screen.fill(BLACK)
        
        title = "SELECT YOUR ADVENTURE"
        title_surface = self.font_large.render(title, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # PM64 Box
        pm64_rect = pygame.Rect(100, 200, 350, 400)
        pygame.draw.rect(self.screen, RED, pm64_rect)
        pygame.draw.rect(self.screen, WHITE, pm64_rect, 3)
        
        pm64_title = "PAPER MARIO 64"
        pm64_surface = self.font_medium.render(pm64_title, True, WHITE)
        pm64_rect = pm64_surface.get_rect(center=(275, 250))
        self.screen.blit(pm64_surface, pm64_rect)
        
        pm64_features = [
            "8 Classic Chapters",
            "Star Spirits",
            "Original Partners",
            "Bowser's Castle"
        ]
        for i, feature in enumerate(pm64_features):
            feat_surface = self.font_small.render(f"• {feature}", True, WHITE)
            self.screen.blit(feat_surface, (130, 320 + i * 40))
            
        press1 = "Press 1"
        press1_surface = self.font_medium.render(press1, True, YELLOW)
        press1_rect = press1_surface.get_rect(center=(275, 550))
        self.screen.blit(press1_surface, press1_rect)
        
        # TTYD Box
        ttyd_rect = pygame.Rect(550, 200, 350, 400)
        pygame.draw.rect(self.screen, DARK_PURPLE, ttyd_rect)
        pygame.draw.rect(self.screen, GOLD, ttyd_rect, 3)
        
        ttyd_title = "THOUSAND-YEAR DOOR"
        ttyd_surface = self.font_medium.render(ttyd_title, True, WHITE)
        ttyd_rect = ttyd_surface.get_rect(center=(725, 250))
        self.screen.blit(ttyd_surface, ttyd_rect)
        
        ttyd_features = [
            "8 New Chapters",
            "Crystal Stars",
            "Paper Abilities",
            "Audience System"
        ]
        for i, feature in enumerate(ttyd_features):
            feat_surface = self.font_small.render(f"• {feature}", True, WHITE)
            self.screen.blit(feat_surface, (580, 320 + i * 40))
            
        press2 = "Press 2"
        press2_surface = self.font_medium.render(press2, True, YELLOW)
        press2_rect = press2_surface.get_rect(center=(725, 550))
        self.screen.blit(press2_surface, press2_rect)
        
    def draw_overworld(self):
        """Draw overworld"""
        if not self.chapters:
            return
            
        chapter = self.chapters[self.current_chapter - 1]
        
        # Background
        self.screen.fill(chapter.background_color)
        
        # Draw platforms
        for platform in chapter.platforms:
            pygame.draw.rect(self.screen, BROWN, 
                           (platform['x'], platform['y'], 
                            platform['width'], platform['height']))
            pygame.draw.rect(self.screen, BLACK, 
                           (platform['x'], platform['y'], 
                            platform['width'], platform['height']), 2)
                            
        # Draw Mario
        self.mario.draw(self.screen)
        
        # Draw partner
        if self.partners and self.current_partner_index < len(self.partners):
            partner = self.partners[self.current_partner_index]
            partner_x = self.mario.x - 60
            partner_y = self.mario.y + 20
            pygame.draw.circle(self.screen, partner.color, 
                             (partner_x + 20, partner_y + 10), 15)
            name_surface = self.font_tiny.render(partner.name, True, WHITE)
            self.screen.blit(name_surface, (partner_x, partner_y - 20))
            
        # Draw HUD
        self.draw_hud()
        
        # Chapter info
        game_label = f"[{self.selected_game}]" if self.selected_game else ""
        chapter_text = f"{game_label} Chapter {chapter.number}: {chapter.name}"
        chapter_surface = self.font_medium.render(chapter_text, True, WHITE)
        self.screen.blit(chapter_surface, (20, 20))
        
        # TTYD special mechanics indicator
        if self.selected_game == "TTYD" and chapter.special_mechanics:
            for i, mechanic in enumerate(chapter.special_mechanics):
                mech_surface = self.font_tiny.render(f"★ {mechanic}", True, GOLD)
                self.screen.blit(mech_surface, (20, 70 + i * 25))
                
    def draw_battle(self):
        """Draw enhanced battle screen"""
        if not self.current_battle:
            return
            
        # Battle background
        self.screen.fill((100, 100, 150))
        
        # Draw audience for TTYD
        if self.selected_game == "TTYD":
            self.draw_audience()
            
        # Stage
        pygame.draw.rect(self.screen, BROWN, 
                        (50, 400, SCREEN_WIDTH - 100, 200))
        pygame.draw.rect(self.screen, BLACK, 
                        (50, 400, SCREEN_WIDTH - 100, 200), 3)
                        
        # Draw Mario
        mario_x = 200
        mario_y = 450
        pygame.draw.rect(self.screen, RED, (mario_x, mario_y + 20, 40, 30))
        pygame.draw.rect(self.screen, BLUE, (mario_x, mario_y + 35, 40, 25))
        pygame.draw.circle(self.screen, (255, 220, 177), 
                          (mario_x + 20, mario_y + 15), 15)
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
            name_surface = self.font_tiny.render(enemy.name, True, WHITE)
            self.screen.blit(name_surface, (enemy_x, enemy_y - 40))
            
        # Draw action menu
        self.draw_battle_menu()
        
        # Battle log
        log_y = 250
        for i, message in enumerate(self.current_battle.battle_log[-3:]):
            log_surface = self.font_tiny.render(message, True, YELLOW)
            self.screen.blit(log_surface, (400, log_y + i * 25))
            
        # Stats
        self.draw_battle_stats()
        
    def draw_battle_menu(self):
        """Draw battle action menu"""
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
        
        if self.selected_game == "TTYD":
            actions.extend([
                "6 - Stylish",
                "7 - Appeal"
            ])
            
        for i, action in enumerate(actions):
            action_surface = self.font_small.render(action, True, WHITE)
            self.screen.blit(action_surface, (50, menu_y + 50 + i * 30))
            
    def draw_audience(self):
        """Draw TTYD audience"""
        audience_y = 650
        
        # Audience meter
        pygame.draw.rect(self.screen, BLACK, (50, audience_y, 200, 30))
        pygame.draw.rect(self.screen, WHITE, (50, audience_y, 200, 30), 2)
        
        # Fill based on audience size
        fill_width = int((self.audience.size / self.audience.max_size) * 200)
        pygame.draw.rect(self.screen, GOLD, (50, audience_y, fill_width, 30))
        
        aud_text = f"Audience: {self.audience.size}"
        aud_surface = self.font_tiny.render(aud_text, True, WHITE)
        self.screen.blit(aud_surface, (55, audience_y + 5))
        
        # Star Power meter
        sp_y = audience_y + 40
        pygame.draw.rect(self.screen, BLACK, (50, sp_y, 200, 20))
        pygame.draw.rect(self.screen, YELLOW, (50, sp_y, 200, 20), 2)
        
        sp_fill = int((self.audience.star_power / self.audience.max_star_power) * 200)
        pygame.draw.rect(self.screen, YELLOW, (50, sp_y, sp_fill, 20))
        
        sp_text = f"Star Power: {self.audience.star_power}%"
        sp_surface = self.font_tiny.render(sp_text, True, BLACK)
        self.screen.blit(sp_surface, (55, sp_y + 2))
        
    def draw_battle_stats(self):
        """Draw battle statistics"""
        stats_x = 50
        stats_y = 500
        
        hp_text = f"HP: {self.mario.hp}/{self.mario.max_hp}"
        hp_surface = self.font_small.render(hp_text, True, WHITE)
        self.screen.blit(hp_surface, (stats_x, stats_y))
        
        fp_text = f"FP: {self.mario.fp}/{self.mario.max_fp}"
        fp_surface = self.font_small.render(fp_text, True, BLUE)
        self.screen.blit(fp_surface, (stats_x, stats_y + 30))
        
        if self.selected_game == "TTYD":
            bp_text = f"BP: {self.mario.bp}/{self.mario.max_bp}"
            bp_surface = self.font_small.render(bp_text, True, GREEN)
            self.screen.blit(bp_surface, (stats_x, stats_y + 60))
            
        # Partner HP
        if self.current_battle.current_partner:
            partner = self.current_battle.current_partner
            partner_hp = f"{partner.name}: {partner.hp}/{partner.max_hp}"
            partner_surface = self.font_small.render(partner_hp, True, partner.color)
            self.screen.blit(partner_surface, (stats_x + 200, stats_y))
            
    def draw_hud(self):
        """Draw HUD overlay"""
        # HP/FP bar background
        hud_height = 100 if self.selected_game == "TTYD" else 80
        pygame.draw.rect(self.screen, BLACK, (10, SCREEN_HEIGHT - hud_height, 250, hud_height))
        pygame.draw.rect(self.screen, WHITE, (10, SCREEN_HEIGHT - hud_height, 250, hud_height), 2)
        
        # HP
        hp_percent = self.mario.hp / self.mario.max_hp
        pygame.draw.rect(self.screen, RED, (20, SCREEN_HEIGHT - hud_height + 10, 180, 20))
        pygame.draw.rect(self.screen, GREEN, 
                        (20, SCREEN_HEIGHT - hud_height + 10, int(180 * hp_percent), 20))
        hp_text = f"HP: {self.mario.hp}/{self.mario.max_hp}"
        hp_surface = self.font_tiny.render(hp_text, True, WHITE)
        self.screen.blit(hp_surface, (25, SCREEN_HEIGHT - hud_height + 12))
        
        # FP
        fp_percent = self.mario.fp / self.mario.max_fp
        pygame.draw.rect(self.screen, BLUE, (20, SCREEN_HEIGHT - hud_height + 35, 180, 20))
        pygame.draw.rect(self.screen, (0, 150, 255), 
                        (20, SCREEN_HEIGHT - hud_height + 35, int(180 * fp_percent), 20))
        fp_text = f"FP: {self.mario.fp}/{self.mario.max_fp}"
        fp_surface = self.font_tiny.render(fp_text, True, WHITE)
        self.screen.blit(fp_surface, (25, SCREEN_HEIGHT - hud_height + 37))
        
        # BP for TTYD
        if self.selected_game == "TTYD":
            bp_percent = self.mario.bp / self.mario.max_bp
            pygame.draw.rect(self.screen, GREEN, (20, SCREEN_HEIGHT - 35, 180, 20))
            pygame.draw.rect(self.screen, (0, 200, 0), 
                            (20, SCREEN_HEIGHT - 35, int(180 * bp_percent), 20))
            bp_text = f"BP: {self.mario.bp}/{self.mario.max_bp}"
            bp_surface = self.font_tiny.render(bp_text, True, WHITE)
            self.screen.blit(bp_surface, (25, SCREEN_HEIGHT - 33))
            
        # Stats
        level_text = f"Lv: {self.mario.level}"
        level_surface = self.font_small.render(level_text, True, WHITE)
        self.screen.blit(level_surface, (270, SCREEN_HEIGHT - hud_height + 10))
        
        coins_text = f"Coins: {self.mario.coins}"
        coins_surface = self.font_tiny.render(coins_text, True, YELLOW)
        self.screen.blit(coins_surface, (270, SCREEN_HEIGHT - hud_height + 40))
        
        if self.selected_game == "PM64":
            star_text = f"★ {self.mario.star_points}"
        else:
            star_text = f"✦ {len(self.mario.crystal_stars)}"
        star_surface = self.font_small.render(star_text, True, YELLOW)
        self.screen.blit(star_surface, (370, SCREEN_HEIGHT - hud_height + 10))
        
    def draw_chapter_complete(self):
        """Draw chapter complete screen"""
        self.screen.fill(BLACK)
        
        # Star/Crystal animation
        star_y = 200 + math.sin(self.intro_timer * 0.1) * 20
        if self.selected_game == "PM64":
            self.draw_star(SCREEN_WIDTH//2, star_y, 50, YELLOW)
            reward_text = "You got a Star Spirit!"
        else:
            self.draw_crystal_star(SCREEN_WIDTH//2, star_y, 50)
            reward_text = "You got a Crystal Star!"
            
        # Text
        complete_text = f"Chapter {self.current_chapter} Complete!"
        complete_surface = self.font_large.render(complete_text, True, WHITE)
        complete_rect = complete_surface.get_rect(center=(SCREEN_WIDTH//2, 350))
        self.screen.blit(complete_surface, complete_rect)
        
        rewards_surface = self.font_medium.render(reward_text, True, YELLOW)
        rewards_rect = rewards_surface.get_rect(center=(SCREEN_WIDTH//2, 420))
        self.screen.blit(rewards_surface, rewards_rect)
        
        cont_text = "Press SPACE to continue"
        cont_surface = self.font_small.render(cont_text, True, WHITE)
        cont_rect = cont_surface.get_rect(center=(SCREEN_WIDTH//2, 500))
        self.screen.blit(cont_surface, cont_rect)
        
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
        
    def draw_crystal_star(self, x, y, size):
        """Draw TTYD crystal star"""
        # Draw as multi-colored crystal
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK]
        for i in range(7):
            angle = (math.pi * 2 * i / 7) + self.intro_timer * 0.05
            px = x + math.cos(angle) * size
            py = y + math.sin(angle) * size
            pygame.draw.polygon(self.screen, colors[i], 
                              [(x, y), (px - 10, py), (px + 10, py)])
                              
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.intro_timer += 1
            
            # Draw based on state
            if self.state == GameState.INTRO:
                self.draw_intro()
            elif self.state == GameState.GAME_SELECT:
                self.draw_game_select()
            elif self.state == GameState.OVERWORLD:
                self.draw_overworld()
            elif self.state == GameState.BATTLE:
                self.draw_battle()
            elif self.state == GameState.CHAPTER_COMPLETE:
                self.draw_chapter_complete()
            elif self.state == GameState.GAME_OVER:
                self.screen.fill(BLACK)
                go_text = "GAME OVER"
                go_surface = self.font_large.render(go_text, True, RED)
                go_rect = go_surface.get_rect(center=(SCREEN_WIDTH//2, 300))
                self.screen.blit(go_surface, go_rect)
                
                restart_text = "Press R to restart"
                restart_surface = self.font_medium.render(restart_text, True, WHITE)
                restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH//2, 400))
                self.screen.blit(restart_surface, restart_rect)
            elif self.state == GameState.VICTORY:
                self.screen.fill(BLACK)
                colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
                victory_text = "VICTORY!"
                for i, char in enumerate(victory_text):
                    color = colors[(self.intro_timer // 10 + i) % len(colors)]
                    char_surface = self.font_large.render(char, True, color)
                    x = SCREEN_WIDTH//2 - 150 + i * 40
                    y = 200 + math.sin(self.intro_timer * 0.1 + i) * 20
                    self.screen.blit(char_surface, (x, y))
                    
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

# Run the game
if __name__ == "__main__":
    print("🌟 PAPER MARIO COMPLETE COLLECTION 🌟")
    print("=" * 50)
    print("FEATURING:")
    print("  • PAPER MARIO 64 - 8 Classic Chapters")
    print("  • THE THOUSAND-YEAR DOOR - 8 New Chapters")
    print("  • 16 Total Chapters!")
    print("  • Enhanced Battle System")
    print("  • Paper Transformations")
    print("  • Audience System")
    print("\nCONTROLS:")
    print("  Arrow Keys - Move")
    print("  SPACE - Jump/Confirm")
    print("  M - Menu")
    print("  P - Switch Partner")
    print("  B - Start Battle")
    print("\nTTYD PAPER MODES:")
    print("  1 - Plane Mode")
    print("  2 - Tube Mode")
    print("  3 - Thin Mode")
    print("  0 - Normal Mode")
    print("=" * 50)
    print("Starting game...")
    
    game = PaperMarioComplete()
    game.run()
