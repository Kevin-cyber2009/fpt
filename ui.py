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
    #   ★★★ ULTRA BEAUTIFUL DOOM BACKGROUND ★★★
    #   3D Perspective Corridor - Retro FPS Style
    # ══════════════════════════════════════════════════════════
    def draw_background(self, screen):
        """
        DOOM/Quake style 3D corridor với:
        - Perspective walls với vanishing point
        - Metal panels với rivets, lights
        - Hexagonal floor tiles
        - Volumetric ceiling lights
        - Atmospheric depth fog
        - Industrial doorway nơi monster đứng
        """
        W, H = self.width, self.height
        t = pygame.time.get_ticks()
        
        # ═══ CEILING GRADIENT (DARK SKY) ═══
        for y in range(H // 2):
            progress = y / (H / 2)
            r = int(8 + progress * 14)
            g = int(10 + progress * 16)
            b = int(18 + progress * 24)
            pygame.draw.line(screen, (r, g, b), (0, y), (W, y))
        
        # ═══ FLOOR GRADIENT (PERSPECTIVE DARKENING) ═══
        for y in range(H // 2, H):
            progress = (y - H/2) / (H/2)
            base = int(22 + progress * 42)
            pygame.draw.line(screen, (base, base - 4, base - 10), (0, y), (W, y))
        
        horizon_y = H // 2
        vanish_x = W // 2
        vanish_y = horizon_y
        
        # ═══ PERSPECTIVE CORRIDOR WALLS ═══
        # Left wall với perspective
        wall_left_near = int(W * 0.02)
        wall_left_far = int(W * 0.22)
        
        left_wall = [
            (0, 0),
            (wall_left_far, vanish_y - 135),
            (wall_left_far, vanish_y + 135),
            (wall_left_near, H)
        ]
        
        # Right wall với perspective
        wall_right_near = int(W * 0.98)
        wall_right_far = int(W * 0.78)
        
        right_wall = [
            (W, 0),
            (wall_right_far, vanish_y - 135),
            (wall_right_far, vanish_y + 135),
            (wall_right_near, H)
        ]
        
        # Draw walls với shading
        pygame.draw.polygon(screen, (48, 53, 62), left_wall)
        pygame.draw.polygon(screen, (44, 49, 58), right_wall)
        pygame.draw.polygon(screen, (68, 73, 82), left_wall, 3)
        pygame.draw.polygon(screen, (64, 69, 78), right_wall, 3)
        
        # Inner shadow cho depth
        shadow_left = [
            (left_wall[1][0] - 12, left_wall[1][1]),
            (left_wall[2][0] - 12, left_wall[2][1]),
            (left_wall[3][0] + 25, left_wall[3][1]),
            (left_wall[0][0] + 25, left_wall[0][1])
        ]
        shadow_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(shadow_surf, (0, 0, 0, 70), shadow_left)
        screen.blit(shadow_surf, (0, 0))
        
        shadow_right = [
            (right_wall[1][0] + 12, right_wall[1][1]),
            (right_wall[2][0] + 12, right_wall[2][1]),
            (right_wall[3][0] - 25, right_wall[3][1]),
            (right_wall[0][0] - 25, right_wall[0][1])
        ]
        shadow_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(shadow_surf, (0, 0, 0, 70), shadow_right)
        screen.blit(shadow_surf, (0, 0))
        
        # ═══ DETAILED WALL PANELS với RIVETS ═══
        num_panels = 10
        for i in range(num_panels):
            depth = i / num_panels
            
            # Calculate panel position với perspective
            panel_y_top = int(vanish_y - 115 + (H * 0.2 - vanish_y + 115) * depth)
            panel_y_bot = int(vanish_y + 115 + (H - vanish_y - 115) * depth)
            
            if panel_y_bot >= H or panel_y_top < 0:
                continue
            
            panel_h = panel_y_bot - panel_y_top
            
            # Left panels
            panel_x_l = int(wall_left_near + (wall_left_far - wall_left_near) * (1 - depth))
            panel_w_l = max(28, int(48 * (1 - depth * 0.65)))
            
            if panel_x_l > 15 and panel_x_l < W * 0.35:
                self._draw_industrial_panel(screen, panel_x_l - panel_w_l, panel_y_top,
                                            panel_w_l, panel_h, depth, t, i, True)
            
            # Right panels
            panel_x_r = int(wall_right_near + (wall_right_far - wall_right_near) * (1 - depth))
            panel_w_r = max(28, int(48 * (1 - depth * 0.65)))
            
            if panel_x_r < W - 15 and panel_x_r > W * 0.65:
                self._draw_industrial_panel(screen, panel_x_r, panel_y_top,
                                            panel_w_r, panel_h, depth, t, i, False)
        
        # ═══ VOLUMETRIC CEILING LIGHTS ═══
        num_lights = 7
        for i in range(num_lights):
            depth = i / num_lights
            light_y = int(vanish_y - 165 + (20 - vanish_y + 165) * depth)
            
            if light_y > -60 and light_y < H // 2:
                light_scale = 1.0 - depth * 0.75
                light_x = vanish_x
                
                fixture_w = int(95 * light_scale)
                fixture_h = int(24 * light_scale)
                
                if fixture_w > 18:
                    self._draw_volumetric_light(screen, light_x, light_y, 
                                                fixture_w, fixture_h, depth, t, i)
        
        # ═══ HEXAGONAL FLOOR GRID ═══
        grid_start_y = vanish_y + 145
        hex_base_size = 48
        
        for row in range(9):
            row_depth = row / 9
            row_y = int(grid_start_y + row * 38 + row_depth * 25)
            
            if row_y <= H // 2 or row_y >= H:
                continue
            
            scale = 1.0 - row_depth * 0.55
            hex_size = int(hex_base_size * scale)
            num_hex = int(6 + row * 0.9)
            
            for col in range(-num_hex // 2, num_hex // 2 + 1):
                hex_x = int(vanish_x + col * hex_size * 1.65 * scale)
                
                if -hex_size < hex_x < W + hex_size:
                    self._draw_hex_tile(screen, hex_x, row_y, hex_size, row_depth, t, row, col)
        
        # ═══ ATMOSPHERIC FOG OVERLAY ═══
        fog_surf = pygame.Surface((W, H // 3), pygame.SRCALPHA)
        for y in range(H // 3):
            alpha = int((y / (H // 3)) * 55)
            pygame.draw.line(fog_surf, (12, 16, 24, alpha), (0, y), (W, y))
        screen.blit(fog_surf, (0, 0))
        
        # ═══ INDUSTRIAL DOORWAY (Monster Portal) ═══
        door_w = 250
        door_h = 275
        door_x = (W - door_w) // 2
        door_y = vanish_y - door_h // 2
        
        # Thick metal frame
        frame_t = 14
        frame_color = (40, 45, 54)
        
        frame_outer = pygame.Rect(door_x - frame_t, door_y - frame_t,
                                  door_w + frame_t * 2, door_h + frame_t * 2)
        pygame.draw.rect(screen, frame_color, frame_outer, border_radius=6)
        pygame.draw.rect(screen, (60, 65, 74), frame_outer, 3, border_radius=6)
        
        # Frame inner edge highlight
        frame_inner = frame_outer.inflate(-6, -6)
        pygame.draw.rect(screen, (28, 33, 42), frame_inner, 2, border_radius=4)
        
        # Dark portal interior (gradient)
        interior_surf = pygame.Surface((door_w, door_h), pygame.SRCALPHA)
        for y in range(door_h):
            darkness = int(6 + (y / door_h) * 8)
            pygame.draw.line(interior_surf, (darkness, darkness + 1, darkness + 4), 
                           (0, y), (door_w, y))
        screen.blit(interior_surf, (door_x, door_y))
        
        # Blinking warning lights (red)
        for side, offset_x in [("left", -30), ("right", door_w + 18)]:
            light_x = door_x + offset_x
            light_y = door_y + 30
            
            blink = (t // 420 + (0 if side == "left" else 1)) % 2
            
            if blink:
                light_color = (255, 42, 42)
                
                # Light housing
                pygame.draw.circle(screen, (78, 26, 26), (light_x, light_y), 13)
                pygame.draw.circle(screen, light_color, (light_x, light_y), 10)
                pygame.draw.circle(screen, (255, 95, 95), (light_x - 2, light_y - 2), 5)
                
                # Volumetric glow layers
                for j in range(5):
                    glow_r = 28 + j * 15
                    alpha = 125 - j * 30
                    
                    glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*light_color, alpha), 
                                     (glow_r, glow_r), glow_r)
                    screen.blit(glow_surf, (light_x - glow_r, light_y - glow_r))
            else:
                pygame.draw.circle(screen, (78, 26, 26), (light_x, light_y), 13)
                pygame.draw.circle(screen, (95, 16, 16), (light_x, light_y), 10)
        
        # Animated hazard stripes
        stripe_w = 32
        stripe_offset = (t // 95) % (stripe_w * 2)
        
        for stripe_y_pos in [door_y - 11, door_y + door_h + 3]:
            num_stripes = (door_w // stripe_w) + 3
            
            for i in range(-1, num_stripes):
                stripe_x = door_x + i * stripe_w * 2 - stripe_offset
                
                if door_x - frame_t <= stripe_x + stripe_w and stripe_x < door_x + door_w + frame_t:
                    # Yellow stripe
                    pygame.draw.rect(screen, (215, 195, 0), 
                                   (stripe_x, stripe_y_pos, stripe_w, 8))
                    # Black stripe
                    pygame.draw.rect(screen, (38, 38, 48), 
                                   (stripe_x + stripe_w, stripe_y_pos, stripe_w, 8))
        
        # Blinking warning text
        if (t // 750) % 2 == 0:
            warning = self.tiny_font.render("⚠ DANGER ZONE ⚠", True, (255, 195, 0))
            screen.blit(warning, warning.get_rect(center=(door_x + door_w // 2, door_y - 28)))
    
    def _draw_industrial_panel(self, screen, x, y, w, h, depth, time_ms, index, is_left):
        """Vẽ wall panel với industrial details"""
        if h < 12 or w < 12:
            return
        
        panel_rect = pygame.Rect(int(x), int(y), int(w), int(h))
        
        # Panel base color với depth darkening
        dark_factor = 1.0 - depth * 0.35
        base_r = int(58 * dark_factor)
        base_g = int(64 * dark_factor)
        base_b = int(74 * dark_factor)
        
        # Panel body
        pygame.draw.rect(screen, (base_r, base_g, base_b), panel_rect)
        pygame.draw.rect(screen, (40, 46, 56), panel_rect, 
                        max(1, int(3 * (1 - depth * 0.5))))
        
        # Panel segments (horizontal divisions)
        if h > 45:
            num_seg = max(2, int(3 * (1 - depth * 0.45)))
            seg_h = h // num_seg
            
            for seg_i in range(num_seg):
                seg_y = int(y + 10 + seg_i * seg_h)
                seg_height = max(6, int(seg_h - 15))
                
                if seg_height > 0:
                    seg_rect = pygame.Rect(int(x + 6), seg_y, 
                                          max(1, int(w - 12)), seg_height)
                    pygame.draw.rect(screen, (base_r + 12, base_g + 12, base_b + 12), seg_rect)
                    pygame.draw.rect(screen, (base_r - 10, base_g - 10, base_b - 10), seg_rect, 1)
        
        # Rivets (bolts)
        if w > 22 and h > 38:
            rivet_positions = [
                (x + w * 0.18, y + h * 0.18),
                (x + w * 0.82, y + h * 0.18),
                (x + w * 0.18, y + h * 0.82),
                (x + w * 0.82, y + h * 0.82)
            ]
            
            rivet_r = max(2, int(5 * (1 - depth * 0.65)))
            for rx, ry in rivet_positions:
                # Rivet head
                pygame.draw.circle(screen, (82, 88, 98), (int(rx), int(ry)), rivet_r)
                # Rivet center
                pygame.draw.circle(screen, (36, 42, 52), (int(rx), int(ry)), 
                                 max(1, rivet_r - 2))
        
        # Blinking indicator light
        if h > 32:
            light_phase = (time_ms // 580 + index) % 4
            
            if light_phase == 0:
                light_color = (0, 255, 135)
                light_y = int(y + h * 0.14)
                light_x = int(x + w // 2)
                light_w = max(4, int(19 * (1 - depth * 0.55)))
                light_h = max(3, int(10 * (1 - depth * 0.55)))
                
                # Light bar
                pygame.draw.rect(screen, light_color, 
                               (light_x - light_w // 2, light_y, light_w, light_h))
                
                # Light glow
                if light_w > 6:
                    glow_surf = pygame.Surface((light_w * 2, light_h * 2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (*light_color, 110), 
                                   (light_w // 2, light_h // 2, light_w, light_h))
                    screen.blit(glow_surf, (light_x - light_w, light_y - light_h // 2))
    
    def _draw_volumetric_light(self, screen, x, y, w, h, depth, time_ms, index):
        """Vẽ ceiling light với volumetric glow"""
        fixture_rect = pygame.Rect(int(x - w // 2), int(y), int(w), int(h))
        
        # Light fixture body
        darkness = 1.0 - depth * 0.45
        fixture_color = (int(68 * darkness), int(74 * darkness), int(84 * darkness))
        fixture_edge = (int(88 * darkness), int(94 * darkness), int(104 * darkness))
        
        pygame.draw.rect(screen, fixture_color, fixture_rect)
        pygame.draw.rect(screen, fixture_edge, fixture_rect, 
                        max(1, int(2 * (1 - depth * 0.5))))
        
        # Volumetric light cone (multiple layers for depth)
        num_layers = max(4, int(6 * (1 - depth * 0.5)))
        
        for layer in range(num_layers):
            glow_w = int(w * 0.85 + layer * (38 * (1 - depth * 0.35)))
            glow_h = int(h + layer * (20 * (1 - depth * 0.35)))
            alpha = int((150 - layer * 30) * (1 - depth * 0.35))
            
            if alpha > 0:
                glow_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
                pygame.draw.ellipse(glow_surf, (195, 215, 255, alpha), 
                                  (0, 0, glow_w, glow_h))
                screen.blit(glow_surf, (int(x - glow_w // 2), int(y + h - 6)))
    
    def _draw_hex_tile(self, screen, cx, cy, size, depth, time_ms, row, col):
        """Vẽ hexagonal floor tile"""
        if size < 6:
            return
        
        # Hexagon points
        points = []
        for i in range(6):
            angle = math.radians(60 * i + 30)
            px = cx + int(math.cos(angle) * size)
            py = cy + int(math.sin(angle) * size)
            points.append((px, py))
        
        # Tile color với depth darkening
        darkness = 1.0 - depth * 0.52
        tile_r = int(35 * darkness)
        tile_g = int(39 * darkness)
        tile_b = int(49 * darkness)
        
        # Subtle pattern variation
        pattern = (row + col) % 3
        if pattern == 1:
            tile_r += 4
            tile_g += 4
        elif pattern == 2:
            tile_b += 5
        
        # Draw hexagon
        pygame.draw.polygon(screen, (tile_r, tile_g, tile_b), points)
        pygame.draw.polygon(screen, (tile_r + 10, tile_g + 10, tile_b + 14), points, 
                          max(1, int(2 * (1 - depth * 0.45))))
        
        # Inner detail line
        if size > 14:
            inner_points = []
            for i in range(6):
                angle = math.radians(60 * i + 30)
                px = cx + int(math.cos(angle) * size * 0.68)
                py = cy + int(math.sin(angle) * size * 0.68)
                inner_points.append((px, py))
            
            pygame.draw.polygon(screen, (tile_r + 6, tile_g + 6, tile_b + 10), 
                              inner_points, 1)

    # ══════════════════════════════════════════════════════════
    #   ★★★ ULTRA REALISTIC FIRST-PERSON GUN ★★★
    #   Detailed hands + weapon như DOOM classic
    # ══════════════════════════════════════════════════════════
    def draw_gun_doom(self, screen, show_flash=False):
        """Vẽ súng first-person với tay cầm chi tiết siêu đẹp"""
        W, H = self.width, self.height
        t = pygame.time.get_ticks()
        
        # Update animation timers
        if self._muzzle_flash_timer > 0:
            self._muzzle_flash_timer -= 1/60.0
            show_flash = True
        
        # Smooth recoil decay
        self._gun_recoil = max(0, self._gun_recoil - 0.08)
        self._gun_kickback = max(0, self._gun_kickback - 2.0)
        
        # Gun base position
        gun_base_x = W // 2
        gun_base_y = H - 58 + int(self._gun_kickback)
        
        # Recoil offset
        recoil_y = int(-self._gun_recoil * 42)
        recoil_sway = math.sin(self._gun_recoil * 3.2) * 6
        
        # ═══ LEFT HAND (Supporting hand) ═══
        lh_x = gun_base_x - 135 + int(recoil_sway)
        lh_y = gun_base_y - 72 + recoil_y
        
        # Left forearm
        lf_points = [
            (lh_x - 52, H),
            (lh_x - 39, H),
            (lh_x + 16, lh_y + 52),
            (lh_x + 2, lh_y + 52)
        ]
        pygame.draw.polygon(screen, (132, 112, 92), lf_points)
        pygame.draw.polygon(screen, (88, 72, 58), lf_points, 4)
        
        # Arm muscle shading
        shade_points = [
            (lh_x - 46, H),
            (lh_x - 41, H),
            (lh_x + 6, lh_y + 52),
            (lh_x + 3, lh_y + 52)
        ]
        pygame.draw.polygon(screen, (102, 87, 72), shade_points)
        
        # Left palm
        palm_rect = pygame.Rect(lh_x - 20, lh_y + 31, 52, 42)
        pygame.draw.ellipse(screen, (158, 138, 118), palm_rect)
        pygame.draw.ellipse(screen, (118, 98, 82), palm_rect, 3)
        
        # Palm detail (lighter center)
        detail_rect = palm_rect.inflate(-11, -11)
        pygame.draw.ellipse(screen, (138, 118, 98), detail_rect)
        
        # Left fingers (gripping foregrip)
        fingers_left = [
            (lh_x - 13, lh_y + 33, 10, 30, -9),   # Thumb
            (lh_x + 1, lh_y + 29, 9, 34, 0),      # Index
            (lh_x + 13, lh_y + 31, 9, 32, 3),     # Middle
            (lh_x + 25, lh_y + 34, 8, 28, 6)      # Ring
        ]
        
        for fx, fy, fw, fh, angle in fingers_left:
            # Finger surface
            f_surf = pygame.Surface((fw, fh), pygame.SRCALPHA)
            pygame.draw.rect(f_surf, (148, 128, 108), (0, 0, fw, fh), border_radius=3)
            pygame.draw.rect(f_surf, (108, 88, 72), (0, 0, fw, fh), 2, border_radius=3)
            
            # Knuckle lines
            for knuckle in [fh // 3, fh * 2 // 3]:
                pygame.draw.line(f_surf, (118, 98, 82), (2, knuckle), (fw - 2, knuckle), 1)
            
            # Rotate and draw
            if angle != 0:
                f_surf = pygame.transform.rotate(f_surf, angle)
            screen.blit(f_surf, (fx, fy))
        
        # ═══ RIGHT HAND (Trigger hand) ═══
        rh_x = gun_base_x + 62 - int(recoil_sway)
        rh_y = gun_base_y - 52 + recoil_y
        
        # Right forearm
        rf_points = [
            (rh_x + 52, H),
            (rh_x + 64, H),
            (rh_x + 26, rh_y + 62),
            (rh_x + 14, rh_y + 62)
        ]
        pygame.draw.polygon(screen, (132, 112, 92), rf_points)
        pygame.draw.polygon(screen, (88, 72, 58), rf_points, 4)
        
        # Arm shading
        shade_r = [
            (rh_x + 57, H),
            (rh_x + 62, H),
            (rh_x + 24, rh_y + 62),
            (rh_x + 21, rh_y + 62)
        ]
        pygame.draw.polygon(screen, (102, 87, 72), shade_r)
        
        # Right palm
        palm_r = pygame.Rect(rh_x - 13, rh_y + 43, 50, 40)
        pygame.draw.ellipse(screen, (158, 138, 118), palm_r)
        pygame.draw.ellipse(screen, (118, 98, 82), palm_r, 3)
        
        detail_r = palm_r.inflate(-9, -9)
        pygame.draw.ellipse(screen, (138, 118, 98), detail_r)
        
        # Right thumb
        thumb_r = pygame.Rect(rh_x + 26, rh_y + 36, 11, 32)
        pygame.draw.rect(screen, (148, 128, 108), thumb_r, border_radius=4)
        pygame.draw.rect(screen, (108, 88, 72), thumb_r, 2, border_radius=4)
        pygame.draw.line(screen, (118, 98, 82), 
                        (thumb_r.left + 3, thumb_r.centery), 
                        (thumb_r.right - 3, thumb_r.centery), 1)
        
        # Grip fingers
        grip_fingers = [
            (rh_x - 9, rh_y + 41, 9, 30),
            (rh_x + 2, rh_y + 39, 9, 32),
            (rh_x + 13, rh_y + 41, 8, 29)
        ]
        
        for gx, gy, gw, gh in grip_fingers:
            pygame.draw.rect(screen, (148, 128, 108), (gx, gy, gw, gh), border_radius=3)
            pygame.draw.rect(screen, (108, 88, 72), (gx, gy, gw, gh), 2, border_radius=3)
            
            # Knuckles
            for k_y in [gy + gh // 3, gy + gh * 2 // 3]:
                pygame.draw.line(screen, (118, 98, 82), (gx + 2, k_y), (gx + gw - 2, k_y), 1)
        
        # Trigger finger
        trigger_base_y = rh_y + 26
        trigger_ext = 6 if self._gun_recoil > 0.4 else 0
        
        tf_rect = pygame.Rect(rh_x + 37, trigger_base_y + trigger_ext, 10, 26)
        pygame.draw.rect(screen, (148, 128, 108), tf_rect, border_radius=4)
        pygame.draw.rect(screen, (108, 88, 72), tf_rect, 2, border_radius=4)
        pygame.draw.line(screen, (118, 98, 82), 
                        (tf_rect.left + 2, tf_rect.top + 13),
                        (tf_rect.right - 2, tf_rect.top + 13), 1)
        
        # ═══ DOUBLE BARREL SHOTGUN ═══
        gun_y = gun_base_y - 112 + recoil_y
        gun_x = gun_base_x + int(recoil_sway)
        
        # === BARRELS ===
        barrel_len = 205
        barrel_gap = 5
        
        # Upper barrel
        ub_rect = pygame.Rect(gun_x - 19, gun_y - 27, barrel_len, 18)
        pygame.draw.rect(screen, (53, 58, 68), ub_rect, border_radius=3)
        pygame.draw.rect(screen, (73, 78, 88), ub_rect, 3, border_radius=3)
        
        # Barrel highlight
        pygame.draw.rect(screen, (83, 88, 98), 
                        (ub_rect.x + 6, ub_rect.y + 4, barrel_len - 12, 6))
        
        # Lower barrel
        lb_rect = pygame.Rect(gun_x - 19, gun_y - 27 + 18 + barrel_gap, barrel_len, 18)
        pygame.draw.rect(screen, (53, 58, 68), lb_rect, border_radius=3)
        pygame.draw.rect(screen, (73, 78, 88), lb_rect, 3, border_radius=3)
        
        pygame.draw.rect(screen, (83, 88, 98), 
                        (lb_rect.x + 6, lb_rect.y + 4, barrel_len - 12, 6))
        
        # Barrel bands (metal rings)
        for band_x in [gun_x + 48, gun_x + 100, gun_x + 155]:
            band_rect = pygame.Rect(band_x, gun_y - 31, 11, 48)
            pygame.draw.rect(screen, (43, 48, 58), band_rect)
            pygame.draw.rect(screen, (63, 68, 78), band_rect, 2)
        
        # === RECEIVER ===
        rec_x = gun_x - 42
        rec_y = gun_y - 19
        rec_w = 78
        rec_h = 46
        
        rec_rect = pygame.Rect(rec_x, rec_y, rec_w, rec_h)
        pygame.draw.rect(screen, (63, 68, 78), rec_rect, border_radius=6)
        pygame.draw.rect(screen, (83, 88, 98), rec_rect, 3, border_radius=6)
        
        # Receiver details
        detail_r = pygame.Rect(rec_x + 9, rec_y + 9, rec_w - 18, rec_h - 18)
        pygame.draw.rect(screen, (73, 78, 88), detail_r, border_radius=4)
        pygame.draw.rect(screen, (53, 58, 68), detail_r, 2, border_radius=4)
        
        # Ejection port
        port = pygame.Rect(rec_x + 16, rec_y + 6, 27, 13)
        pygame.draw.rect(screen, (28, 33, 43), port, border_radius=3)
        pygame.draw.rect(screen, (48, 53, 63), port, 1, border_radius=3)
        
        # === PUMP FOREGRIP ===
        pump_push = int(self._gun_recoil * 28)
        pump_x = gun_x - 28 - pump_push
        pump_y = gun_y - 9
        pump_w = 43
        pump_h = 26
        
        pump_rect = pygame.Rect(pump_x, pump_y, pump_w, pump_h)
        pygame.draw.rect(screen, (73, 78, 88), pump_rect, border_radius=5)
        pygame.draw.rect(screen, (53, 58, 68), pump_rect, 3, border_radius=5)
        
        # Pump grooves
        for g_i in range(6):
            groove_x = pump_x + 6 + g_i * 6
            pygame.draw.line(screen, (53, 58, 68), 
                           (groove_x, pump_y + 6), 
                           (groove_x, pump_y + pump_h - 6), 2)
        
        # === TRIGGER ASSEMBLY ===
        # Trigger guard
        guard_x = gun_x + 27
        guard_y = gun_y + 9
        
        pygame.draw.arc(screen, (63, 68, 78), 
                       (guard_x, guard_y, 37, 34), 
                       0, math.pi, 5)
        
        # Trigger
        trigger_pull = 7 if self._gun_recoil > 0.4 else 0
        trigger_rect = pygame.Rect(guard_x + 14, guard_y + 19 + trigger_pull, 8, 15)
        pygame.draw.rect(screen, (165, 145, 125), trigger_rect, border_radius=3)
        pygame.draw.rect(screen, (125, 105, 85), trigger_rect, 2, border_radius=3)
        
        # === WOODEN STOCK ===
        stock_points = [
            (gun_x + 72, gun_y - 6),
            (gun_x + 170, gun_y - 11),
            (gun_x + 170, gun_y + 32),
            (gun_x + 72, gun_y + 27)
        ]
        
        # Wood body
        pygame.draw.polygon(screen, (92, 72, 52), stock_points)
        pygame.draw.polygon(screen, (72, 57, 42), stock_points, 4)
        
        # Wood grain texture
        for grain_i in range(5):
            grain_sx = gun_x + 77 + grain_i * 20
            grain_ex = gun_x + 160 + grain_i * 2
            grain_y = gun_y + 6 + grain_i * 5
            
            pygame.draw.line(screen, (82, 62, 47), 
                           (grain_sx, grain_y), 
                           (grain_ex, grain_y + 9), 2)
        
        # Stock buttplate
        buttplate = pygame.Rect(gun_x + 160, gun_y - 13, 16, 46)
        pygame.draw.rect(screen, (62, 52, 42), buttplate, border_radius=3)
        pygame.draw.rect(screen, (92, 77, 62), buttplate, 2, border_radius=3)
        
        # === MUZZLE FLASH & EFFECTS ===
        if show_flash and self._muzzle_flash_timer > 0:
            flash_x = gun_x - 19 - 55
            flash_y = gun_y - 9
            
            flash_intensity = self._muzzle_flash_timer / 0.15
            
            # Large expanding flash core
            for radius in range(75, 18, -13):
                alpha = int(flash_intensity * 255 * (radius / 75))
                flash_color = (255, 238, 125) if radius > 42 else (255, 198, 85)
                
                flash_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(flash_surf, (*flash_color, alpha), (radius, radius), radius)
                screen.blit(flash_surf, (flash_x - radius, flash_y - radius))
            
            # Flash rays (star burst)
            num_rays = 18
            for ray_i in range(num_rays):
                angle = (ray_i / num_rays) * 2 * math.pi + random.uniform(-0.18, 0.18)
                length = random.randint(55, 100)
                width = random.randint(4, 8)
                
                ray_alpha = int(flash_intensity * 230)
                ray_surf = pygame.Surface((6, length), pygame.SRCALPHA)
                pygame.draw.line(ray_surf, (255, 238, 155, ray_alpha), (3, 0), (3, length), width)
                
                ray_surf = pygame.transform.rotate(ray_surf, -math.degrees(angle) - 90)
                screen.blit(ray_surf, (flash_x - ray_surf.get_width() // 2, 
                                      flash_y - ray_surf.get_height() // 2))
            
            # Bright core
            core_size = int(20 * flash_intensity)
            pygame.draw.circle(screen, (255, 255, 235), (flash_x, flash_y), core_size)
            pygame.draw.circle(screen, (255, 238, 155), (flash_x, flash_y), core_size - 6)
            
            # Smoke puffs
            if self._muzzle_flash_timer < 0.09:
                for puff_i in range(4):
                    puff_offset = puff_i * 16 + random.randint(-6, 6)
                    puff_x = flash_x - 75 - puff_offset
                    puff_y = flash_y + random.randint(-12, 12)
                    puff_size = 17 + puff_i * 9
                    
                    puff_alpha = int((0.09 - self._muzzle_flash_timer) / 0.09 * 85)
                    puff_surf = pygame.Surface((puff_size * 2, puff_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(puff_surf, (95, 95, 95, puff_alpha), 
                                     (puff_size, puff_size), puff_size)
                    screen.blit(puff_surf, (puff_x - puff_size, puff_y - puff_size))
        
        # === AMMO COUNTER HUD ===
        ammo_bg = pygame.Rect(W - 225, H - 78, 205, 63)
        pygame.draw.rect(screen, (18, 23, 33), ammo_bg, border_radius=8)
        pygame.draw.rect(screen, (0, 175, 255), ammo_bg, 3, border_radius=8)
        
        ammo_label = self.tiny_font.render("SHELLS", True, (145, 175, 255))
        screen.blit(ammo_label, (W - 215, H - 71))
        
        ammo_count = self.large_font.render("50", True, (255, 195, 0))
        screen.blit(ammo_count, (W - 155, H - 63))

    # Legacy compatibility
    def draw_gun(self, screen, show_flash=False):
        self.draw_gun_doom(screen, show_flash)

    # ══════════════════════════════════════════════════════════
    #   PHẦN CÒN LẠI GIỮ NGUYÊN TỪ CODE GỐC
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
    #   PHẦN CÒN LẠI - GIỐNG HỆT CODE GỐC
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