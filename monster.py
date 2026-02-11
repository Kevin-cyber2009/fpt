import pygame
import math
import random

class Monster:
    def __init__(self, x, y, monster_type='titan_bot'):
        self.x = x
        self.y = y
        self.hp = 100
        self.max_hp = 100
        self.monster_type = monster_type
        
        # Animation
        self.idle_offset = 0
        self.breath_cycle = 0
        
        # Body part positions
        self.parts = {
            'head': {'x': 0, 'y': -120, 'width': 120, 'height': 140},
            'body': {'x': 0, 'y': 0, 'width': 100, 'height': 120},
            'left_arm': {'x': -100, 'y': 10, 'width': 40, 'height': 100},
            'right_arm': {'x': 100, 'y': 10, 'width': 40, 'height': 100},
            'left_leg': {'x': -30, 'y': 120, 'width': 35, 'height': 110},
            'right_leg': {'x': 30, 'y': 120, 'width': 35, 'height': 110}
        }
        
        # Robot color schemes - ALL ROBOTS
        self.color_schemes = {
            'titan_bot': {  # Massive heavy tank robot
                'primary': (80, 90, 120),
                'secondary': (100, 110, 150),
                'dark': (40, 50, 80),
                'accent': (255, 150, 0),
                'glow': (255, 200, 50)
            },
            'stealth_bot': {  # Sleek assassin robot
                'primary': (60, 60, 70),
                'secondary': (80, 80, 90),
                'dark': (30, 30, 40),
                'accent': (0, 255, 150),
                'glow': (50, 255, 200)
            },
            'plasma_bot': {  # Energy-based robot
                'primary': (100, 50, 150),
                'secondary': (130, 70, 180),
                'dark': (60, 30, 90),
                'accent': (200, 0, 255),
                'glow': (255, 100, 255)
            },
            'war_bot': {  # Military combat robot
                'primary': (90, 100, 70),
                'secondary': (110, 130, 90),
                'dark': (50, 60, 40),
                'accent': (255, 50, 50),
                'glow': (255, 100, 50)
            },
            'nano_bot': {  # Small tech advanced robot
                'primary': (120, 150, 180),
                'secondary': (150, 180, 210),
                'dark': (70, 90, 110),
                'accent': (0, 200, 255),
                'glow': (100, 220, 255)
            },
            'mech_bot': {  # Industrial worker robot
                'primary': (150, 120, 80),
                'secondary': (180, 150, 100),
                'dark': (90, 70, 50),
                'accent': (255, 200, 0),
                'glow': (255, 220, 100)
            },
            'cyber_bot': {  # Futuristic cyber robot
                'primary': (50, 100, 100),
                'secondary': (70, 130, 130),
                'dark': (30, 60, 60),
                'accent': (0, 255, 255),
                'glow': (100, 255, 255)
            }
        }
        
        self.colors = self.color_schemes.get(monster_type, self.color_schemes['titan_bot'])
    
    def clamp_color(self, color):
        """Clamp color values to valid range 0-255"""
        return tuple(min(255, max(0, int(c))) for c in color)
    
    def reset(self):
        self.hp = self.max_hp
        self.idle_offset = 0
        self.breath_cycle = 0
    
    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
    
    def update_animation(self, dt):
        self.idle_offset = math.sin(pygame.time.get_ticks() / 500) * 5
        self.breath_cycle = (pygame.time.get_ticks() / 1000) % (2 * math.pi)
    
    def get_clicked_part(self, mouse_x, mouse_y):
        for part_name, part_data in self.parts.items():
            part_x = self.x + part_data['x']
            part_y = self.y + part_data['y'] + self.idle_offset
            
            half_w = part_data['width'] / 2
            half_h = part_data['height'] / 2
            if (part_x - half_w <= mouse_x <= part_x + half_w and
                part_y - half_h <= mouse_y <= part_y + half_h):
                return part_name
        return None
    
    def draw(self, screen, highlighted_part=None):
        self.update_animation(0.016)
        
        if self.monster_type == 'titan_bot':
            self.draw_titan_bot(screen, highlighted_part)
        elif self.monster_type == 'stealth_bot':
            self.draw_stealth_bot(screen, highlighted_part)
        elif self.monster_type == 'plasma_bot':
            self.draw_plasma_bot(screen, highlighted_part)
        elif self.monster_type == 'war_bot':
            self.draw_war_bot(screen, highlighted_part)
        elif self.monster_type == 'nano_bot':
            self.draw_nano_bot(screen, highlighted_part)
        elif self.monster_type == 'mech_bot':
            self.draw_mech_bot(screen, highlighted_part)
        elif self.monster_type == 'cyber_bot':
            self.draw_cyber_bot(screen, highlighted_part)
    
    def draw_titan_bot(self, screen, highlighted_part):
        """Massive tank robot - boxy, heavy armor"""
        y_offset = self.idle_offset
        
        # Shadow
        shadow = pygame.Surface((240, 50), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), (0, 0, 240, 50), border_radius=25)
        screen.blit(shadow, (self.x - 120, self.y + 250))
        
        # === LEGS - Tank treads ===
        for leg_name in ['left_leg', 'right_leg']:
            part = self.parts[leg_name]
            color = self.colors['accent'] if highlighted_part == leg_name else self.colors['primary']
            
            leg_x = self.x + part['x']
            leg_y = self.y + part['y'] + y_offset
            
            # Main leg structure
            leg_rect = pygame.Rect(leg_x - 25, leg_y - 55, 50, 110)
            pygame.draw.rect(screen, color, leg_rect, border_radius=8)
            pygame.draw.rect(screen, self.colors['dark'], leg_rect, 4, border_radius=8)
            
            # Tread segments
            for i in range(5):
                seg_y = leg_rect.top + 10 + i * 20
                pygame.draw.rect(screen, self.colors['dark'],
                               (leg_rect.left + 5, seg_y, leg_rect.width - 10, 14),
                               border_radius=3)
                pygame.draw.rect(screen, self.colors['secondary'],
                               (leg_rect.left + 8, seg_y + 3, leg_rect.width - 16, 8))
            
            # Hydraulic pistons
            pygame.draw.rect(screen, (150, 150, 170),
                           (leg_rect.centerx - 6, leg_rect.top - 20, 12, 25))
        
        # === BODY - Armored chassis ===
        part = self.parts['body']
        color = self.colors['accent'] if highlighted_part == 'body' else self.colors['secondary']
        body_rect = pygame.Rect(
            self.x + part['x'] - 70,
            self.y + part['y'] - 60 + y_offset,
            140, 120
        )
        
        # Main body
        pygame.draw.rect(screen, color, body_rect, border_radius=10)
        pygame.draw.rect(screen, self.colors['dark'], body_rect, 5, border_radius=10)
        
        # Armor plates
        for i in range(3):
            plate_y = body_rect.top + 15 + i * 35
            pygame.draw.rect(screen, self.colors['primary'],
                           (body_rect.left + 10, plate_y, body_rect.width - 20, 28),
                           border_radius=5)
            pygame.draw.rect(screen, self.colors['dark'],
                           (body_rect.left + 10, plate_y, body_rect.width - 20, 28),
                           2, border_radius=5)
            
            # Bolts
            for bx in [body_rect.left + 20, body_rect.right - 20]:
                pygame.draw.rect(screen, (100, 100, 120),
                               (bx - 4, plate_y + 10, 8, 8))
        
        # === ARMS - Heavy cannons ===
        for arm_name in ['left_arm', 'right_arm']:
            part = self.parts[arm_name]
            color = self.colors['accent'] if highlighted_part == arm_name else self.colors['primary']
            
            arm_x = self.x + part['x']
            arm_y = self.y + part['y'] + y_offset
            is_left = 'left' in arm_name
            
            # Shoulder mount
            shoulder = pygame.Rect(arm_x - 25, arm_y - 50, 50, 40)
            pygame.draw.rect(screen, color, shoulder, border_radius=8)
            pygame.draw.rect(screen, self.colors['dark'], shoulder, 3, border_radius=8)
            
            # Cannon barrel
            barrel_width = 35
            barrel_length = 80
            barrel_x = arm_x - barrel_width//2
            barrel_y = arm_y - 10
            
            barrel_rect = pygame.Rect(barrel_x, barrel_y, barrel_width, barrel_length)
            pygame.draw.rect(screen, self.colors['dark'], barrel_rect, border_radius=6)
            
            # Barrel segments
            for seg in range(3):
                seg_y = barrel_y + 10 + seg * 22
                pygame.draw.rect(screen, self.colors['secondary'],
                               (barrel_x + 3, seg_y, barrel_width - 6, 18))
                pygame.draw.line(screen, self.colors['primary'],
                               (barrel_x + 5, seg_y + 9),
                               (barrel_x + barrel_width - 5, seg_y + 9), 2)
            
            # Barrel tip
            tip_rect = pygame.Rect(barrel_x - 2, barrel_y + barrel_length - 8,
                                  barrel_width + 4, 15)
            pygame.draw.rect(screen, (50, 50, 60), tip_rect, border_radius=4)
        
        # === HEAD - Command center ===
        part = self.parts['head']
        color = self.colors['accent'] if highlighted_part == 'head' else self.colors['primary']
        
        head_rect = pygame.Rect(
            self.x + part['x'] - 60,
            self.y + part['y'] - 70 + y_offset,
            120, 140
        )
        
        # Main head (hexagonal-ish)
        head_points = [
            (head_rect.centerx, head_rect.top),
            (head_rect.right - 10, head_rect.top + 30),
            (head_rect.right - 10, head_rect.bottom - 30),
            (head_rect.centerx, head_rect.bottom),
            (head_rect.left + 10, head_rect.bottom - 30),
            (head_rect.left + 10, head_rect.top + 30)
        ]
        pygame.draw.polygon(screen, color, head_points)
        pygame.draw.polygon(screen, self.colors['dark'], head_points, 4)
        
        # Visor (glowing)
        visor_y = head_rect.centery - 10
        visor_rect = pygame.Rect(head_rect.left + 20, visor_y, head_rect.width - 40, 35)
        
        # Visor glow
        glow_color = self.colors['glow']
        for i in range(3):
            glow_rect = visor_rect.inflate(6 - i*2, 4 - i*2)
            alpha = 80 - i * 25
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*glow_color, alpha), (0, 0, glow_rect.width, glow_rect.height))
            screen.blit(glow_surf, glow_rect.topleft)
        
        pygame.draw.rect(screen, self.colors['glow'], visor_rect)
        pygame.draw.rect(screen, self.colors['accent'], visor_rect, 2)
        
        # Visor segments
        for i in range(3):
            seg_x = visor_rect.left + 10 + i * 25
            pygame.draw.rect(screen, (255, 255, 200),
                           (seg_x, visor_rect.top + 8, 18, 20))
        
        # Antenna
        antenna_base = (head_rect.centerx, head_rect.top)
        antenna_tip = (head_rect.centerx, head_rect.top - 30)
        pygame.draw.line(screen, (150, 150, 170), antenna_base, antenna_tip, 5)
        
        # Antenna light
        blink = int(pygame.time.get_ticks() / 400) % 2
        light_color = (255, 0, 0) if blink else (100, 0, 0)
        pygame.draw.polygon(screen, light_color, [
            (antenna_tip[0], antenna_tip[1]),
            (antenna_tip[0] - 8, antenna_tip[1] - 12),
            (antenna_tip[0] + 8, antenna_tip[1] - 12)
        ])
    
    def draw_stealth_bot(self, screen, highlighted_part):
        """Sleek assassin robot - angular, sharp edges"""
        y_offset = self.idle_offset
        
        # Minimal shadow
        shadow = pygame.Surface((180, 35), pygame.SRCALPHA)
        pygame.draw.polygon(shadow, (0, 0, 0, 70), [(0, 17), (90, 0), (180, 17), (90, 35)])
        screen.blit(shadow, (self.x - 90, self.y + 250))
        
        # === LEGS - Blade-like ===
        for leg_name in ['left_leg', 'right_leg']:
            part = self.parts[leg_name]
            color = self.colors['accent'] if highlighted_part == leg_name else self.colors['primary']
            
            leg_x = self.x + part['x']
            leg_y = self.y + part['y'] + y_offset
            
            # Upper leg (trapezoid)
            upper_points = [
                (leg_x - 20, leg_y - 55),
                (leg_x + 20, leg_y - 55),
                (leg_x + 15, leg_y),
                (leg_x - 15, leg_y)
            ]
            pygame.draw.polygon(screen, color, upper_points)
            pygame.draw.polygon(screen, self.colors['accent'], upper_points, 2)
            
            # Lower leg (narrow blade)
            lower_points = [
                (leg_x - 12, leg_y),
                (leg_x + 12, leg_y),
                (leg_x + 8, leg_y + 55),
                (leg_x - 8, leg_y + 55)
            ]
            pygame.draw.polygon(screen, self.colors['dark'], lower_points)
            pygame.draw.polygon(screen, self.colors['accent'], lower_points, 2)
            
            # Knee joint (diamond)
            knee_points = [
                (leg_x, leg_y - 8),
                (leg_x + 12, leg_y),
                (leg_x, leg_y + 8),
                (leg_x - 12, leg_y)
            ]
            pygame.draw.polygon(screen, (150, 150, 160), knee_points)
        
        # === BODY - Sleek chassis ===
        part = self.parts['body']
        color = self.colors['accent'] if highlighted_part == 'body' else self.colors['secondary']
        
        body_points = [
            (self.x - 50, self.y - 50 + y_offset),
            (self.x + 50, self.y - 50 + y_offset),
            (self.x + 40, self.y + 60 + y_offset),
            (self.x - 40, self.y + 60 + y_offset)
        ]
        pygame.draw.polygon(screen, color, body_points)
        pygame.draw.polygon(screen, self.colors['dark'], body_points, 3)
        
        # Energy core (glowing lines)
        core_x = self.x
        core_y = self.y + 5 + y_offset
        
        for i in range(3):
            line_y = core_y - 20 + i * 20
            glow_intensity = int(abs(math.sin(pygame.time.get_ticks() / 300 + i)) * 155 + 100)
            glow_color = self.clamp_color((0, glow_intensity, glow_intensity + 50))
            pygame.draw.line(screen, glow_color,
                           (core_x - 30, line_y),
                           (core_x + 30, line_y), 4)
        
        # === ARMS - Blade weapons ===
        for arm_name in ['left_arm', 'right_arm']:
            part = self.parts[arm_name]
            color = self.colors['accent'] if highlighted_part == arm_name else self.colors['primary']
            
            arm_x = self.x + part['x']
            arm_y = self.y + part['y'] + y_offset
            
            # Upper arm
            upper_arm = [
                (arm_x - 18, arm_y - 50),
                (arm_x + 18, arm_y - 50),
                (arm_x + 14, arm_y + 20),
                (arm_x - 14, arm_y + 20)
            ]
            pygame.draw.polygon(screen, color, upper_arm)
            pygame.draw.polygon(screen, self.colors['accent'], upper_arm, 2)
            
            # Blade (energy sword)
            blade_points = [
                (arm_x - 8, arm_y + 20),
                (arm_x + 8, arm_y + 20),
                (arm_x + 5, arm_y + 70),
                (arm_x, arm_y + 85),
                (arm_x - 5, arm_y + 70)
            ]
            
            # Blade glow
            for i in range(2):
                glow_points = [(p[0] + (2-i)*2 if p[0] < arm_x else p[0] - (2-i)*2, p[1]) 
                              for p in blade_points]
                alpha = 100 - i * 40
                blade_surf = pygame.Surface((150, 150), pygame.SRCALPHA)
                pygame.draw.polygon(blade_surf, (*self.colors['glow'], alpha), 
                                  [(p[0] - arm_x + 75, p[1] - arm_y + 25) for p in glow_points])
                screen.blit(blade_surf, (arm_x - 75, arm_y - 25))
            
            pygame.draw.polygon(screen, self.colors['glow'], blade_points)
            pygame.draw.polygon(screen, (200, 255, 255), blade_points, 2)
        
        # === HEAD - Sleek helmet ===
        part = self.parts['head']
        color = self.colors['accent'] if highlighted_part == 'head' else self.colors['primary']
        
        head_x = self.x
        head_y = self.y - 120 + y_offset
        
        # Main head (sharp angles)
        head_points = [
            (head_x, head_y - 60),
            (head_x + 45, head_y - 30),
            (head_x + 40, head_y + 40),
            (head_x - 40, head_y + 40),
            (head_x - 45, head_y - 30)
        ]
        pygame.draw.polygon(screen, color, head_points)
        pygame.draw.polygon(screen, self.colors['dark'], head_points, 3)
        
        # Visor (single glowing slit)
        visor_y = head_y - 10
        visor_points = [
            (head_x - 35, visor_y),
            (head_x + 35, visor_y),
            (head_x + 30, visor_y + 8),
            (head_x - 30, visor_y + 8)
        ]
        
        # Visor glow
        for i in range(2):
            glow_surf = pygame.Surface((80, 20), pygame.SRCALPHA)
            alpha = 120 - i * 50
            pygame.draw.polygon(glow_surf, (*self.colors['glow'], alpha), 
                              [(p[0] - head_x + 40, p[1] - visor_y + 5) for p in visor_points])
            screen.blit(glow_surf, (head_x - 40, visor_y - 5))
        
        pygame.draw.polygon(screen, self.colors['glow'], visor_points)
        
        # Targeting dots
        for dx in [-20, 0, 20]:
            dot_color = self.colors['accent'] if int(pygame.time.get_ticks() / 200 + dx) % 2 else self.colors['glow']
            pygame.draw.polygon(screen, dot_color, [
                (head_x + dx, visor_y + 3),
                (head_x + dx + 3, visor_y + 6),
                (head_x + dx, visor_y + 9),
                (head_x + dx - 3, visor_y + 6)
            ])
    
    def draw_plasma_bot(self, screen, highlighted_part):
        """Energy-based robot - glowing core, hexagons"""
        y_offset = self.idle_offset
        
        # Energy field shadow
        shadow = pygame.Surface((200, 40), pygame.SRCALPHA)
        pygame.draw.polygon(shadow, (100, 0, 150, 60), [
            (0, 20), (50, 0), (150, 0), (200, 20), (150, 40), (50, 40)
        ])
        screen.blit(shadow, (self.x - 100, self.y + 250))
        
        # === LEGS - Energy conduits ===
        for leg_name in ['left_leg', 'right_leg']:
            part = self.parts[leg_name]
            color = self.colors['accent'] if highlighted_part == leg_name else self.colors['primary']
            
            leg_x = self.x + part['x']
            leg_y = self.y + part['y'] + y_offset
            
            # Main leg (hexagonal segments)
            for seg in range(3):
                seg_y = leg_y - 40 + seg * 35
                hex_points = self.create_hexagon(leg_x, seg_y, 20, 28)
                
                pygame.draw.polygon(screen, color, hex_points)
                pygame.draw.polygon(screen, self.colors['dark'], hex_points, 3)
                
                # Energy flow
                flow_intensity = int(abs(math.sin(pygame.time.get_ticks() / 200 - seg * 0.5)) * 155 + 100)
                flow_color = self.clamp_color((flow_intensity, 0, flow_intensity + 50))
                inner_hex = self.create_hexagon(leg_x, seg_y, 14, 20)
                pygame.draw.polygon(screen, flow_color, inner_hex)
        
        # === BODY - Plasma core ===
        part = self.parts['body']
        color = self.colors['accent'] if highlighted_part == 'body' else self.colors['secondary']
        
        body_x = self.x
        body_y = self.y + y_offset
        
        # Outer hexagon
        outer_hex = self.create_hexagon(body_x, body_y, 60, 70)
        pygame.draw.polygon(screen, color, outer_hex)
        pygame.draw.polygon(screen, self.colors['dark'], outer_hex, 4)
        
        # Plasma core (animated)
        core_pulse = abs(math.sin(pygame.time.get_ticks() / 250))
        core_size = int(40 + core_pulse * 15)
        
        for i in range(3):
            size = core_size - i * 12
            alpha = int(200 - i * 60)
            core_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            core_hex = self.create_hexagon(size, size, size - 5, size - 3)
            pygame.draw.polygon(core_surf, (*self.colors['glow'], alpha), core_hex)
            screen.blit(core_surf, (body_x - size, body_y - size))
        
        # Core center
        center_hex = self.create_hexagon(body_x, body_y, 18, 18)
        pygame.draw.polygon(screen, (255, 200, 255), center_hex)
        
        # === ARMS - Plasma emitters ===
        for arm_name in ['left_arm', 'right_arm']:
            part = self.parts[arm_name]
            color = self.colors['accent'] if highlighted_part == arm_name else self.colors['primary']
            
            arm_x = self.x + part['x']
            arm_y = self.y + part['y'] + y_offset
            
            # Upper arm
            upper_hex = self.create_hexagon(arm_x, arm_y - 25, 22, 30)
            pygame.draw.polygon(screen, color, upper_hex)
            pygame.draw.polygon(screen, self.colors['dark'], upper_hex, 3)
            
            # Lower arm (emitter)
            lower_hex = self.create_hexagon(arm_x, arm_y + 20, 18, 35)
            pygame.draw.polygon(screen, self.colors['dark'], lower_hex)
            pygame.draw.polygon(screen, self.colors['accent'], lower_hex, 2)
            
            # Plasma ball at hand
            plasma_y = arm_y + 50
            for i in range(3):
                plasma_size = 15 - i * 4
                plasma_alpha = 180 - i * 50
                plasma_surf = pygame.Surface((plasma_size*2, plasma_size*2), pygame.SRCALPHA)
                plasma_hex = self.create_hexagon(plasma_size, plasma_size, plasma_size - 2, plasma_size - 2)
                pygame.draw.polygon(plasma_surf, (*self.colors['glow'], plasma_alpha), plasma_hex)
                screen.blit(plasma_surf, (arm_x - plasma_size, plasma_y - plasma_size))
        
        # === HEAD - Energy matrix ===
        part = self.parts['head']
        color = self.colors['accent'] if highlighted_part == 'head' else self.colors['primary']
        
        head_x = self.x
        head_y = self.y - 120 + y_offset
        
        # Main head hexagon
        head_hex = self.create_hexagon(head_x, head_y, 55, 60)
        pygame.draw.polygon(screen, color, head_hex)
        pygame.draw.polygon(screen, self.colors['dark'], head_hex, 4)
        
        # Matrix eyes (3 hexagonal cells)
        eye_positions = [
            (head_x - 25, head_y - 10),
            (head_x, head_y - 10),
            (head_x + 25, head_y - 10)
        ]
        
        for ex, ey in eye_positions:
            eye_hex = self.create_hexagon(ex, ey, 12, 12)
            
            # Eye glow
            for i in range(2):
                glow_hex = self.create_hexagon(ex, ey, 14 - i*2, 14 - i*2)
                alpha = 120 - i * 50
                glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                glow_hex_offset = [(p[0] - ex + 15, p[1] - ey + 15) for p in glow_hex]
                pygame.draw.polygon(glow_surf, (*self.colors['glow'], alpha), glow_hex_offset)
                screen.blit(glow_surf, (ex - 15, ey - 15))
            
            pygame.draw.polygon(screen, self.colors['glow'], eye_hex)
            
            # Pupil
            pupil_hex = self.create_hexagon(ex, ey, 6, 6)
            pygame.draw.polygon(screen, (255, 255, 255), pupil_hex)
        
        # Energy corona
        corona_points = self.create_hexagon(head_x, head_y - 80, 15, 18)
        pygame.draw.polygon(screen, self.colors['glow'], corona_points)
    
    def create_hexagon(self, cx, cy, width, height):
        """Create hexagon points"""
        return [
            (cx, cy - height),
            (cx + width, cy - height//2),
            (cx + width, cy + height//2),
            (cx, cy + height),
            (cx - width, cy + height//2),
            (cx - width, cy - height//2)
        ]
    
    def draw_war_bot(self, screen, highlighted_part):
        """Military combat robot - rugged, practical design"""
        y_offset = self.idle_offset
        
        # Heavy shadow
        shadow = pygame.Surface((220, 45), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 90), (0, 0, 220, 45), border_radius=22)
        screen.blit(shadow, (self.x - 110, self.y + 250))
        
        # === LEGS - Combat boots ===
        for leg_name in ['left_leg', 'right_leg']:
            part = self.parts[leg_name]
            color = self.colors['accent'] if highlighted_part == leg_name else self.colors['primary']
            
            leg_x = self.x + part['x']
            leg_y = self.y + part['y'] + y_offset
            
            # Upper leg (reinforced)
            upper_rect = pygame.Rect(leg_x - 20, leg_y - 55, 40, 60)
            pygame.draw.rect(screen, color, upper_rect, border_radius=5)
            pygame.draw.rect(screen, self.colors['dark'], upper_rect, 3, border_radius=5)
            
            # Knee plate
            knee_rect = pygame.Rect(leg_x - 22, leg_y - 8, 44, 16)
            pygame.draw.rect(screen, self.colors['secondary'], knee_rect)
            pygame.draw.rect(screen, self.colors['dark'], knee_rect, 2)
            
            # Lower leg
            lower_rect = pygame.Rect(leg_x - 18, leg_y, 36, 55)
            pygame.draw.rect(screen, self.colors['dark'], lower_rect, border_radius=5)
            pygame.draw.rect(screen, self.colors['accent'], lower_rect, 2, border_radius=5)
            
            # Boot (wide base)
            boot_rect = pygame.Rect(leg_x - 24, leg_y + 45, 48, 15)
            pygame.draw.rect(screen, (60, 60, 70), boot_rect, border_radius=3)
        
        # === BODY - Armored vest ===
        part = self.parts['body']
        color = self.colors['accent'] if highlighted_part == 'body' else self.colors['secondary']
        
        body_rect = pygame.Rect(self.x - 55, self.y - 60 + y_offset, 110, 120)
        pygame.draw.rect(screen, color, body_rect, border_radius=8)
        pygame.draw.rect(screen, self.colors['dark'], body_rect, 4, border_radius=8)
        
        # Tactical vest plates
        plates = [
            pygame.Rect(body_rect.left + 10, body_rect.top + 15, 42, 35),
            pygame.Rect(body_rect.right - 52, body_rect.top + 15, 42, 35),
            pygame.Rect(body_rect.left + 10, body_rect.top + 55, 42, 35),
            pygame.Rect(body_rect.right - 52, body_rect.top + 55, 42, 35)
        ]
        
        for plate in plates:
            pygame.draw.rect(screen, self.colors['primary'], plate, border_radius=4)
            pygame.draw.rect(screen, self.colors['dark'], plate, 2, border_radius=4)
            
            # Bolts
            for by in [plate.top + 8, plate.bottom - 8]:
                for bx in [plate.left + 8, plate.right - 8]:
                    pygame.draw.rect(screen, (100, 100, 110), (bx - 3, by - 3, 6, 6))
        
        # Ammo belt
        for i in range(8):
            ammo_x = body_rect.left + 15 + i * 12
            ammo_y = body_rect.centery
            pygame.draw.rect(screen, (180, 150, 0), (ammo_x, ammo_y - 8, 8, 16), border_radius=2)
            pygame.draw.rect(screen, (120, 100, 0), (ammo_x, ammo_y - 8, 8, 16), 1, border_radius=2)
        
        # === ARMS - Weapon mounts ===
        for arm_name in ['left_arm', 'right_arm']:
            part = self.parts[arm_name]
            color = self.colors['accent'] if highlighted_part == arm_name else self.colors['primary']
            
            arm_x = self.x + part['x']
            arm_y = self.y + part['y'] + y_offset
            is_left = 'left' in arm_name
            
            # Upper arm
            upper_rect = pygame.Rect(arm_x - 20, arm_y - 50, 40, 55)
            pygame.draw.rect(screen, color, upper_rect, border_radius=6)
            pygame.draw.rect(screen, self.colors['dark'], upper_rect, 3, border_radius=6)
            
            # Elbow joint
            elbow_rect = pygame.Rect(arm_x - 18, arm_y - 10, 36, 20)
            pygame.draw.rect(screen, (120, 120, 130), elbow_rect)
            pygame.draw.line(screen, (80, 80, 90), 
                           (elbow_rect.left, elbow_rect.centery),
                           (elbow_rect.right, elbow_rect.centery), 2)
            
            # Forearm (gun mount)
            forearm_rect = pygame.Rect(arm_x - 16, arm_y + 10, 32, 50)
            pygame.draw.rect(screen, self.colors['dark'], forearm_rect, border_radius=5)
            pygame.draw.rect(screen, self.colors['accent'], forearm_rect, 2, border_radius=5)
            
            # Minigun barrels
            barrel_y = arm_y + 50
            for barrel_offset in [-8, 0, 8]:
                barrel_rect = pygame.Rect(arm_x + barrel_offset - 2, barrel_y, 4, 25)
                pygame.draw.rect(screen, (50, 50, 60), barrel_rect)
                pygame.draw.rect(screen, (100, 100, 110), barrel_rect, 1)
            
            # Barrel rotation indicator
            rotation_angle = (pygame.time.get_ticks() / 100) % 360
            indicator_x = arm_x + math.cos(math.radians(rotation_angle)) * 6
            indicator_y = barrel_y - 8 + math.sin(math.radians(rotation_angle)) * 6
            pygame.draw.line(screen, (255, 0, 0),
                           (arm_x, barrel_y - 8), (indicator_x, indicator_y), 2)
        
        # === HEAD - Tactical helmet ===
        part = self.parts['head']
        color = self.colors['accent'] if highlighted_part == 'head' else self.colors['primary']
        
        head_rect = pygame.Rect(self.x - 50, self.y - 180 + y_offset, 100, 120)
        pygame.draw.rect(screen, color, head_rect, border_radius=10)
        pygame.draw.rect(screen, self.colors['dark'], head_rect, 4, border_radius=10)
        
        # Helmet ridge
        ridge_rect = pygame.Rect(head_rect.left + 15, head_rect.top, head_rect.width - 30, 25)
        pygame.draw.rect(screen, self.colors['secondary'], ridge_rect, border_radius=8)
        pygame.draw.rect(screen, self.colors['dark'], ridge_rect, 2, border_radius=8)
        
        # Visor (T-shaped)
        visor_v = pygame.Rect(head_rect.centerx - 8, head_rect.centery - 25, 16, 45)
        visor_h = pygame.Rect(head_rect.left + 20, head_rect.centery - 25, head_rect.width - 40, 16)
        
        pygame.draw.rect(screen, (20, 20, 30), visor_v)
        pygame.draw.rect(screen, (20, 20, 30), visor_h)
        pygame.draw.rect(screen, self.colors['accent'], visor_v, 2)
        pygame.draw.rect(screen, self.colors['accent'], visor_h, 2)
        
        # HUD indicators in visor
        for i in range(3):
            hud_x = visor_h.left + 10 + i * 20
            hud_color = self.colors['accent'] if int(pygame.time.get_ticks() / 300 + i) % 2 else (100, 100, 100)
            pygame.draw.rect(screen, hud_color, (hud_x, visor_h.centery - 4, 12, 8))
        
        # Radio antenna
        antenna_base = (head_rect.right - 10, head_rect.top + 15)
        antenna_tip = (head_rect.right + 15, head_rect.top - 20)
        pygame.draw.line(screen, (150, 150, 160), antenna_base, antenna_tip, 4)
        pygame.draw.rect(screen, (255, 0, 0), (antenna_tip[0] - 4, antenna_tip[1] - 4, 8, 8))
    
    def draw_nano_bot(self, screen, highlighted_part):
        """Small advanced tech robot - clean, precise design"""
        y_offset = self.idle_offset * 1.5  # More floating motion
        
        # Soft glow shadow
        shadow = pygame.Surface((160, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (100, 150, 200, 50), (0, 0, 160, 30))
        screen.blit(shadow, (self.x - 80, self.y + 250))
        
        # === LEGS - Hover pads ===
        for leg_name in ['left_leg', 'right_leg']:
            part = self.parts[leg_name]
            color = self.colors['accent'] if highlighted_part == leg_name else self.colors['primary']
            
            leg_x = self.x + part['x']
            leg_y = self.y + part['y'] + y_offset
            
            # Upper leg (slim cylinder)
            upper_points = [
                (leg_x - 12, leg_y - 55),
                (leg_x + 12, leg_y - 55),
                (leg_x + 10, leg_y),
                (leg_x - 10, leg_y)
            ]
            pygame.draw.polygon(screen, color, upper_points)
            pygame.draw.polygon(screen, self.colors['dark'], upper_points, 2)
            
            # Knee joint (small sphere)
            pygame.draw.polygon(screen, (150, 180, 200), [
                (leg_x, leg_y - 8),
                (leg_x + 10, leg_y),
                (leg_x, leg_y + 8),
                (leg_x - 10, leg_y)
            ])
            
            # Lower leg
            lower_points = [
                (leg_x - 10, leg_y),
                (leg_x + 10, leg_y),
                (leg_x + 8, leg_y + 45),
                (leg_x - 8, leg_y + 45)
            ]
            pygame.draw.polygon(screen, self.colors['secondary'], lower_points)
            pygame.draw.polygon(screen, self.colors['dark'], lower_points, 2)
            
            # Hover pad (glowing)
            pad_y = leg_y + 50
            pad_rect = pygame.Rect(leg_x - 18, pad_y, 36, 12)
            
            # Pad glow
            for i in range(2):
                glow_rect = pad_rect.inflate(4 - i*2, 2)
                alpha = 100 - i * 40
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*self.colors['glow'], alpha), (0, 0, glow_rect.width, glow_rect.height))
                screen.blit(glow_surf, glow_rect.topleft)
            
            pygame.draw.rect(screen, self.colors['glow'], pad_rect)
            
            # Hover effect particles
            if random.random() > 0.7:
                particle_x = leg_x + random.randint(-15, 15)
                particle_y = pad_y + random.randint(8, 20)
                pygame.draw.polygon(screen, (150, 200, 255), [
                    (particle_x, particle_y),
                    (particle_x + 4, particle_y + 4),
                    (particle_x, particle_y + 8),
                    (particle_x - 4, particle_y + 4)
                ])
        
        # === BODY - Compact core ===
        part = self.parts['body']
        color = self.colors['accent'] if highlighted_part == 'body' else self.colors['secondary']
        
        body_rect = pygame.Rect(self.x - 45, self.y - 55 + y_offset, 90, 110)
        
        # Rounded body
        pygame.draw.rect(screen, color, body_rect, border_radius=15)
        pygame.draw.rect(screen, self.colors['dark'], body_rect, 3, border_radius=15)
        
        # Tech panels
        for i in range(4):
            panel_y = body_rect.top + 15 + i * 24
            panel_rect = pygame.Rect(body_rect.left + 10, panel_y, body_rect.width - 20, 18)
            
            pygame.draw.rect(screen, self.colors['primary'], panel_rect, border_radius=4)
            pygame.draw.rect(screen, self.colors['accent'], panel_rect, 1, border_radius=4)
            
            # Data lights
            for j in range(5):
                light_x = panel_rect.left + 5 + j * 14
                light_active = (pygame.time.get_ticks() // 100 + i * 3 + j) % 10 < 5
                light_color = self.colors['glow'] if light_active else (80, 90, 100)
                pygame.draw.rect(screen, light_color, (light_x, panel_rect.centery - 3, 8, 6))
        
        # Central processor
        core_rect = pygame.Rect(body_rect.centerx - 15, body_rect.centery - 15, 30, 30)
        pygame.draw.rect(screen, self.colors['dark'], core_rect, border_radius=8)
        
        # Processor glow
        pulse = abs(math.sin(pygame.time.get_ticks() / 200))
        glow_size = int(12 + pulse * 6)
        pygame.draw.rect(screen, self.colors['glow'], 
                        (core_rect.centerx - glow_size//2, core_rect.centery - glow_size//2, 
                         glow_size, glow_size), border_radius=4)
        
        # === ARMS - Precision tools ===
        for arm_name in ['left_arm', 'right_arm']:
            part = self.parts[arm_name]
            color = self.colors['accent'] if highlighted_part == arm_name else self.colors['primary']
            
            arm_x = self.x + part['x']
            arm_y = self.y + part['y'] + y_offset
            
            # Slim arm design
            arm_points = [
                (arm_x - 10, arm_y - 50),
                (arm_x + 10, arm_y - 50),
                (arm_x + 8, arm_y + 40),
                (arm_x - 8, arm_y + 40)
            ]
            pygame.draw.polygon(screen, color, arm_points)
            pygame.draw.polygon(screen, self.colors['dark'], arm_points, 2)
            
            # Elbow segment
            elbow_rect = pygame.Rect(arm_x - 12, arm_y - 8, 24, 16)
            pygame.draw.rect(screen, self.colors['secondary'], elbow_rect, border_radius=8)
            
            # Hand tool (laser pointer/scanner)
            hand_y = arm_y + 45
            hand_rect = pygame.Rect(arm_x - 8, hand_y, 16, 25)
            pygame.draw.rect(screen, self.colors['dark'], hand_rect, border_radius=4)
            
            # Laser beam
            beam_points = [
                (arm_x - 2, hand_y + 25),
                (arm_x + 2, hand_y + 25),
                (arm_x + 1, hand_y + 40),
                (arm_x - 1, hand_y + 40)
            ]
            pygame.draw.polygon(screen, (255, 100, 100), beam_points)
            
            # Beam tip glow
            pygame.draw.polygon(screen, (255, 200, 200), [
                (arm_x, hand_y + 40),
                (arm_x + 4, hand_y + 44),
                (arm_x, hand_y + 48),
                (arm_x - 4, hand_y + 44)
            ])
        
        # === HEAD - Display screen ===
        part = self.parts['head']
        color = self.colors['accent'] if highlighted_part == 'head' else self.colors['primary']
        
        head_rect = pygame.Rect(self.x - 45, self.y - 175 + y_offset, 90, 100)
        pygame.draw.rect(screen, color, head_rect, border_radius=12)
        pygame.draw.rect(screen, self.colors['dark'], head_rect, 3, border_radius=12)
        
        # Display screen
        screen_rect = pygame.Rect(head_rect.left + 10, head_rect.top + 15, head_rect.width - 20, 60)
        pygame.draw.rect(screen, (20, 30, 50), screen_rect, border_radius=6)
        pygame.draw.rect(screen, self.colors['accent'], screen_rect, 2, border_radius=6)
        
        # Display content (animated text/graphs)
        for i in range(4):
            line_y = screen_rect.top + 8 + i * 13
            line_width = 50 + int(abs(math.sin(pygame.time.get_ticks() / 500 + i)) * 20)
            pygame.draw.rect(screen, self.colors['glow'],
                           (screen_rect.left + 8, line_y, line_width, 8))
        
        # Status indicator
        status_rect = pygame.Rect(head_rect.left + 10, head_rect.bottom - 20, head_rect.width - 20, 12)
        pygame.draw.rect(screen, self.colors['dark'], status_rect, border_radius=6)
        
        # Status bars
        for i in range(5):
            bar_x = status_rect.left + 5 + i * 15
            bar_active = i < (pygame.time.get_ticks() // 300) % 6
            bar_color = self.colors['glow'] if bar_active else (60, 70, 80)
            pygame.draw.rect(screen, bar_color, (bar_x, status_rect.top + 3, 10, 6))
        
        # Antenna array
        for antenna_x in [head_rect.left + 15, head_rect.right - 15]:
            pygame.draw.rect(screen, (150, 180, 200), (antenna_x - 2, head_rect.top - 20, 4, 22))
            pygame.draw.polygon(screen, self.colors['glow'], [
                (antenna_x, head_rect.top - 24),
                (antenna_x + 5, head_rect.top - 28),
                (antenna_x, head_rect.top - 32),
                (antenna_x - 5, head_rect.top - 28)
            ])
    
    def draw_mech_bot(self, screen, highlighted_part):
        """Industrial worker robot - heavy, utilitarian"""
        y_offset = self.idle_offset
        
        # Oil stain shadow
        shadow = pygame.Surface((230, 48), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (40, 30, 20, 80), (0, 0, 230, 48))
        screen.blit(shadow, (self.x - 115, self.y + 250))
        
        # === LEGS - Industrial hydraulics ===
        for leg_name in ['left_leg', 'right_leg']:
            part = self.parts[leg_name]
            color = self.colors['accent'] if highlighted_part == leg_name else self.colors['primary']
            
            leg_x = self.x + part['x']
            leg_y = self.y + part['y'] + y_offset
            
            # Upper leg (thick rectangle)
            upper_rect = pygame.Rect(leg_x - 22, leg_y - 55, 44, 58)
            pygame.draw.rect(screen, color, upper_rect, border_radius=6)
            pygame.draw.rect(screen, self.colors['dark'], upper_rect, 4, border_radius=6)
            
            # Rivets
            for ry in [upper_rect.top + 12, upper_rect.top + 30, upper_rect.top + 48]:
                for rx in [upper_rect.left + 8, upper_rect.right - 8]:
                    pygame.draw.rect(screen, (120, 100, 80), (rx - 4, ry - 4, 8, 8))
                    pygame.draw.rect(screen, (80, 60, 40), (rx - 4, ry - 4, 8, 8), 2)
            
            # Hydraulic piston
            piston_rect = pygame.Rect(leg_x - 8, leg_y - 10, 16, 28)
            pygame.draw.rect(screen, (140, 140, 150), piston_rect)
            pygame.draw.rect(screen, (90, 90, 100), piston_rect, 2)
            
            # Piston rod
            rod_rect = pygame.Rect(leg_x - 4, leg_y - 30, 8, 35)
            pygame.draw.rect(screen, (180, 180, 190), rod_rect)
            
            # Lower leg
            lower_rect = pygame.Rect(leg_x - 20, leg_y + 15, 40, 45)
            pygame.draw.rect(screen, self.colors['dark'], lower_rect, border_radius=5)
            pygame.draw.rect(screen, self.colors['accent'], lower_rect, 3, border_radius=5)
            
            # Foot platform
            foot_rect = pygame.Rect(leg_x - 26, leg_y + 52, 52, 14)
            pygame.draw.rect(screen, (100, 90, 70), foot_rect, border_radius=3)
            pygame.draw.rect(screen, (60, 50, 40), foot_rect, 2, border_radius=3)
        
        # === BODY - Industrial chassis ===
        part = self.parts['body']
        color = self.colors['accent'] if highlighted_part == 'body' else self.colors['secondary']
        
        body_rect = pygame.Rect(self.x - 60, self.y - 65 + y_offset, 120, 130)
        pygame.draw.rect(screen, color, body_rect, border_radius=8)
        pygame.draw.rect(screen, self.colors['dark'], body_rect, 5, border_radius=8)
        
        # Warning stripes
        stripe_y = body_rect.top + 10
        for i in range(6):
            stripe_x = body_rect.left + 10 + i * 18
            stripe_color = (255, 200, 0) if i % 2 == 0 else (40, 40, 50)
            pygame.draw.rect(screen, stripe_color, (stripe_x, stripe_y, 14, body_rect.height - 20))
        
        # Cargo compartment
        cargo_rect = pygame.Rect(body_rect.left + 15, body_rect.top + 40, body_rect.width - 30, 50)
        pygame.draw.rect(screen, self.colors['dark'], cargo_rect, border_radius=6)
        pygame.draw.rect(screen, (180, 160, 120), cargo_rect, 3, border_radius=6)
        
        # Compartment latch
        latch_rect = pygame.Rect(cargo_rect.centerx - 12, cargo_rect.centery - 8, 24, 16)
        pygame.draw.rect(screen, (200, 180, 140), latch_rect, border_radius=4)
        pygame.draw.rect(screen, (120, 100, 80), latch_rect, 2, border_radius=4)
        
        # === ARMS - Industrial claws/tools ===
        for arm_name in ['left_arm', 'right_arm']:
            part = self.parts[arm_name]
            color = self.colors['accent'] if highlighted_part == arm_name else self.colors['primary']
            
            arm_x = self.x + part['x']
            arm_y = self.y + part['y'] + y_offset
            is_left = 'left' in arm_name
            
            # Shoulder joint (large cylinder)
            shoulder_rect = pygame.Rect(arm_x - 24, arm_y - 55, 48, 35)
            pygame.draw.rect(screen, color, shoulder_rect, border_radius=8)
            pygame.draw.rect(screen, self.colors['dark'], shoulder_rect, 4, border_radius=8)
            
            # Joint bolts
            for jx in [shoulder_rect.left + 10, shoulder_rect.right - 10]:
                for jy in [shoulder_rect.top + 10, shoulder_rect.bottom - 10]:
                    pygame.draw.rect(screen, (120, 100, 80), (jx - 5, jy - 5, 10, 10))
            
            # Upper arm
            upper_rect = pygame.Rect(arm_x - 18, arm_y - 20, 36, 50)
            pygame.draw.rect(screen, self.colors['secondary'], upper_rect, border_radius=5)
            pygame.draw.rect(screen, self.colors['dark'], upper_rect, 3, border_radius=5)
            
            # Elbow hydraulic
            elbow_rect = pygame.Rect(arm_x - 20, arm_y + 20, 40, 24)
            pygame.draw.rect(screen, (140, 140, 150), elbow_rect)
            pygame.draw.rect(screen, (90, 90, 100), elbow_rect, 2)
            
            # Forearm
            forearm_rect = pygame.Rect(arm_x - 16, arm_y + 40, 32, 35)
            pygame.draw.rect(screen, self.colors['dark'], forearm_rect, border_radius=4)
            pygame.draw.rect(screen, self.colors['accent'], forearm_rect, 2, border_radius=4)
            
            # Claw/gripper
            claw_base_y = arm_y + 72
            
            # Claw fingers (3 prongs)
            for claw_i, angle_offset in enumerate([-30, 0, 30]):
                angle = math.radians(angle_offset)
                
                # Finger base
                finger_points = [
                    (arm_x, claw_base_y),
                    (arm_x + math.sin(angle) * 15, claw_base_y + 8),
                    (arm_x + math.sin(angle) * 18, claw_base_y + 28),
                    (arm_x + math.sin(angle) * 10, claw_base_y + 30),
                    (arm_x, claw_base_y + 8)
                ]
                
                pygame.draw.polygon(screen, (100, 90, 70), finger_points)
                pygame.draw.polygon(screen, (60, 50, 40), finger_points, 2)
        
        # === HEAD - Industrial helmet ===
        part = self.parts['head']
        color = self.colors['accent'] if highlighted_part == 'head' else self.colors['primary']
        
        head_rect = pygame.Rect(self.x - 52, self.y - 185 + y_offset, 104, 125)
        pygame.draw.rect(screen, color, head_rect, border_radius=10)
        pygame.draw.rect(screen, self.colors['dark'], head_rect, 4, border_radius=10)
        
        # Hard hat style top
        hat_rect = pygame.Rect(head_rect.left + 5, head_rect.top, head_rect.width - 10, 30)
        pygame.draw.rect(screen, (255, 200, 0), hat_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 150, 0), hat_rect, 3, border_radius=8)
        
        # Center stripe on hat
        pygame.draw.rect(screen, (255, 255, 255),
                        (hat_rect.left + 10, hat_rect.top + 8, hat_rect.width - 20, 14))
        
        # Visor window
        visor_rect = pygame.Rect(head_rect.left + 15, head_rect.top + 45, head_rect.width - 30, 50)
        pygame.draw.rect(screen, (30, 40, 60), visor_rect, border_radius=6)
        pygame.draw.rect(screen, (100, 110, 130), visor_rect, 3, border_radius=6)
        
        # Visor grid
        for grid_x in range(visor_rect.left + 12, visor_rect.right - 10, 18):
            pygame.draw.line(screen, (60, 70, 90),
                           (grid_x, visor_rect.top + 8),
                           (grid_x, visor_rect.bottom - 8), 2)
        for grid_y in range(visor_rect.top + 12, visor_rect.bottom - 10, 15):
            pygame.draw.line(screen, (60, 70, 90),
                           (visor_rect.left + 8, grid_y),
                           (visor_rect.right - 8, grid_y), 2)
        
        # Eyes/cameras behind visor
        for eye_x in [head_rect.left + 30, head_rect.right - 30]:
            eye_rect = pygame.Rect(eye_x - 10, visor_rect.centery - 8, 20, 16)
            pygame.draw.rect(screen, (255, 200, 0), eye_rect, border_radius=8)
            pygame.draw.rect(screen, (200, 150, 0), eye_rect, border_radius=8)
            
            # Lens
            pygame.draw.rect(screen, (100, 80, 0), (eye_x - 6, visor_rect.centery - 4, 12, 8))
        
        # Vents at bottom
        for vent_i in range(4):
            vent_x = head_rect.left + 20 + vent_i * 18
            vent_rect = pygame.Rect(vent_x, head_rect.bottom - 22, 14, 16)
            pygame.draw.rect(screen, (50, 50, 60), vent_rect, border_radius=3)
            pygame.draw.rect(screen, (100, 100, 110), vent_rect, 1, border_radius=3)
        
        # Warning light
        light_blink = int(pygame.time.get_ticks() / 500) % 2
        light_color = (255, 100, 0) if light_blink else (150, 60, 0)
        light_rect = pygame.Rect(head_rect.right - 18, head_rect.top + 8, 12, 12)
        pygame.draw.rect(screen, light_color, light_rect)
        if light_blink:
            pygame.draw.rect(screen, (255, 200, 150), light_rect.inflate(-4, -4))
    
    def draw_cyber_bot(self, screen, highlighted_part):
        """Futuristic cyber robot - neon, holographic style"""
        y_offset = self.idle_offset
        
        # Hologram projection shadow
        shadow = pygame.Surface((200, 40), pygame.SRCALPHA)
        for i in range(5):
            alpha = 60 - i * 10
            pygame.draw.ellipse(shadow, (0, 255, 255, alpha), (i*5, i*2, 200-i*10, 40-i*4))
        screen.blit(shadow, (self.x - 100, self.y + 250))
        
        # === LEGS - Energy conduits ===
        for leg_name in ['left_leg', 'right_leg']:
            part = self.parts[leg_name]
            color = self.colors['accent'] if highlighted_part == leg_name else self.colors['primary']
            
            leg_x = self.x + part['x']
            leg_y = self.y + part['y'] + y_offset
            
            # Leg segments with gaps (showing energy flow)
            segments = [
                (leg_y - 55, 25),
                (leg_y - 25, 22),
                (leg_y, 20),
                (leg_y + 25, 30)
            ]
            
            for seg_y, seg_h in segments:
                seg_rect = pygame.Rect(leg_x - 12, seg_y, 24, seg_h)
                
                # Main segment
                pygame.draw.rect(screen, color, seg_rect, border_radius=6)
                pygame.draw.rect(screen, self.colors['accent'], seg_rect, 2, border_radius=6)
                
                # Inner glow
                glow_rect = seg_rect.inflate(-6, -6)
                glow_intensity = int(abs(math.sin(pygame.time.get_ticks() / 300 + seg_y / 50)) * 155 + 100)
                glow_color = self.clamp_color((0, glow_intensity, glow_intensity + 50))
                pygame.draw.rect(screen, glow_color, glow_rect, border_radius=3)
            
            # Energy bridges between segments
            for i in range(len(segments) - 1):
                bridge_y1 = segments[i][0] + segments[i][1]
                bridge_y2 = segments[i+1][0]
                
                # Glowing lines
                for offset in [-4, 0, 4]:
                    line_x = leg_x + offset
                    line_color = self.colors['glow'] if offset == 0 else self.colors['accent']
                    pygame.draw.line(screen, line_color, (line_x, bridge_y1), (line_x, bridge_y2), 2)
        
        # === BODY - Holographic core ===
        part = self.parts['body']
        color = self.colors['accent'] if highlighted_part == 'body' else self.colors['secondary']
        
        body_x = self.x
        body_y = self.y + y_offset
        
        # Outer frame (diamond shape)
        body_points = [
            (body_x, body_y - 65),
            (body_x + 55, body_y),
            (body_x, body_y + 65),
            (body_x - 55, body_y)
        ]
        
        # Frame glow
        for i in range(3):
            glow_points = [(p[0] + (2-i)*3 if p[0] > body_x else p[0] - (2-i)*3, 
                          p[1] + (2-i)*3 if p[1] > body_y else p[1] - (2-i)*3)
                         for p in body_points]
            alpha = 80 - i * 25
            body_surf = pygame.Surface((150, 150), pygame.SRCALPHA)
            pygame.draw.polygon(body_surf, (*self.colors['glow'], alpha),
                              [(p[0] - body_x + 75, p[1] - body_y + 75) for p in glow_points])
            screen.blit(body_surf, (body_x - 75, body_y - 75))
        
        pygame.draw.polygon(screen, color, body_points)
        pygame.draw.polygon(screen, self.colors['accent'], body_points, 3)
        
        # Holographic matrix inside
        matrix_size = int(40 + abs(math.sin(pygame.time.get_ticks() / 400)) * 15)
        for layer in range(3):
            layer_size = matrix_size - layer * 12
            layer_alpha = 200 - layer * 60
            layer_points = [
                (body_x, body_y - layer_size),
                (body_x + layer_size, body_y),
                (body_x, body_y + layer_size),
                (body_x - layer_size, body_y)
            ]
            
            matrix_surf = pygame.Surface((layer_size*2+20, layer_size*2+20), pygame.SRCALPHA)
            pygame.draw.polygon(matrix_surf, (*self.colors['glow'], layer_alpha),
                              [(p[0] - body_x + layer_size + 10, p[1] - body_y + layer_size + 10) 
                               for p in layer_points])
            screen.blit(matrix_surf, (body_x - layer_size - 10, body_y - layer_size - 10))
        
        # Data streams
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle + pygame.time.get_ticks() / 50)
            stream_x = body_x + math.cos(rad) * 35
            stream_y = body_y + math.sin(rad) * 35
            
            pygame.draw.polygon(screen, self.colors['accent'], [
                (stream_x, stream_y),
                (stream_x + 4, stream_y + 4),
                (stream_x, stream_y + 8),
                (stream_x - 4, stream_y + 4)
            ])
        
        # === ARMS - Holographic projectors ===
        for arm_name in ['left_arm', 'right_arm']:
            part = self.parts[arm_name]
            color = self.colors['accent'] if highlighted_part == arm_name else self.colors['primary']
            
            arm_x = self.x + part['x']
            arm_y = self.y + part['y'] + y_offset
            
            # Arm segments (floating pieces)
            arm_segments = [
                (arm_y - 50, 28),
                (arm_y - 18, 24),
                (arm_y + 10, 28),
                (arm_y + 42, 20)
            ]
            
            for seg_y, seg_h in arm_segments:
                seg_points = [
                    (arm_x - 10, seg_y),
                    (arm_x + 10, seg_y),
                    (arm_x + 8, seg_y + seg_h),
                    (arm_x - 8, seg_y + seg_h)
                ]
                
                pygame.draw.polygon(screen, color, seg_points)
                pygame.draw.polygon(screen, self.colors['accent'], seg_points, 2)
                
                # Energy glow
                inner_points = [
                    (arm_x - 6, seg_y + 4),
                    (arm_x + 6, seg_y + 4),
                    (arm_x + 5, seg_y + seg_h - 4),
                    (arm_x - 5, seg_y + seg_h - 4)
                ]
                pygame.draw.polygon(screen, self.colors['glow'], inner_points)
            
            # Hologram projector at hand
            proj_y = arm_y + 68
            proj_rect = pygame.Rect(arm_x - 10, proj_y, 20, 16)
            pygame.draw.rect(screen, self.colors['dark'], proj_rect, border_radius=4)
            pygame.draw.rect(screen, self.colors['accent'], proj_rect, 2, border_radius=4)
            
            # Hologram projection
            for holo_i in range(3):
                holo_y = proj_y + 18 + holo_i * 8
                holo_width = 16 - holo_i * 3
                holo_alpha = 150 - holo_i * 40
                holo_surf = pygame.Surface((holo_width, 4), pygame.SRCALPHA)
                holo_surf.fill((*self.colors['glow'], holo_alpha))
                screen.blit(holo_surf, (arm_x - holo_width//2, holo_y))
        
        # === HEAD - Holographic display ===
        part = self.parts['head']
        color = self.colors['accent'] if highlighted_part == 'head' else self.colors['primary']
        
        head_x = self.x
        head_y = self.y - 120 + y_offset
        
        # Head frame (octagon)
        head_size = 50
        oct_angles = [i * 45 for i in range(8)]
        head_points = [
            (head_x + math.cos(math.radians(angle)) * head_size,
             head_y + math.sin(math.radians(angle)) * head_size)
            for angle in oct_angles
        ]
        
        # Frame glow
        for i in range(2):
            glow_factor = 1 + i * 0.1
            glow_points = [
                (head_x + (p[0] - head_x) * glow_factor,
                 head_y + (p[1] - head_y) * glow_factor)
                for p in head_points
            ]
            alpha = 100 - i * 40
            head_surf = pygame.Surface((head_size*3, head_size*3), pygame.SRCALPHA)
            pygame.draw.polygon(head_surf, (*self.colors['glow'], alpha),
                              [(p[0] - head_x + head_size*1.5, p[1] - head_y + head_size*1.5) 
                               for p in glow_points])
            screen.blit(head_surf, (head_x - head_size*1.5, head_y - head_size*1.5))
        
        pygame.draw.polygon(screen, color, head_points)
        pygame.draw.polygon(screen, self.colors['accent'], head_points, 3)
        
        # Holographic face display
        face_pulse = abs(math.sin(pygame.time.get_ticks() / 300))
        
        # Eyes (glowing lines)
        eye_width = int(20 + face_pulse * 8)
        for eye_x in [head_x - 20, head_x + 20]:
            eye_points = [
                (eye_x - eye_width//2, head_y - 15),
                (eye_x + eye_width//2, head_y - 15),
                (eye_x + eye_width//2 - 3, head_y - 8),
                (eye_x - eye_width//2 + 3, head_y - 8)
            ]
            
            # Eye glow
            for i in range(2):
                alpha = int((180 - i * 60) * (0.5 + face_pulse * 0.5))
                eye_surf = pygame.Surface((eye_width+10, 15), pygame.SRCALPHA)
                pygame.draw.polygon(eye_surf, (*self.colors['glow'], alpha),
                                  [(p[0] - eye_x + eye_width//2 + 5, p[1] - head_y + 20) 
                                   for p in eye_points])
                screen.blit(eye_surf, (eye_x - eye_width//2 - 5, head_y - 20))
            
            pygame.draw.polygon(screen, self.colors['glow'], eye_points)
        
        # Mouth/data stream
        mouth_y = head_y + 10
        for line_i in range(5):
            line_width = 30 - abs(line_i - 2) * 8
            line_x = head_x - line_width // 2
            line_y = mouth_y + line_i * 4
            
            line_alpha = int((150 - line_i * 20) * (0.5 + face_pulse * 0.5))
            line_surf = pygame.Surface((line_width, 2), pygame.SRCALPHA)
            line_surf.fill((*self.colors['glow'], line_alpha))
            screen.blit(line_surf, (line_x, line_y))
        
        # Antenna/signal array
        for antenna_angle in [-30, 30]:
            angle_rad = math.radians(antenna_angle)
            antenna_base = (head_x + math.sin(angle_rad) * 35, head_y - 45)
            antenna_tip = (head_x + math.sin(angle_rad) * 45, head_y - 70)
            
            pygame.draw.line(screen, self.colors['accent'], antenna_base, antenna_tip, 3)
            
            # Signal waves
            wave_phase = pygame.time.get_ticks() / 200
            for wave_i in range(3):
                wave_dist = 8 + wave_i * 6 + (wave_phase % 20)
                wave_x = antenna_tip[0] + math.sin(angle_rad) * wave_dist
                wave_y = antenna_tip[1] - wave_dist // 2
                wave_alpha = int(200 - wave_i * 60 - (wave_phase % 20) * 8)
                
                if wave_alpha > 0:
                    wave_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
                    pygame.draw.polygon(wave_surf, (*self.colors['glow'], wave_alpha), [
                        (5, 0), (8, 5), (5, 10), (2, 5)
                    ])
                    screen.blit(wave_surf, (wave_x - 5, wave_y - 5))