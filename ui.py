import pygame
import os
import math
import random

class UI:
    def __init__(self, width, height):
        self.width  = width
        self.height = height
        pygame.font.init()

        font_file = 'fonts/DejaVuSans.ttf'
        if os.path.exists(font_file):
            try:
                self.title_font  = pygame.font.Font(font_file, 72)
                self.large_font  = pygame.font.Font(font_file, 48)
                self.medium_font = pygame.font.Font(font_file, 36)
                self.small_font  = pygame.font.Font(font_file, 28)
                self.tiny_font   = pygame.font.Font(font_file, 21)
                self.micro_font  = pygame.font.Font(font_file, 17)
                self.buttons = {}
                # Animation states
                self._gun_recoil = 0.0
                self._gun_kickback = 0.0
                self._muzzle_flash_timer = 0.0
                self._shoot_frame = 0
                print("OK Font DejaVuSans")
                return
            except: pass

        vn = ['dejavusans','notosans','freesans','liberationsans','arial','tahoma','verdana']
        sf = next((f for f in vn if f in pygame.font.get_fonts()), None)
        def mk(s,b=False):
            return pygame.font.SysFont(sf,s,bold=b) if sf else pygame.font.Font(None,s)
        self.title_font=mk(72,True); self.large_font=mk(48,True)
        self.medium_font=mk(36); self.small_font=mk(28)
        self.tiny_font=mk(21); self.micro_font=mk(17)
        self.buttons={}
        self._gun_recoil=0.0; self._gun_kickback=0.0
        self._muzzle_flash_timer=0.0; self._shoot_frame=0

    # ══════════════════════════════════════════════════════════
    #   HELPER FUNCTIONS
    # ══════════════════════════════════════════════════════════
    def wrap_text(self, text, font, max_width):
        words=text.split(' '); lines=[]; cur=[]
        for w in words:
            test=' '.join(cur+[w])
            try:
                if font.size(test)[0]<=max_width: cur.append(w)
                else:
                    if cur: lines.append(' '.join(cur))
                    cur=[w]
            except: cur.append(w)
        if cur: lines.append(' '.join(cur))
        return lines or [""]

    def safe_render(self, font, text, color):
        try: return font.render(text, True, color)
        except: return self.micro_font.render(text, True, color)

    def draw_button(self, screen, text, x, y, w, h, col, hov, bid):
        mx,my=pygame.mouse.get_pos()
        c=hov if (x<=mx<=x+w and y<=my<=y+h) else col
        pygame.draw.rect(screen,c,(x,y,w,h),border_radius=10)
        pygame.draw.rect(screen,(255,255,255),(x,y,w,h),3,border_radius=10)
        ts=self.safe_render(self.medium_font,text,(255,255,255))
        if ts.get_width()>w-10: ts=self.safe_render(self.small_font,text,(255,255,255))
        screen.blit(ts,ts.get_rect(center=(x+w//2,y+h//2)))
        self.buttons[bid]=(x,y,w,h)

    def check_button_click(self,x,y,bid):
        if bid in self.buttons:
            bx,by,bw,bh=self.buttons[bid]
            return bx<=x<=bx+bw and by<=y<=by+bh
        return False

    # ══════════════════════════════════════════════════════════
    #   TRIGGER SHOOT EFFECT
    # ══════════════════════════════════════════════════════════
    def trigger_shoot_effect(self):
        """Trigger shooting animation"""
        self._gun_recoil = 1.0
        self._gun_kickback = 25.0
        self._muzzle_flash_timer = 0.15
        self._shoot_frame = 0

    # ══════════════════════════════════════════════════════════
    #   ENHANCED DOOM BACKGROUND - CORRIDOR WITH DEPTH
    # ══════════════════════════════════════════════════════════
    def draw_background(self, screen):
        """Vẽ background DOOM corridor với depth và lighting nâng cao"""
        W, H = self.width, self.height
        t = pygame.time.get_ticks()
        
        # ═══ SKY/CEILING GRADIENT ═══
        for y in range(H // 2):
            progress = y / (H / 2)
            r = int(15 + progress * 15)
            g = int(18 + progress * 18)
            b = int(25 + progress * 25)
            pygame.draw.line(screen, (r, g, b), (0, y), (W, y))
        
        # ═══ FLOOR GRADIENT WITH PERSPECTIVE ═══
        for y in range(H // 2, H):
            progress = (y - H/2) / (H/2)
            # Darker near horizon, lighter closer to player
            base = int(30 + progress * 35)
            pygame.draw.line(screen, (base, base - 5, base - 10), (0, y), (W, y))
        
        horizon_y = H // 2
        
        # ═══ CORRIDOR WALLS WITH PERSPECTIVE ═══
        # Left wall
        wall_left_top = int(W * 0.20)
        wall_left_bottom = int(W * 0.05)
        
        wall_left_points = [
            (0, 0),
            (wall_left_top, horizon_y - 120),
            (wall_left_top, horizon_y + 120),
            (wall_left_bottom, H)
        ]
        
        # Right wall
        wall_right_top = int(W * 0.80)
        wall_right_bottom = int(W * 0.95)
        
        wall_right_points = [
            (W, 0),
            (wall_right_top, horizon_y - 120),
            (wall_right_top, horizon_y + 120),
            (wall_right_bottom, H)
        ]
        
        # Draw walls with lighting
        for points, base_color in [(wall_left_points, (55, 60, 70)), 
                                   (wall_right_points, (50, 55, 65))]:
            pygame.draw.polygon(screen, base_color, points)
            pygame.draw.polygon(screen, (75, 80, 90), points, 3)
        
        # ═══ WALL PANELS AND DETAILS ═══
        # Left wall panels
        for panel_y in range(80, H - 80, 100):
            panel_w = 50
            panel_h = 85
            
            # Perspective calculation
            y_progress = panel_y / H
            panel_x = int(wall_left_bottom + (wall_left_top - wall_left_bottom) * (1 - y_progress))
            
            if panel_x > 20 and panel_x < W * 0.3:
                panel_rect = pygame.Rect(panel_x - panel_w, panel_y, panel_w, panel_h)
                
                # Panel background
                pygame.draw.rect(screen, (65, 70, 80), panel_rect)
                pygame.draw.rect(screen, (45, 50, 60), panel_rect, 2)
                
                # Panel details
                for i in range(3):
                    detail_y = panel_rect.top + 15 + i * 25
                    pygame.draw.rect(screen, (75, 80, 90), 
                                   (panel_rect.left + 5, detail_y, panel_rect.width - 10, 18))
                    pygame.draw.rect(screen, (55, 60, 70), 
                                   (panel_rect.left + 5, detail_y, panel_rect.width - 10, 18), 1)
                
                # Rivets
                for rx in [panel_rect.left + 10, panel_rect.right - 10]:
                    for ry in [panel_rect.top + 20, panel_rect.bottom - 20]:
                        pygame.draw.circle(screen, (85, 90, 100), (rx, ry), 4)
                        pygame.draw.circle(screen, (40, 45, 55), (rx, ry), 2)
                
                # Blinking light
                if (t // 600 + panel_y // 100) % 3 == 0:
                    light_color = (0, 255, 150)
                else:
                    light_color = (0, 80, 50)
                
                pygame.draw.rect(screen, light_color, 
                               (panel_rect.centerx - 8, panel_rect.top + 8, 16, 8))
        
        # Right wall panels (mirror)
        for panel_y in range(80, H - 80, 100):
            panel_w = 50
            panel_h = 85
            
            y_progress = panel_y / H
            panel_x = int(wall_right_bottom + (wall_right_top - wall_right_bottom) * (1 - y_progress))
            
            if panel_x < W - 20 and panel_x > W * 0.7:
                panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
                
                pygame.draw.rect(screen, (65, 70, 80), panel_rect)
                pygame.draw.rect(screen, (45, 50, 60), panel_rect, 2)
                
                for i in range(3):
                    detail_y = panel_rect.top + 15 + i * 25
                    pygame.draw.rect(screen, (75, 80, 90), 
                                   (panel_rect.left + 5, detail_y, panel_rect.width - 10, 18))
                
                for rx in [panel_rect.left + 10, panel_rect.right - 10]:
                    for ry in [panel_rect.top + 20, panel_rect.bottom - 20]:
                        pygame.draw.circle(screen, (85, 90, 100), (rx, ry), 4)
                        pygame.draw.circle(screen, (40, 45, 55), (rx, ry), 2)
                
                if (t // 600 + panel_y // 100) % 3 == 0:
                    light_color = (0, 255, 150)
                else:
                    light_color = (0, 80, 50)
                
                pygame.draw.rect(screen, light_color, 
                               (panel_rect.centerx - 8, panel_rect.top + 8, 16, 8))
        
        # ═══ CEILING LIGHTS WITH GLOW ═══
        num_lights = 5
        for i in range(num_lights):
            light_x = int(W * 0.25 + (W * 0.5 / (num_lights - 1)) * i) if num_lights > 1 else W // 2
            light_y = horizon_y - 140
            
            # Light fixture
            fixture_w = 80
            fixture_h = 20
            fixture_rect = pygame.Rect(light_x - fixture_w // 2, light_y, fixture_w, fixture_h)
            
            pygame.draw.rect(screen, (75, 80, 90), fixture_rect)
            pygame.draw.rect(screen, (95, 100, 110), fixture_rect, 2)
            
            # Light glow (multiple layers for depth)
            for j in range(4):
                glow_size = (90 + j * 30, 40 + j * 15)
                alpha = 140 - j * 35
                
                glow_surf = pygame.Surface(glow_size, pygame.SRCALPHA)
                pygame.draw.ellipse(glow_surf, (200, 220, 255, alpha), (0, 0, *glow_size))
                
                screen.blit(glow_surf, (light_x - glow_size[0] // 2, light_y + 10 - j * 5))
        
        # ═══ FLOOR GRID WITH PERSPECTIVE ═══
        grid_start_y = horizon_y + 130
        
        # Horizontal lines
        for i in range(10):
            y = grid_start_y + i * 30
            
            # Width decreases with distance
            progress = i / 10
            width_factor = 1 - progress * 0.6
            line_width = int(W * 0.5 * width_factor)
            
            x_center = W // 2
            line_color = (45 + i * 3, 45 + i * 3, 55 + i * 3)
            
            pygame.draw.line(screen, line_color,
                           (x_center - line_width, y),
                           (x_center + line_width, y), 2)
        
        # Vertical lines (perspective)
        for i in range(-3, 4):
            x_start = W // 2 + i * 100
            
            # Draw from horizon to bottom
            for j in range(10):
                y1 = grid_start_y + j * 30
                y2 = y1 + 25
                
                # Converge to center
                convergence = (10 - j) / 10
                x_offset = i * 100 * convergence
                
                x1 = W // 2 + int(x_offset)
                x2 = W // 2 + int(x_offset * 0.92)
                
                line_color = (45 + j * 2, 45 + j * 2, 55 + j * 2)
                pygame.draw.line(screen, line_color, (x1, y1), (x2, y2), 1)
        
        # ═══ DISTANT DOORWAY (WHERE MONSTER STANDS) ═══
        door_w = 240
        door_h = 260
        door_x = (W - door_w) // 2
        door_y = horizon_y - door_h // 2
        
        # Doorway frame (thick metal frame)
        frame_thickness = 12
        pygame.draw.rect(screen, (45, 50, 60), 
                        (door_x - frame_thickness, door_y - frame_thickness, 
                         door_w + frame_thickness * 2, door_h + frame_thickness * 2))
        
        # Frame highlights
        pygame.draw.rect(screen, (65, 70, 80),
                        (door_x - frame_thickness, door_y - frame_thickness,
                         door_w + frame_thickness * 2, door_h + frame_thickness * 2), 3)
        
        # Dark interior
        pygame.draw.rect(screen, (10, 12, 18), (door_x, door_y, door_w, door_h))
        
        # Doorway warning lights
        for light_side, dx in [("left", -25), ("right", door_w + 15)]:
            light_x = door_x + dx
            light_y = door_y + 25
            
            # Blinking effect
            blink_phase = (t // 400) % 2
            if blink_phase:
                light_color = (255, 50, 50)
                
                # Light housing
                pygame.draw.circle(screen, (80, 30, 30), (light_x, light_y), 12)
                pygame.draw.circle(screen, light_color, (light_x, light_y), 9)
                
                # Glow
                for j in range(3):
                    glow_size = 25 + j * 12
                    alpha = 120 - j * 40
                    
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*light_color, alpha), (glow_size, glow_size), glow_size)
                    screen.blit(glow_surf, (light_x - glow_size, light_y - glow_size))
            else:
                pygame.draw.circle(screen, (80, 30, 30), (light_x, light_y), 12)
                pygame.draw.circle(screen, (100, 20, 20), (light_x, light_y), 9)
        
        # Hazard stripes on doorway
        stripe_w = 30
        for i in range(0, door_w, stripe_w * 2):
            # Top stripe
            pygame.draw.rect(screen, (200, 200, 0), (door_x + i, door_y - 8, stripe_w, 8))
            # Bottom stripe
            pygame.draw.rect(screen, (200, 200, 0), (door_x + i, door_y + door_h, stripe_w, 8))

    # ══════════════════════════════════════════════════════════
    #   ENHANCED DOOM GUN - REALISTIC HANDS & WEAPON
    # ══════════════════════════════════════════════════════════
    def draw_gun_doom(self, screen, show_flash=False):
        """Vẽ súng DOOM-style với tay cầm chi tiết và realistic"""
        W, H = self.width, self.height
        t = pygame.time.get_ticks()
        
        # Update animation timers
        if self._muzzle_flash_timer > 0:
            self._muzzle_flash_timer -= 1/60.0
            show_flash = True
        
        # Recoil animation (smooth decay)
        self._gun_recoil = max(0, self._gun_recoil - 0.08)
        self._gun_kickback = max(0, self._gun_kickback - 2.0)
        
        # Gun base position
        gun_base_x = W // 2
        gun_base_y = H - 60 + self._gun_kickback
        
        # Recoil offset
        recoil_y = -self._gun_recoil * 40
        recoil_x_sway = math.sin(self._gun_recoil * 3) * 5  # Slight horizontal sway
        
        # ═══ LEFT HAND (SUPPORTING HAND) ═══
        left_hand_x = gun_base_x - 130 + recoil_x_sway
        left_hand_y = gun_base_y - 70 + recoil_y
        
        # Left forearm
        left_arm_points = [
            (left_hand_x - 50, H),
            (left_hand_x - 38, H),
            (left_hand_x + 15, left_hand_y + 50),
            (left_hand_x + 3, left_hand_y + 50)
        ]
        
        # Arm gradient (darker on edges)
        pygame.draw.polygon(screen, (130, 110, 90), left_arm_points)
        pygame.draw.polygon(screen, (90, 75, 60), left_arm_points, 4)
        
        # Arm shading
        shade_points = [
            (left_hand_x - 45, H),
            (left_hand_x - 40, H),
            (left_hand_x + 5, left_hand_y + 50),
            (left_hand_x + 3, left_hand_y + 50)
        ]
        pygame.draw.polygon(screen, (100, 85, 70), shade_points)
        
        # Left palm
        palm_rect = pygame.Rect(left_hand_x - 18, left_hand_y + 30, 50, 40)
        pygame.draw.ellipse(screen, (155, 135, 115), palm_rect)
        pygame.draw.ellipse(screen, (115, 95, 80), palm_rect, 3)
        
        # Palm shading
        shade_rect = palm_rect.inflate(-10, -10)
        pygame.draw.ellipse(screen, (135, 115, 95), shade_rect)
        
        # Left fingers (gripping foregrip)
        finger_data = [
            (left_hand_x - 12, left_hand_y + 32, 9, 28, -8),   # Thumb
            (left_hand_x + 0, left_hand_y + 28, 8, 32, 0),      # Index
            (left_hand_x + 12, left_hand_y + 30, 8, 30, 3),     # Middle
            (left_hand_x + 23, left_hand_y + 33, 7, 26, 5)      # Ring
        ]
        
        for fx, fy, fw, fh, angle in finger_data:
            # Finger base
            finger_surf = pygame.Surface((fw, fh), pygame.SRCALPHA)
            pygame.draw.rect(finger_surf, (145, 125, 105), (0, 0, fw, fh), border_radius=3)
            pygame.draw.rect(finger_surf, (105, 85, 70), (0, 0, fw, fh), 2, border_radius=3)
            
            # Knuckle lines
            for knuckle_y in [fh // 3, fh * 2 // 3]:
                pygame.draw.line(finger_surf, (115, 95, 80), (2, knuckle_y), (fw - 2, knuckle_y), 1)
            
            # Rotate and blit
            if angle != 0:
                finger_surf = pygame.transform.rotate(finger_surf, angle)
            
            screen.blit(finger_surf, (fx, fy))
        
        # ═══ RIGHT HAND (TRIGGER HAND) ═══
        right_hand_x = gun_base_x + 60 - recoil_x_sway
        right_hand_y = gun_base_y - 50 + recoil_y
        
        # Right forearm
        right_arm_points = [
            (right_hand_x + 50, H),
            (right_hand_x + 62, H),
            (right_hand_x + 25, right_hand_y + 60),
            (right_hand_x + 13, right_hand_y + 60)
        ]
        
        pygame.draw.polygon(screen, (130, 110, 90), right_arm_points)
        pygame.draw.polygon(screen, (90, 75, 60), right_arm_points, 4)
        
        # Arm shading
        shade_points = [
            (right_hand_x + 55, H),
            (right_hand_x + 60, H),
            (right_hand_x + 23, right_hand_y + 60),
            (right_hand_x + 20, right_hand_y + 60)
        ]
        pygame.draw.polygon(screen, (100, 85, 70), shade_points)
        
        # Right palm
        palm_rect = pygame.Rect(right_hand_x - 12, right_hand_y + 42, 48, 38)
        pygame.draw.ellipse(screen, (155, 135, 115), palm_rect)
        pygame.draw.ellipse(screen, (115, 95, 80), palm_rect, 3)
        
        shade_rect = palm_rect.inflate(-8, -8)
        pygame.draw.ellipse(screen, (135, 115, 95), shade_rect)
        
        # Right fingers (wrapped around grip)
        # Thumb
        thumb_rect = pygame.Rect(right_hand_x + 25, right_hand_y + 35, 10, 30)
        pygame.draw.rect(screen, (145, 125, 105), thumb_rect, border_radius=4)
        pygame.draw.rect(screen, (105, 85, 70), thumb_rect, 2, border_radius=4)
        pygame.draw.line(screen, (115, 95, 80), (thumb_rect.left + 3, thumb_rect.centery), 
                        (thumb_rect.right - 3, thumb_rect.centery), 1)
        
        # Fingers wrapped around grip
        grip_fingers = [
            (right_hand_x - 8, right_hand_y + 40, 8, 28),
            (right_hand_x + 2, right_hand_y + 38, 8, 30),
            (right_hand_x + 12, right_hand_y + 40, 7, 27)
        ]
        
        for gfx, gfy, gfw, gfh in grip_fingers:
            pygame.draw.rect(screen, (145, 125, 105), (gfx, gfy, gfw, gfh), border_radius=3)
            pygame.draw.rect(screen, (105, 85, 70), (gfx, gfy, gfw, gfh), 2, border_radius=3)
            
            # Knuckles
            for knuckle_y in [gfy + gfh // 3, gfy + gfh * 2 // 3]:
                pygame.draw.line(screen, (115, 95, 80), (gfx + 2, knuckle_y), (gfx + gfw - 2, knuckle_y), 1)
        
        # Trigger finger
        trigger_y_base = right_hand_y + 25
        trigger_extend = 5 if self._gun_recoil > 0.4 else 0
        
        trigger_finger_rect = pygame.Rect(right_hand_x + 35, trigger_y_base + trigger_extend, 9, 24)
        pygame.draw.rect(screen, (145, 125, 105), trigger_finger_rect, border_radius=4)
        pygame.draw.rect(screen, (105, 85, 70), trigger_finger_rect, 2, border_radius=4)
        
        # Finger joint
        pygame.draw.line(screen, (115, 95, 80), 
                        (trigger_finger_rect.left + 2, trigger_finger_rect.top + 12),
                        (trigger_finger_rect.right - 2, trigger_finger_rect.top + 12), 1)
        
        # ═══ GUN WEAPON (SHOTGUN STYLE) ═══
        gun_y = gun_base_y - 110 + recoil_y
        gun_x = gun_base_x + recoil_x_sway
        
        # === DOUBLE BARREL ===
        barrel_length = 200
        barrel_spacing = 4
        
        # Upper barrel
        upper_barrel = pygame.Rect(gun_x - 18, gun_y - 26, barrel_length, 17)
        pygame.draw.rect(screen, (55, 60, 70), upper_barrel, border_radius=3)
        pygame.draw.rect(screen, (75, 80, 90), upper_barrel, 3, border_radius=3)
        
        # Barrel highlight
        pygame.draw.rect(screen, (85, 90, 100), (upper_barrel.x + 5, upper_barrel.y + 3, barrel_length - 10, 5))
        
        # Lower barrel
        lower_barrel = pygame.Rect(gun_x - 18, gun_y - 26 + 17 + barrel_spacing, barrel_length, 17)
        pygame.draw.rect(screen, (55, 60, 70), lower_barrel, border_radius=3)
        pygame.draw.rect(screen, (75, 80, 90), lower_barrel, 3, border_radius=3)
        
        pygame.draw.rect(screen, (85, 90, 100), (lower_barrel.x + 5, lower_barrel.y + 3, barrel_length - 10, 5))
        
        # Barrel bands
        for band_x in [gun_x + 45, gun_x + 95, gun_x + 150]:
            band_rect = pygame.Rect(band_x, gun_y - 30, 10, 46)
            pygame.draw.rect(screen, (45, 50, 60), band_rect)
            pygame.draw.rect(screen, (65, 70, 80), band_rect, 2)
        
        # === RECEIVER/ACTION ===
        receiver_x = gun_x - 40
        receiver_y = gun_y - 18
        receiver_w = 75
        receiver_h = 44
        
        receiver_rect = pygame.Rect(receiver_x, receiver_y, receiver_w, receiver_h)
        pygame.draw.rect(screen, (65, 70, 80), receiver_rect, border_radius=6)
        pygame.draw.rect(screen, (85, 90, 100), receiver_rect, 3, border_radius=6)
        
        # Receiver details
        detail_rect = pygame.Rect(receiver_x + 8, receiver_y + 8, receiver_w - 16, receiver_h - 16)
        pygame.draw.rect(screen, (75, 80, 90), detail_rect, border_radius=4)
        pygame.draw.rect(screen, (55, 60, 70), detail_rect, 2, border_radius=4)
        
        # Ejection port
        port_rect = pygame.Rect(receiver_x + 15, receiver_y + 5, 25, 12)
        pygame.draw.rect(screen, (30, 35, 45), port_rect, border_radius=3)
        pygame.draw.rect(screen, (50, 55, 65), port_rect, 1, border_radius=3)
        
        # === PUMP ACTION (FOREGRIP) ===
        pump_offset = int(self._gun_recoil * 25)
        pump_x = gun_x - 25 - pump_offset
        pump_y = gun_y - 8
        pump_w = 40
        pump_h = 24
        
        pump_rect = pygame.Rect(pump_x, pump_y, pump_w, pump_h)
        pygame.draw.rect(screen, (75, 80, 90), pump_rect, border_radius=5)
        pygame.draw.rect(screen, (55, 60, 70), pump_rect, 3, border_radius=5)
        
        # Pump grooves
        for groove_i in range(5):
            groove_x = pump_x + 5 + groove_i * 7
            pygame.draw.line(screen, (55, 60, 70), (groove_x, pump_y + 5), (groove_x, pump_y + pump_h - 5), 2)
        
        # === TRIGGER ASSEMBLY ===
        # Trigger guard
        guard_x = gun_x + 25
        guard_y = gun_y + 8
        
        pygame.draw.arc(screen, (65, 70, 80), 
                       (guard_x, guard_y, 35, 32), 
                       0, math.pi, 5)
        
        # Trigger
        trigger_pull = 6 if self._gun_recoil > 0.4 else 0
        trigger_rect = pygame.Rect(guard_x + 13, guard_y + 18 + trigger_pull, 7, 14)
        pygame.draw.rect(screen, (160, 140, 120), trigger_rect, border_radius=3)
        pygame.draw.rect(screen, (120, 100, 80), trigger_rect, 2, border_radius=3)
        
        # === STOCK ===
        stock_points = [
            (gun_x + 70, gun_y - 5),
            (gun_x + 165, gun_y - 10),
            (gun_x + 165, gun_y + 30),
            (gun_x + 70, gun_y + 25)
        ]
        
        # Stock body (wood texture)
        pygame.draw.polygon(screen, (90, 70, 50), stock_points)
        pygame.draw.polygon(screen, (70, 55, 40), stock_points, 4)
        
        # Wood grain
        for grain_i in range(4):
            grain_start_x = gun_x + 75 + grain_i * 22
            grain_end_x = gun_x + 155 + grain_i * 3
            grain_y = gun_y + 5 + grain_i * 5
            
            pygame.draw.line(screen, (80, 60, 45), 
                           (grain_start_x, grain_y), 
                           (grain_end_x, grain_y + 8), 2)
        
        # Stock buttplate
        buttplate_rect = pygame.Rect(gun_x + 155, gun_y - 12, 15, 44)
        pygame.draw.rect(screen, (60, 50, 40), buttplate_rect, border_radius=3)
        pygame.draw.rect(screen, (90, 75, 60), buttplate_rect, 2, border_radius=3)
        
        # === MUZZLE FLASH ===
        if show_flash and self._muzzle_flash_timer > 0:
            flash_x = gun_x - 18 - 50
            flash_y = gun_y - 8
            
            flash_intensity = self._muzzle_flash_timer / 0.15
            
            # Large expanding flash
            for radius in range(70, 15, -12):
                alpha = int(flash_intensity * 255 * (radius / 70))
                flash_color = (255, 240, 120) if radius > 40 else (255, 200, 80)
                
                flash_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(flash_surf, (*flash_color, alpha), (radius, radius), radius)
                screen.blit(flash_surf, (flash_x - radius, flash_y - radius))
            
            # Flash rays (random)
            num_rays = 16
            for ray_i in range(num_rays):
                angle = (ray_i / num_rays) * 2 * math.pi + random.uniform(-0.2, 0.2)
                length = random.randint(50, 95)
                width = random.randint(3, 7)
                
                end_x = flash_x + math.cos(angle) * length
                end_y = flash_y + math.sin(angle) * length
                
                ray_alpha = int(flash_intensity * 220)
                ray_surf = pygame.Surface((5, length), pygame.SRCALPHA)
                pygame.draw.line(ray_surf, (255, 240, 150, ray_alpha), (2, 0), (2, length), width)
                
                ray_surf = pygame.transform.rotate(ray_surf, -math.degrees(angle) - 90)
                screen.blit(ray_surf, (flash_x - ray_surf.get_width() // 2, flash_y - ray_surf.get_height() // 2))
            
            # Bright core
            core_size = int(18 * flash_intensity)
            pygame.draw.circle(screen, (255, 255, 230), (flash_x, flash_y), core_size)
            pygame.draw.circle(screen, (255, 240, 150), (flash_x, flash_y), core_size - 5)
            
            # Smoke puffs (if late in flash)
            if self._muzzle_flash_timer < 0.08:
                for puff_i in range(3):
                    puff_offset = puff_i * 15 + random.randint(-5, 5)
                    puff_x = flash_x - 70 - puff_offset
                    puff_y = flash_y + random.randint(-10, 10)
                    puff_size = 15 + puff_i * 8
                    
                    puff_alpha = int((0.08 - self._muzzle_flash_timer) / 0.08 * 80)
                    puff_surf = pygame.Surface((puff_size * 2, puff_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(puff_surf, (100, 100, 100, puff_alpha), (puff_size, puff_size), puff_size)
                    screen.blit(puff_surf, (puff_x - puff_size, puff_y - puff_size))
        
        # === AMMO COUNTER (HUD STYLE) ===
        ammo_bg_rect = pygame.Rect(W - 220, H - 75, 200, 60)
        pygame.draw.rect(screen, (20, 25, 35), ammo_bg_rect, border_radius=8)
        pygame.draw.rect(screen, (0, 180, 255), ammo_bg_rect, 3, border_radius=8)
        
        ammo_label = self.tiny_font.render("SHELLS", True, (150, 180, 255))
        screen.blit(ammo_label, (W - 210, H - 68))
        
        ammo_count = self.large_font.render("50", True, (255, 200, 0))
        screen.blit(ammo_count, (W - 150, H - 60))

    # Legacy compatibility
    def draw_gun(self, screen, show_flash=False):
        self.draw_gun_doom(screen, show_flash)

    # ══════════════════════════════════════════════════════════
    #   NAME INPUT SCREEN (DOOM STYLE)
    # ══════════════════════════════════════════════════════════
    def draw_name_input(self, screen, player_name):
        """DOOM-style name input screen với hiệu ứng sci-fi đầy đủ"""
        W, H = self.width, self.height
        t = pygame.time.get_ticks()
        
        # ═══ ANIMATED BACKGROUND (DOOM CORRIDOR) ═══
        for y in range(H):
            shade = int(15 + (y / H) * 25)
            pygame.draw.line(screen, (shade, shade, shade + 5), (0, y), (W, y))
        
        horizon_y = H // 2
        for i in range(12):
            y_pos = horizon_y + 20 + i * 35
            alpha = max(0, 200 - i * 15)
            grid_width = int(W * 0.7 * (1 - i / 15))
            
            line_surf = pygame.Surface((grid_width, 2), pygame.SRCALPHA)
            line_surf.fill((0, 150, 255, alpha))
            screen.blit(line_surf, ((W - grid_width) // 2, y_pos))
        
        for i in range(-4, 5):
            x_offset = i * 80
            start_y = horizon_y + 20
            for j in range(10):
                y1 = start_y + j * 35
                y2 = y1 + 30
                
                perspective_factor = 1 - (j / 12)
                x1 = W // 2 + int(x_offset * perspective_factor)
                x2 = W // 2 + int(x_offset * perspective_factor * 0.95)
                
                alpha = max(0, 180 - j * 18)
                if alpha > 0:
                    try:
                        pygame.draw.line(screen, (0, 100, 200), (x1, y1), (x2, y2), 1)
                    except:
                        pass
        
        # Wall panels
        for wall_x in [100, W - 150]:
            for panel_y in range(100, H - 100, 120):
                panel_rect = pygame.Rect(wall_x, panel_y, 45, 100)
                pygame.draw.rect(screen, (60, 65, 75), panel_rect)
                pygame.draw.rect(screen, (80, 85, 95), panel_rect, 2)
                
                light_on = (t // 500 + panel_y // 120) % 3 == 0
                light_color = (0, 255, 150) if light_on else (0, 80, 50)
                pygame.draw.rect(screen, light_color, (wall_x + 15, panel_y + 15, 15, 8))
        
        # Top banner
        banner_height = 100
        banner_surf = pygame.Surface((W, banner_height), pygame.SRCALPHA)
        for i in range(banner_height):
            alpha = int(220 * (1 - i / banner_height * 0.3))
            pygame.draw.rect(banner_surf, (20, 25, 35, alpha), (0, i, W, 1))
        screen.blit(banner_surf, (0, 0))
        
        bracket_color = (0, 255, 200)
        for bx, flip in [(20, False), (W - 80, True)]:
            bracket_points = [
                (bx, 20),
                (bx + (60 if not flip else -60), 20),
                (bx + (50 if not flip else -50), 30),
                (bx + (10 if not flip else -10), 30),
                (bx + (10 if not flip else -10), 70),
                (bx, 70)
            ]
            pygame.draw.lines(screen, bracket_color, False, bracket_points, 3)
        
        # Title
        title_text = "ENTER YOUR NAME"
        title_surf = self.title_font.render(title_text, True, (255, 255, 255))
        
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            shadow_surf = self.title_font.render(title_text, True, (100, 0, 0))
            screen.blit(shadow_surf, (W // 2 - title_surf.get_width() // 2 + offset[0], 35 + offset[1]))
        
        screen.blit(title_surf, title_surf.get_rect(center=(W // 2, 37)))
        
        subtitle = self.medium_font.render("MARINE REGISTRATION", True, (150, 180, 255))
        screen.blit(subtitle, subtitle.get_rect(center=(W // 2, 85)))
        
        # Main input panel
        panel_w = 700
        panel_h = 280
        panel_x = (W - panel_w) // 2
        panel_y = 180
        
        for i in range(4):
            glow_rect = pygame.Rect(panel_x - i * 3, panel_y - i * 3, panel_w + i * 6, panel_h + i * 6)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (0, 150, 255, max(0, 40 - i * 10)), 
                           (0, 0, glow_rect.width, glow_rect.height), border_radius=15)
            screen.blit(glow_surf, glow_rect.topleft)
        
        pygame.draw.rect(screen, (25, 30, 45), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
        pygame.draw.rect(screen, (0, 200, 255), (panel_x, panel_y, panel_w, panel_h), 4, border_radius=12)
        pygame.draw.rect(screen, (0, 100, 180), (panel_x + 3, panel_y + 3, panel_w - 6, panel_h - 6), 2, border_radius=10)
        
        corner_size = 25
        for cx, cy in [(panel_x, panel_y), (panel_x + panel_w, panel_y),
                       (panel_x, panel_y + panel_h), (panel_x + panel_w, panel_y + panel_h)]:
            x_offset = -corner_size if cx == panel_x else 0
            y_offset = -corner_size if cy == panel_y else 0
            
            corner_rect = pygame.Rect(cx + x_offset, cy + y_offset, corner_size, corner_size)
            pygame.draw.lines(screen, (255, 200, 0), False, [
                (corner_rect.left, corner_rect.centery),
                (corner_rect.left, corner_rect.top),
                (corner_rect.centerx, corner_rect.top)
            ], 3)
        
        instruction = self.small_font.render("MARINE NAME:", True, (255, 200, 100))
        screen.blit(instruction, (panel_x + 30, panel_y + 30))
        
        # Input box
        input_w = panel_w - 60
        input_h = 70
        input_x = panel_x + 30
        input_y = panel_y + 75
        
        for scan_y in range(input_h):
            if scan_y % 3 == 0:
                alpha = 180
            else:
                alpha = 200
            pygame.draw.rect(screen, (15, 20, 30), (input_x, input_y + scan_y, input_w, 1))
        
        pygame.draw.rect(screen, (0, 255, 200), (input_x, input_y, input_w, input_h), 3)
        pygame.draw.rect(screen, (0, 180, 150), (input_x + 2, input_y + 2, input_w - 4, input_h - 4), 1)
        
        cursor_visible = (t // 400) % 2 == 0
        display_text = player_name + ("|" if cursor_visible else " ")
        
        text_surf = self.large_font.render(display_text, True, (0, 255, 200))
        
        for i in range(2):
            glow_surf = self.large_font.render(display_text, True, (0, 200, 150))
            glow_alpha = max(0, 80 - i * 40)
            glow_surface = pygame.Surface((text_surf.get_width(), text_surf.get_height()), pygame.SRCALPHA)
            glow_surface.blit(glow_surf, (0, 0))
            glow_surface.set_alpha(glow_alpha)
            screen.blit(glow_surface, (input_x + 20 - i, input_y + 16 - i))
        
        screen.blit(text_surf, (input_x + 20, input_y + 16))
        
        char_count_text = f"{len(player_name)}/20"
        char_surf = self.tiny_font.render(char_count_text, True, (150, 150, 180))
        screen.blit(char_surf, (input_x + input_w - 70, input_y + input_h + 8))
        
        # Info panel
        info_y = input_y + input_h + 35
        
        info_items = [
            ("STATUS:", "AWAITING INPUT", (255, 200, 0)),
            ("CLEARANCE:", "LEVEL 1 MARINE", (100, 255, 150)),
            ("MISSION:", "MONSTER HUNT", (255, 100, 100))
        ]
        
        for i, (label, value, color) in enumerate(info_items):
            info_x = panel_x + 30 + (i * 210)
            
            label_surf = self.micro_font.render(label, True, (150, 150, 180))
            screen.blit(label_surf, (info_x, info_y))
            
            value_surf = self.tiny_font.render(value, True, color)
            screen.blit(value_surf, (info_x, info_y + 18))
        
        # Buttons
        button_y = panel_y + panel_h + 40
        
        back_x = W // 2 - 330
        self._draw_doom_button(screen, "< ABORT", back_x, button_y, 280, 75, 
                              (150, 50, 50), (200, 70, 70), "back", t)
        
        start_x = W // 2 + 50
        if player_name.strip():
            self._draw_doom_button(screen, "START >", start_x, button_y, 280, 75,
                                  (0, 180, 100), (0, 230, 130), "confirm", t, pulse=True)
        else:
            pygame.draw.rect(screen, (40, 40, 50), (start_x, button_y, 280, 75), border_radius=8)
            pygame.draw.rect(screen, (80, 80, 90), (start_x, button_y, 280, 75), 3, border_radius=8)
            
            text_surf = self.medium_font.render("START >", True, (100, 100, 120))
            screen.blit(text_surf, text_surf.get_rect(center=(start_x + 140, button_y + 37)))
            
            self.buttons["confirm"] = (start_x, button_y, 280, 75)
        
        # Warning stripes
        stripe_y = H - 60
        stripe_h = 50
        
        stripe_offset = (t // 50) % 40
        for x in range(-40, W + 40, 40):
            stripe_x = x + stripe_offset
            
            points = [
                (stripe_x, stripe_y),
                (stripe_x + 30, stripe_y),
                (stripe_x + 20, stripe_y + stripe_h),
                (stripe_x - 10, stripe_y + stripe_h)
            ]
            
            stripe_color = (200, 180, 0) if (stripe_x // 40) % 2 == 0 else (40, 40, 50)
            pygame.draw.polygon(screen, stripe_color, points)
        
        warning_text = "! AUTHORIZED PERSONNEL ONLY !"
        warning_blink = (t // 600) % 2 == 0
        if warning_blink:
            warning_surf = self.small_font.render(warning_text, True, (255, 50, 50))
            screen.blit(warning_surf, warning_surf.get_rect(center=(W // 2, stripe_y + stripe_h // 2)))
    
    def _draw_doom_button(self, screen, text, x, y, w, h, base_color, hover_color, button_id, time_ms, pulse=False):
        """Vẽ button theo phong cách DOOM"""
        mx, my = pygame.mouse.get_pos()
        is_hover = (x <= mx <= x + w and y <= my <= y + h)
        
        if pulse:
            pulse_value = int(abs(math.sin(time_ms / 200)) * 50)
            color = tuple(min(255, c + pulse_value) for c in base_color)
        else:
            color = hover_color if is_hover else base_color
        
        if is_hover or pulse:
            for i in range(4):
                glow_rect = pygame.Rect(x - i * 2, y - i * 2, w + i * 4, h + i * 4)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                alpha = 60 - i * 15 if is_hover else 40 - i * 10
                pygame.draw.rect(glow_surf, (*color, max(0, alpha)), 
                               (0, 0, glow_rect.width, glow_rect.height), border_radius=10)
                screen.blit(glow_surf, glow_rect.topleft)
        
        pygame.draw.rect(screen, color, (x, y, w, h), border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 3, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 120), (x + 2, y + 2, w - 4, h - 4), 1, border_radius=7)
        
        highlight_rect = pygame.Rect(x + 8, y + 8, w - 16, h // 3)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 40), 
                        (0, 0, highlight_rect.width, highlight_rect.height), border_radius=5)
        screen.blit(highlight_surf, highlight_rect.topleft)
        
        text_surf = self.medium_font.render(text, True, (255, 255, 255))
        shadow_surf = self.medium_font.render(text, True, (0, 0, 0))
        screen.blit(shadow_surf, (x + w // 2 - text_surf.get_width() // 2 + 2, 
                                 y + h // 2 - text_surf.get_height() // 2 + 2))
        screen.blit(text_surf, text_surf.get_rect(center=(x + w // 2, y + h // 2)))
        
        if pulse:
            arrow_alpha = int(abs(math.sin(time_ms / 150)) * 200 + 55)
            for arrow_x in [x - 30, x + w + 15]:
                arrow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                arrow_dir = 1 if arrow_x > x else -1
                
                arrow_points = [
                    (10 - arrow_dir * 8, 0),
                    (10 + arrow_dir * 8, 10),
                    (10 - arrow_dir * 8, 20)
                ]
                
                pygame.draw.polygon(arrow_surf, (255, 255, 200, arrow_alpha), arrow_points)
                screen.blit(arrow_surf, (arrow_x, y + h // 2 - 10))
        
        self.buttons[button_id] = (x, y, w, h)

    # ══════════════════════════════════════════════════════════
    #   MENU, HUD, AND OTHER UI SCREENS
    # ══════════════════════════════════════════════════════════
    def draw_menu(self,screen,question_count):
        t=self.title_font.render("Monster Quiz Shooter",True,(255,215,0))
        screen.blit(t,t.get_rect(center=(self.width//2,150)))
        bw,bh,bx=400,80,self.width//2-200
        self.draw_button(screen,"BAT DAU",       bx,300,bw,bh,(0,180,0),  (0,220,0),  "start")
        self.draw_button(screen,"QUAN LY FILE",  bx,400,bw,bh,(0,100,200),(0,130,230),"upload")
        self.draw_button(screen,"BANG XEP HANG", bx,500,bw,bh,(200,150,0),(230,180,0),"ranking")
        ct=self.safe_render(self.small_font,f"Tong cau hoi: {question_count}",(200,200,200))
        screen.blit(ct,ct.get_rect(center=(self.width//2,610)))

    def draw_hud(self,screen,player_name,score,hp,wrong,max_wrong,monsters_killed):
        pygame.draw.rect(screen,(0,0,0,180),pygame.Rect(10,10,280,120),border_radius=10)
        screen.blit(self.safe_render(self.small_font, player_name,      (255,255,255)),(20,20))
        screen.blit(self.safe_render(self.medium_font,f"Score: {score}", (255,215,0)), (20,55))
        screen.blit(self.safe_render(self.small_font, f"Quai: {monsters_killed}",(100,255,100)),(20,95))
        pygame.draw.rect(screen,(0,0,0,180),pygame.Rect(self.width//2-150,10,300,80),border_radius=10)
        hl=self.safe_render(self.small_font,"HP Quai",(255,255,255))
        screen.blit(hl,hl.get_rect(center=(self.width//2,25)))
        bw2,bh2,bx2,by2=260,30,self.width//2-130,50
        pygame.draw.rect(screen,(70,70,70),(bx2,by2,bw2,bh2),border_radius=5)
        pygame.draw.rect(screen,(220,50,50) if hp>30 else (255,100,0),(bx2,by2,int(bw2*hp/100),bh2),border_radius=5)
        pygame.draw.rect(screen,(255,255,255),(bx2,by2,bw2,bh2),2,border_radius=5)
        ht=self.safe_render(self.small_font,f"{int(hp)}%",(255,255,255))
        screen.blit(ht,ht.get_rect(center=(self.width//2,by2+bh2//2)))
        pygame.draw.rect(screen,(0,0,0,180),pygame.Rect(self.width-160,10,150,90),border_radius=10)
        screen.blit(self.safe_render(self.small_font,f"Sai: {wrong}/{max_wrong}",(255,255,255)),(self.width-145,20))
        for i in range(max_wrong):
            hc=(100,100,100) if i<wrong else (255,50,50)
            hx=self.width-140+i*40; hy=65
            pygame.draw.circle(screen,hc,(hx,hy),12)
            pygame.draw.circle(screen,hc,(hx+15,hy),12)
            pygame.draw.polygon(screen,hc,[(hx-12,hy),(hx+7,hy+25),(hx+27,hy)])

    def draw_question_panel(self,screen,question,target_part,selected_answer,
                            selected_answers,user_input,show_feedback,is_correct):
        PH=440; PY=self.height-PH
        for i in range(PH):
            s=pygame.Surface((self.width,1),pygame.SRCALPHA)
            s.fill((0,0,0,int(238*(1-i/PH*0.25)))); screen.blit(s,(0,PY+i))
        gl=pygame.Surface((self.width,3),pygame.SRCALPHA)
        pygame.draw.rect(gl,(100,150,255,180),(0,0,self.width,3)); screen.blit(gl,(0,PY))

        lvl,bc="NHAN BIET",(0,180,0)
        if   target_part=="head":  lvl,bc="VAN DUNG",  (200,50,50)
        elif target_part=="body":  lvl,bc="THONG HIEU",(200,150,0)
        badge=self.safe_render(self.small_font,lvl,(255,255,255))
        br=badge.get_rect(topleft=(50,PY+12))
        bgr=pygame.Rect(br.x-10,br.y-5,br.width+20,br.height+10)
        pygame.draw.rect(screen,bc,bgr,border_radius=15)
        pygame.draw.rect(screen,(255,255,255),bgr,2,border_radius=15)
        screen.blit(badge,br)

        q_type=question.get('type','multiple_choice')
        tl={'multiple_choice':"TRAC NGHIEM",'true_false':"DUNG / SAI",'short_answer':"TRA LOI NGAN"}
        ts=self.safe_render(self.tiny_font,tl.get(q_type,"TRAC NGHIEM"),(150,200,255))
        screen.blit(ts,(br.right+18,PY+15))

        yp=PY+46
        if question.get('context'):
            for line in self.wrap_text(question['context'],self.micro_font,self.width-120)[:2]:
                s=self.safe_render(self.micro_font,line,(175,175,198))
                screen.blit(s,(50,yp)); yp+=19
            yp+=3

        for line in self.wrap_text(question['question'],self.small_font,self.width-340)[:3]:
            s=self.safe_render(self.small_font,line,(255,255,255))
            screen.blit(s,(50,yp)); yp+=30
        yp+=5

        if   q_type=='multiple_choice': self.draw_multiple_choice(screen,question,selected_answer,selected_answers,show_feedback,yp)
        elif q_type=='true_false':      self.draw_true_false(screen,question,selected_answers,show_feedback,yp)
        elif q_type=='short_answer':    self.draw_short_answer(screen,question,user_input,show_feedback,is_correct,yp)

    def draw_multiple_choice(self,screen,question,selected_answer,selected_answers,show_feedback,y_pos):
        FA=310; cw=(self.width-100-FA-20)//2; AH=65; AX=50; SP=10
        answers=question.get('answers',[])
        if not answers: return
        for i,ans in enumerate(answers):
            txt=ans.get('text',str(ans)) if isinstance(ans,dict) else str(ans)
            x=AX+(i%2)*(cw+SP); y=y_pos+(i//2)*(AH+SP); cor=question.get('correct')
            if show_feedback:
                if i==cor:                  col2,gc=(0,200,100),(0,255,150)
                elif i in selected_answers: col2,gc=(220,60,60),(255,100,100)
                else:                       col2,gc=(50,50,70),None
            else:
                col2,gc=((70,120,255),(100,150,255)) if i in selected_answers else ((60,60,80),None)
            if gc:
                for j in range(3):
                    gr=pygame.Rect(x-j*2,y-j*2,cw+j*4,AH+j*4)
                    gs=pygame.Surface((gr.width,gr.height),pygame.SRCALPHA)
                    pygame.draw.rect(gs,(*gc,max(0,40-j*12)),(0,0,gr.width,gr.height),border_radius=12)
                    screen.blit(gs,gr.topleft)
            pygame.draw.rect(screen,col2,(x,y,cw,AH),border_radius=10)
            pygame.draw.rect(screen,(255,255,255) if i in selected_answers else (100,100,130),(x,y,cw,AH),2,border_radius=10)
            lines=self.wrap_text(f"{chr(65+i)}. {txt}",self.tiny_font,cw-28)
            ly=y+8
            for li,line in enumerate(lines[:2]):
                s=self.safe_render(self.tiny_font,line,(255,255,255))
                if s.get_width()>cw-14: s=self.safe_render(self.micro_font,line,(255,255,255))
                screen.blit(s,(x+14,ly)); ly+=s.get_height()+2
            self.buttons[f"answer_{i}"]=(x,y,cw,AH)
        if not show_feedback: self._fire_btn(screen,len(selected_answers)>0)

    def draw_true_false(self,screen,question,selected_answers,show_feedback,y_pos):
        screen.blit(self.safe_render(self.tiny_font,"Chon tat ca nhan dinh DUNG:",(255,200,100)),(50,y_pos-26))
        answers=question.get('answers',[]); ci=question.get('correct_answers',[question.get('correct')])
        ci=[c for c in (ci or []) if c is not None]
        if not answers: return
        FA=310; CB=30; PAD=9; AX=50; AW=self.width-AX-FA-20
        TX_OFF=CB+22; TX_MAX=AW-TX_OFF-18; LH=self.tiny_font.get_height()+2; curr_y=y_pos
        for i,ans in enumerate(answers):
            txt=ans.get('text',str(ans)) if isinstance(ans,dict) else str(ans)
            lines=self.wrap_text(txt,self.tiny_font,TX_MAX); n=min(len(lines),3)
            item_h=max(CB+PAD*2,n*LH+PAD*2+4)
            is_sel=i in selected_answers; is_cor=i in ci
            if show_feedback:
                if is_cor:   col2,gc=(0,200,100),(0,255,150)
                elif is_sel: col2,gc=(220,60,60),(255,100,100)
                else:        col2,gc=(50,50,70),None
            else:
                col2,gc=((70,120,255),(100,150,255)) if is_sel else ((60,60,80),None)
            if gc:
                for j in range(2):
                    gr=pygame.Rect(AX-j*2,curr_y-j*2,AW+j*4,item_h+j*4)
                    gs=pygame.Surface((gr.width,gr.height),pygame.SRCALPHA)
                    pygame.draw.rect(gs,(*gc,max(0,50-j*20)),(0,0,gr.width,gr.height),border_radius=10)
                    screen.blit(gs,gr.topleft)
            pygame.draw.rect(screen,col2,(AX,curr_y,AW,item_h),border_radius=10)
            pygame.draw.rect(screen,(255,255,255) if is_sel else (100,100,130),(AX,curr_y,AW,item_h),2,border_radius=10)
            cb_y=curr_y+(item_h-CB)//2
            pygame.draw.rect(screen,(40,40,60),(AX+10,cb_y,CB,CB),border_radius=5)
            pygame.draw.rect(screen,(100,200,255) if is_sel else (100,100,120),(AX+10,cb_y,CB,CB),2,border_radius=5)
            if is_sel:
                pygame.draw.line(screen,(255,255,255),(AX+16,cb_y+14),(AX+22,cb_y+20),3)
                pygame.draw.line(screen,(255,255,255),(AX+22,cb_y+20),(AX+34,cb_y+8),3)
            text_x=AX+TX_OFF; ty2=curr_y+PAD
            for li,line in enumerate(lines[:3]):
                disp=f"{chr(65+i)}. {line}" if li==0 else f"    {line}"
                s=self.safe_render(self.tiny_font,disp,(255,255,255))
                if s.get_width()>TX_MAX+6: s=self.safe_render(self.micro_font,disp,(255,255,255))
                if s.get_width()>AW-TX_OFF-8:
                    cl=pygame.Rect(text_x,ty2,AW-TX_OFF-8,s.get_height())
                    screen.set_clip(cl); screen.blit(s,(text_x,ty2)); screen.set_clip(None)
                else: screen.blit(s,(text_x,ty2))
                ty2+=LH
            self.buttons[f"answer_{i}"]=(AX,curr_y,AW,item_h); curr_y+=item_h+8
        if not show_feedback: self._fire_btn(screen,len(selected_answers)>0)

    def draw_short_answer(self,screen,question,user_input,show_feedback,is_correct,y_pos):
        iw,ih,ix=660,62,50
        if not show_feedback:
            for j in range(3):
                gr=pygame.Rect(ix-j*2,y_pos-j*2,iw+j*4,ih+j*4)
                gs=pygame.Surface((gr.width,gr.height),pygame.SRCALPHA)
                pygame.draw.rect(gs,(100,150,255,max(0,50-j*15)),(0,0,gr.width,gr.height),border_radius=12)
                screen.blit(gs,gr.topleft)
        bc=(50,50,70) if not show_feedback else ((0,180,100) if is_correct else (200,60,60))
        pygame.draw.rect(screen,bc,(ix,y_pos,iw,ih),border_radius=10)
        pygame.draw.rect(screen,(120,150,255),(ix,y_pos,iw,ih),3,border_radius=10)
        dt=user_input; cur="|" if not show_feedback and pygame.time.get_ticks()%1000<500 else ""
        mw=iw-40
        try:
            ts=self.medium_font.render(dt+cur,True,(255,255,255))
            while ts.get_width()>mw and len(dt)>0:
                dt=dt[1:]; ts=self.medium_font.render(dt+cur,True,(255,255,255))
            screen.blit(ts,(ix+20,y_pos+14))
        except: pass
        hint="Nhap dap an" if not show_feedback else f"Dap an dung: {question.get('correct_answer','')}"
        try: screen.blit(self.safe_render(self.tiny_font,hint,(150,150,180)),(ix,y_pos+ih+6))
        except: pass
        if not show_feedback: self._fire_btn(screen,len(user_input.strip())>0)

    def _fire_btn(self,screen,enabled):
        t=pygame.time.get_ticks()
        sx=self.width-295; sy=self.height-200; sw,sh=255,90
        if enabled:
            pulse=int(abs(math.sin(t/240))*115+80)
            for j in range(5):
                gr=pygame.Rect(sx-j*5,sy-j*5,sw+j*10,sh+j*10)
                gs=pygame.Surface((gr.width,gr.height),pygame.SRCALPHA)
                pygame.draw.rect(gs,(0,min(255,pulse),140,max(0,65-j*14)),(0,0,gr.width,gr.height),border_radius=20)
                screen.blit(gs,gr.topleft)
            col=(0,min(255,175+pulse//4),80); hov=(0,255,140)
        else:
            col=(55,55,75); hov=(55,55,75)
        self.draw_button(screen,"[ BAN! ]",sx,sy,sw,sh,col,hov,"submit")
        if enabled:
            for li in range(3):
                la=int(abs(math.sin((t/195)+li))*255)
                ls=pygame.Surface((20,4),pygame.SRCALPHA); ls.fill((0,255,200,la))
                screen.blit(ls,(sx-25,sy+24+li*18))

    def check_answer_click(self,x,y,answer_count):
        for i in range(answer_count):
            if self.check_button_click(x,y,f"answer_{i}"): return i
        return None

    def draw_result(self,screen,player_name,score,wrong,hp,monsters_killed,won):
        tc=(0,255,0) if won else (255,50,50)
        t=self.title_font.render("CHIEN THANG!" if won else "THAT BAI!",True,tc)
        screen.blit(t,t.get_rect(center=(self.width//2,150)))
        bw,bh,bx,by=500,350,self.width//2-250,250
        pygame.draw.rect(screen,(30,30,50),(bx,by,bw,bh),border_radius=15)
        pygame.draw.rect(screen,(255,255,255),(bx,by,bw,bh),3,border_radius=15)
        yo=by+40
        for txt,col2,dy,fn in [
            (f"Nguoi choi: {player_name}",(255,255,255),  0,self.medium_font),
            (f"Diem: {score}",           (255,215,0),   60,self.large_font),
            (f"Quai tieu diet: {monsters_killed}",(100,255,100),120,self.medium_font),
            (f"Cau sai: {wrong}/2",      (200,200,200),170,self.small_font),
            (f"HP quai con lai: {int(hp)}%",(200,200,200),210,self.small_font),
        ]:
            s=fn.render(txt,True,col2); screen.blit(s,s.get_rect(center=(self.width//2,yo+dy)))
        self.draw_button(screen,"Choi lai",self.width//2-150,620,300,70,(0,180,0),(0,220,0),"menu")

    def draw_ranking(self,screen,rankings):
        t=self.large_font.render("BANG XEP HANG",True,(255,215,0))
        screen.blit(t,t.get_rect(center=(self.width//2,60)))
        self.draw_button(screen,"Reset",self.width-180,50,140,50,(200,50,50),(230,70,70),"reset")
        if not rankings:
            s=self.medium_font.render("Chua co nguoi choi nao",True,(150,150,150))
            screen.blit(s,s.get_rect(center=(self.width//2,self.height//2)))
        else:
            yo=130
            for i,rank in enumerate(rankings):
                rh,ry=70,yo+i*82
                col=[(255,215,0),(192,192,192),(205,127,50)][i] if i<3 else (70,70,70)
                tc2=(0,0,0) if i<3 else (255,255,255)
                pygame.draw.rect(screen,col,(100,ry,self.width-200,rh),border_radius=10)
                pygame.draw.rect(screen,(255,255,255),(100,ry,self.width-200,rh),2,border_radius=10)
                screen.blit(self.large_font.render(f"#{i+1}",True,tc2),(120,ry+15))
                screen.blit(self.medium_font.render(rank['name'],True,tc2),(220,ry+10))
                screen.blit(self.small_font.render(rank['date'][:10],True,tc2 if i<3 else (200,200,200)),(220,ry+45))
                screen.blit(self.small_font.render(f"Quai: {rank.get('monsters_killed',0)}",True,tc2 if i<3 else (100,255,100)),(450,ry+45))
                sc=self.large_font.render(str(rank['score']),True,tc2)
                screen.blit(sc,sc.get_rect(right=self.width-250,centery=ry+rh//2))
                st=self.small_font.render("Thang" if rank['won'] else "Thua",True,
                    (0,100,0) if (rank['won'] and i<3) else ((0,255,0) if rank['won'] else (255,100,100)))
                screen.blit(st,st.get_rect(right=self.width-130,centery=ry+rh//2))
        self.draw_button(screen,"Quay lai",self.width//2-150,self.height-100,300,60,(0,100,200),(0,130,230),"back")

    def draw_file_manager(self,screen,files):
        t=self.large_font.render("Quan ly File De",True,(255,255,255))
        screen.blit(t,t.get_rect(center=(self.width//2,80)))
        self.draw_button(screen,"Tai len file moi (.txt)",self.width//2-250,150,500,60,(0,100,200),(0,130,230),"upload")
        if not files:
            s=self.medium_font.render("Chua co file nao duoc tai len",True,(150,150,150))
            screen.blit(s,s.get_rect(center=(self.width//2,self.height//2)))
        else:
            yo=240
            for i,file in enumerate(files):
                fy=yo+i*90
                pygame.draw.rect(screen,(50,50,70),(100,fy,self.width-200,75),border_radius=10)
                pygame.draw.rect(screen,(100,100,150),(100,fy,self.width-200,75),2,border_radius=10)
                screen.blit(self.medium_font.render(file['name'],True,(255,255,255)),(120,fy+15))
                screen.blit(self.small_font.render(f"{file['question_count']} cau hoi - {file['upload_date'][:10]}",True,(200,200,200)),(120,fy+48))
                self.draw_button(screen,"Xoa",self.width-180,fy+17,100,40,(200,50,50),(230,70,70),f"delete_{i}")
        self.draw_button(screen,"Quay lai",self.width//2-150,self.height-100,300,60,(100,100,100),(130,130,130),"back")

    def check_file_delete_click(self,x,y,file_count):
        for i in range(file_count):
            if self.check_button_click(x,y,f"delete_{i}"): return i
        return None