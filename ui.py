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
                print("OK Font DejaVuSans")
            except:
                self._fallback_fonts()
        else:
            self._fallback_fonts()

        self.buttons = {}

        # Gun animation state
        self._gun_recoil     = 0.0
        self._gun_recoil_x   = 0.0
        self._gun_sway_x     = 0.0
        self._gun_sway_y     = 0.0
        self._gun_tilt       = 0.0
        self._shoot_flash    = 0.0   # 0..1, fades to 0
        self._screen_flash   = 0.0   # 0..1, fades to 0
        self._prev_mouse     = (width // 2, height // 2)

    def _fallback_fonts(self):
        vn = ['dejavusans', 'notosans', 'freesans', 'liberationsans', 'arial', 'tahoma', 'verdana']
        sf = next((f for f in vn if f in pygame.font.get_fonts()), None)
        def mk(s, b=False):
            return pygame.font.SysFont(sf, s, bold=b) if sf else pygame.font.Font(None, s)
        self.title_font  = mk(72, True)
        self.large_font  = mk(48, True)
        self.medium_font = mk(36)
        self.small_font  = mk(28)
        self.tiny_font   = mk(21)
        self.micro_font  = mk(17)

    # ── helpers ──────────────────────────────────────────────────
    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []; cur = []
        for w in words:
            test = ' '.join(cur + [w])
            try:
                if font.size(test)[0] <= max_width:
                    cur.append(w)
                else:
                    if cur: lines.append(' '.join(cur))
                    cur = [w]
            except:
                cur.append(w)
        if cur: lines.append(' '.join(cur))
        return lines or [""]

    def safe_render(self, font, text, color):
        try:
            return font.render(text, True, color)
        except:
            return self.micro_font.render(text, True, color)

    def draw_button(self, screen, text, x, y, w, h, col, hov, bid):
        mx, my = pygame.mouse.get_pos()
        c = hov if (x <= mx <= x + w and y <= my <= y + h) else col
        pygame.draw.rect(screen, c, (x, y, w, h), border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 3, border_radius=10)
        ts = self.safe_render(self.medium_font, text, (255, 255, 255))
        if ts.get_width() > w - 10:
            ts = self.safe_render(self.small_font, text, (255, 255, 255))
        screen.blit(ts, ts.get_rect(center=(x + w // 2, y + h // 2)))
        self.buttons[bid] = (x, y, w, h)

    def check_button_click(self, x, y, bid):
        if bid in self.buttons:
            bx, by, bw, bh = self.buttons[bid]
            return bx <= x <= bx + bw and by <= y <= by + bh
        return False

    def check_answer_click(self, x, y, answer_count):
        for i in range(answer_count):
            if self.check_button_click(x, y, f"answer_{i}"):
                return i
        return None

    # ═══════════════════════════════════════════════════════════
    #   PUBLIC: trigger shoot effect (called AFTER panel hides)
    # ═══════════════════════════════════════════════════════════
    def trigger_shoot_effect(self):
        self._gun_recoil   = 42.0
        self._gun_recoil_x = random.uniform(-7, 7)
        self._shoot_flash  = 1.0
        self._screen_flash = 1.0

    # ═══════════════════════════════════════════════════════════
    #   POV GUN  —  draw every frame
    # ═══════════════════════════════════════════════════════════
    def draw_gun(self, screen, show_flash=False):
        W, H = self.width, self.height
        t = pygame.time.get_ticks()
        mx, my = pygame.mouse.get_pos()

        # Smooth aim sway
        aim_x = (mx - W * 0.5) * 0.038
        aim_y = (my - H * 0.5) * 0.026
        self._gun_sway_x += (aim_x - self._gun_sway_x) * 0.09
        self._gun_sway_y += (aim_y - self._gun_sway_y) * 0.09

        # Tilt by mouse delta
        dx = mx - self._prev_mouse[0]
        target_tilt = dx * 0.32
        self._gun_tilt += (target_tilt - self._gun_tilt) * 0.13
        self._gun_tilt = max(-20.0, min(20.0, self._gun_tilt))
        self._prev_mouse = (mx, my)

        # Recoil decay
        self._gun_recoil   *= 0.70
        self._gun_recoil_x *= 0.70
        self._shoot_flash  = max(0.0, self._shoot_flash - 0.11)
        self._screen_flash = max(0.0, self._screen_flash - 0.07)

        # Breathing
        bob_y = math.sin(t / 920) * 3.8
        bob_x = math.sin(t / 1400) * 2.2

        # ── Screen flash ──
        if self._screen_flash > 0.01:
            fl = pygame.Surface((W, H), pygame.SRCALPHA)
            fl.fill((255, 245, 180, int(self._screen_flash * 60)))
            screen.blit(fl, (0, 0))

        # ── Build gun surface ──
        GW, GH = 660, 420
        gs = pygame.Surface((GW, GH), pygame.SRCALPHA)

        # Pivot = grip bottom (bottom-right of surface)
        PX = GW - 115
        PY = GH - 55

        self._draw_gun_all(gs, PX, PY, t, self._shoot_flash > 0.05)

        # ── Rotate around pivot ──
        rad = math.radians(-self._gun_tilt)
        rotated = pygame.transform.rotate(gs, -self._gun_tilt)

        ox = PX - GW / 2;  oy = PY - GH / 2
        rx = ox * math.cos(rad) - oy * math.sin(rad)
        ry = ox * math.sin(rad) + oy * math.cos(rad)

        # Screen anchor = bottom-right corner area
        BASE_X = W - 35  + self._gun_sway_x + self._gun_recoil_x + bob_x
        BASE_Y = H + 15  + self._gun_sway_y - self._gun_recoil   + bob_y

        blit_x = int(BASE_X - (rotated.get_width()  / 2 + rx))
        blit_y = int(BASE_Y - (rotated.get_height() / 2 + ry))

        screen.blit(rotated, (blit_x, blit_y))

    # ── Master draw: all gun parts in correct z-order ──
    def _draw_gun_all(self, s, PX, PY, t, flash):
        MX = PX - 490   # muzzle x on surface
        MY = PY - 115   # muzzle y (barrel center)

        # Z-order: right arm → barrel+handguard → receiver → stock/grip → optic → left arm → flash
        self._draw_right_arm(s, PX, PY, t)
        self._draw_barrel(s, MX, MY, PX, PY, t)
        self._draw_receiver(s, PX, PY, t)
        self._draw_stock(s, PX, PY, t)
        self._draw_optic(s, PX, PY, t)
        self._draw_left_arm(s, MX, MY, t)
        if flash:
            self._draw_muzzle_flash(s, MX - 8, MY, t)

    # ── BARREL ──
    def _draw_barrel(self, s, MX, MY, PX, PY, t):
        blen = PX - MX - 108

        # Main barrel tube  (gradient fill)
        for row in range(28):
            frac = row / 28
            c = (int(55 + frac * 22), int(65 + frac * 22), int(80 + frac * 22))
            pygame.draw.line(s, c, (MX, MY + 4 + row), (MX + blen, MY + 4 + row))
        pygame.draw.rect(s, (28, 36, 50), pygame.Rect(MX, MY + 4, blen, 28), 2, border_radius=5)

        # Top rail
        rail = pygame.Rect(MX + 8, MY - 2, blen - 16, 10)
        pygame.draw.rect(s, (52, 63, 78), rail)
        for i in range(24):
            rx = rail.left + 5 + i * 19
            pygame.draw.line(s, (33, 42, 56), (rx, rail.top + 1), (rx, rail.bottom - 1), 2)
        pygame.draw.rect(s, (68, 80, 96), rail, 1)

        # Handguard below
        hg = pygame.Rect(MX + 12, MY + 32, 270, 22)
        for row in range(22):
            frac = row / 22
            c = (int(40 + frac * 14), int(48 + frac * 14), int(60 + frac * 14))
            pygame.draw.line(s, c, (hg.left, hg.top + row), (hg.right, hg.top + row))
        pygame.draw.rect(s, (26, 34, 46), hg, 2, border_radius=4)
        for i in range(11):
            sx = hg.left + 6 + i * 23
            pygame.draw.rect(s, (22, 28, 40), (sx, hg.top + 4, 16, 14), border_radius=3)

        # Plasma coils (animated)
        off = (t // 15) % 26
        for ci in range(0, blen - 10, 26):
            cx = MX + (ci + off) % blen
            ca = int(abs(math.sin((ci + t * 0.044) * 0.29)) * 145 + 55)
            ps = pygame.Surface((3, 20), pygame.SRCALPHA)
            ps.fill((0, 195, 255, ca))
            s.blit(ps, (cx, MY + 8))

        # Suppressor
        sup = pygame.Rect(MX - 18, MY - 4, 20, 36)
        for row in range(36):
            frac = row / 36
            c = (int(26 + frac * 16), int(34 + frac * 16), int(46 + frac * 16))
            pygame.draw.line(s, c, (sup.left, sup.top + row), (sup.right, sup.top + row))
        pygame.draw.rect(s, (52, 66, 84), sup, 2, border_radius=4)
        for i in range(3):
            pygame.draw.rect(s, (16, 22, 32), (sup.left + 2, sup.top + 5 + i * 10, sup.width - 4, 7))

    # ── RECEIVER ──
    def _draw_receiver(self, s, PX, PY, t):
        RX = PX - 125; RY = PY - 100
        rec = pygame.Rect(RX, RY, 125, 72)
        for row in range(72):
            frac = row / 72
            c = (int(50 + frac * 24), int(58 + frac * 24), int(74 + frac * 24))
            pygame.draw.line(s, c, (rec.left, rec.top + row), (rec.right, rec.top + row))
        pygame.draw.rect(s, (30, 38, 54), rec, 3, border_radius=8)

        pan = pygame.Rect(RX + 8, RY + 13, 109, 46)
        pygame.draw.rect(s, (36, 44, 60), pan, border_radius=5)
        for li in range(4):
            ly = pan.top + 8 + li * 10
            pygame.draw.line(s, (26, 32, 44), (pan.left + 5, ly), (pan.right - 5, ly), 1)

        for i, lc in enumerate([(0, 255, 100), (255, 200, 0), (0, 170, 255)]):
            lx = RX + 15 + i * 17
            ba = int(abs(math.sin((t / 280) + i)) * 175 + 60)
            bs = pygame.Surface((11, 11), pygame.SRCALPHA)
            bs.fill((*lc, ba))
            s.blit(bs, (lx, RY + 10))

        pygame.draw.rect(s, (22, 28, 42), (RX + 94, RY + 18, 18, 38), border_radius=4)
        for i in range(3):
            pygame.draw.line(s, (60, 74, 94), (RX + 95, RY + 24 + i * 14), (RX + 111, RY + 24 + i * 14), 2)

    # ── STOCK + GRIP + MAGAZINE ──
    def _draw_stock(self, s, PX, PY, t):
        # Pistol grip  (polygon, no alpha issues)
        gp = [(PX - 15, PY - 48), (PX + 11, PY - 46),
              (PX + 17, PY + 36), (PX - 7, PY + 40)]
        pygame.draw.polygon(s, (60, 50, 40), gp)
        pygame.draw.polygon(s, (38, 34, 28), gp, 3)
        for gi in range(10):
            gy = PY - 38 + gi * 8
            pygame.draw.line(s, (48, 42, 36), (PX - 11, gy), (PX + 9, gy + 2), 2)

        # Trigger guard arc
        pygame.draw.arc(s, (32, 40, 52), pygame.Rect(PX - 26, PY - 40, 26, 36), 0, math.pi, 3)

        # Trigger
        pygame.draw.rect(s, (180, 48, 20), (PX - 19, PY - 28, 9, 20), border_radius=4)

        # Buffer tube
        st = pygame.Rect(PX + 11, PY - 58, 72, 26)
        for row in range(26):
            frac = row / 26
            c = (int(46 + frac * 20), int(54 + frac * 20), int(68 + frac * 20))
            pygame.draw.line(s, c, (st.left, st.top + row), (st.right, st.top + row))
        pygame.draw.rect(s, (70, 84, 102), st, 2, border_radius=5)
        pygame.draw.rect(s, (44, 52, 66), (st.right - 15, st.top + 5, 13, 16))

        # Magazine
        mg = pygame.Rect(PX - 70, PY - 9, 32, 60)
        for row in range(60):
            frac = row / 60
            c = (int(48 + frac * 20), int(56 + frac * 20), int(72 + frac * 20))
            pygame.draw.line(s, c, (mg.left, mg.top + row), (mg.right, mg.top + row))
        pygame.draw.rect(s, (0, 175, 230), mg, 2, border_radius=5)
        win = pygame.Rect(mg.x + 5, mg.y + 8, 22, 48)
        pygame.draw.rect(s, (12, 20, 34), win, border_radius=3)
        for i in range(6):
            cy = win.top + 4 + i * 7
            act = i < (6 - (t // 1150) % 7)
            pygame.draw.rect(s, (0, 215, 165) if act else (20, 36, 44),
                             (win.left + 3, cy, 16, 5), border_radius=2)

    # ── OPTIC / SIGHT ──
    def _draw_optic(self, s, PX, PY, t):
        SX = PX - 248; SY = PY - 134
        pygame.draw.rect(s, (48, 60, 78), (SX - 2, SY + 30, 62, 13), border_radius=4)
        sb = pygame.Rect(SX, SY, 58, 32)
        for row in range(32):
            frac = row / 32
            c = (int(46 + frac * 20), int(58 + frac * 20), int(78 + frac * 20))
            pygame.draw.line(s, c, (sb.left, sb.top + row), (sb.right, sb.top + row))
        pygame.draw.rect(s, (0, 165, 245), sb, 2, border_radius=7)
        # Front glass
        pygame.draw.rect(s, (7, 20, 44), (SX + 3, SY + 7, 16, 18), border_radius=4)
        pygame.draw.rect(s, (0, 150, 215), (SX + 3, SY + 7, 16, 18), 2, border_radius=4)
        # Reticle
        rcx = SX + 35; rcy = SY + 16
        pygame.draw.line(s, (0, 225, 255), (rcx - 9, rcy), (rcx + 9, rcy), 1)
        pygame.draw.line(s, (0, 225, 255), (rcx, rcy - 9), (rcx, rcy + 9), 1)
        pygame.draw.circle(s, (255, 45, 45), (rcx, rcy), 3)
        # LED
        pulse = int(abs(math.sin(t / 360)) * 165 + 70)
        ps = pygame.Surface((9, 9), pygame.SRCALPHA)
        ps.fill((0, pulse, 255, 180))
        s.blit(ps, (SX + 47, SY + 12))

    # ── RIGHT ARM (shooting hand) ──
    def _draw_right_arm(self, s, PX, PY, t):
        # Forearm slab coming from bottom-right
        arm = [(PX + 24, PY - 30), (PX + 92, PY - 10),
               (PX + 105, PY + 75), (PX + 32, PY + 88)]
        pygame.draw.polygon(s, (50, 56, 72), arm)
        pygame.draw.polygon(s, (36, 44, 60), arm, 2)
        for i in range(5):
            sy = PY - 20 + i * 23
            pygame.draw.line(s, (42, 48, 64), (PX + 28, sy), (PX + 86, sy + 5), 2)

        # Palm + knuckles
        hand = [(PX + 10, PY - 42), (PX + 36, PY - 44),
                (PX + 40, PY + 16), (PX + 18, PY + 20), (PX + 6, PY)]
        pygame.draw.polygon(s, (64, 72, 90), hand)
        pygame.draw.polygon(s, (46, 54, 70), hand, 2)

        for fi in range(4):
            fr = pygame.Rect(PX + 16, PY - 32 + fi * 14, 24, 12)
            pygame.draw.rect(s, (58, 66, 84), fr, border_radius=4)
            pygame.draw.rect(s, (42, 50, 66), fr, 1, border_radius=4)

        pygame.draw.ellipse(s, (66, 74, 92), (PX + 1, PY - 16, 17, 30))
        pygame.draw.ellipse(s, (48, 56, 72), (PX + 1, PY - 16, 17, 30), 1)

        for i in range(3):
            pygame.draw.rect(s, (74, 84, 106), (PX + 14, PY - 34 + i * 17, 26, 12), border_radius=3)
            pygame.draw.rect(s, (56, 66, 86), (PX + 14, PY - 34 + i * 17, 26, 12), 1, border_radius=3)

    # ── LEFT ARM (supporting, grips handguard) ──
    def _draw_left_arm(self, s, MX, MY, t):
        lx = MX + 210
        ly = MY + 50

        arm = [(lx - 54, ly - 24), (lx + 14, ly - 18),
               (lx + 18, ly + 46), (lx - 50, ly + 38)]
        pygame.draw.polygon(s, (48, 54, 70), arm)
        pygame.draw.polygon(s, (34, 42, 58), arm, 2)
        for i in range(4):
            sy = ly - 12 + i * 19
            pygame.draw.line(s, (40, 46, 62), (lx - 48, sy), (lx + 10, sy + 4), 2)

        hand = [(lx - 18, ly - 28), (lx + 14, ly - 26),
                (lx + 16, ly + 28), (lx - 16, ly + 30), (lx - 24, ly + 10)]
        pygame.draw.polygon(s, (62, 70, 88), hand)
        pygame.draw.polygon(s, (46, 54, 70), hand, 2)

        for fi in range(4):
            fr = pygame.Rect(lx - 16, ly - 18 + fi * 14, 24, 12)
            pygame.draw.rect(s, (58, 66, 84), fr, border_radius=4)
            pygame.draw.rect(s, (42, 50, 66), fr, 1, border_radius=4)

        for i in range(2):
            pygame.draw.rect(s, (72, 82, 104), (lx - 14, ly - 24 + i * 19, 28, 12), border_radius=3)
            pygame.draw.rect(s, (54, 64, 84), (lx - 14, ly - 24 + i * 19, 28, 12), 1, border_radius=3)

    # ── MUZZLE FLASH (Valorant) ──
    def _draw_muzzle_flash(self, s, fx, fy, t):
        # Bright core
        for r in range(85, 4, -15):
            a = int(255 * r / 85)
            fc = (245, 252, 255) if r > 42 else (255, 238, 88)
            ms = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ms, (*fc, a), (r, r), r)
            s.blit(ms, (fx - r, fy - r))

        # Rays
        for i in range(18):
            ang = math.radians(i * 20 + random.randint(-9, 9))
            ln = random.randint(60, 125)
            pygame.draw.line(s, (238, 250, 255),
                             (fx, fy),
                             (fx + int(math.cos(ang) * ln), fy + int(math.sin(ang) * ln)),
                             random.randint(2, 6))

        pygame.draw.circle(s, (255, 255, 255), (fx, fy), 32)
        pygame.draw.circle(s, (205, 238, 255), (fx, fy), 22)
        pygame.draw.circle(s, (255, 250, 125), (fx, fy), 11)

        # Shockwave rings
        for r in [62, 85, 112]:
            ws = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ws, (215, 238, 255, max(0, 105 - r)), (r, r), r, 4)
            s.blit(ws, (fx - r, fy - r))

        # Sparks
        for _ in range(26):
            ang = random.uniform(0, math.pi * 2)
            d = random.randint(75, 165)
            px = fx + int(math.cos(ang) * d)
            py = fy + int(math.sin(ang) * d)
            ps = random.randint(2, 8)
            pygame.draw.circle(s, random.choice([(255, 255, 220), (220, 245, 255), (255, 212, 62)]),
                               (px, py), ps)
            if ps > 4:
                pygame.draw.circle(s, (255, 255, 255), (px, py), ps - 3)

    # ═══════════════════════════════════════════════════════════
    #   MENU / NAME INPUT / HUD
    # ═══════════════════════════════════════════════════════════
    def draw_menu(self, screen, question_count):
        t = self.title_font.render("Monster Quiz Shooter", True, (255, 215, 0))
        screen.blit(t, t.get_rect(center=(self.width // 2, 150)))
        bw, bh, bx = 400, 80, self.width // 2 - 200
        self.draw_button(screen, "BAT DAU",       bx, 300, bw, bh, (0, 180, 0),   (0, 220, 0),   "start")
        self.draw_button(screen, "QUAN LY FILE",  bx, 400, bw, bh, (0, 100, 200), (0, 130, 230), "upload")
        self.draw_button(screen, "BANG XEP HANG", bx, 500, bw, bh, (200, 150, 0), (230, 180, 0), "ranking")
        ct = self.safe_render(self.small_font, f"Tong cau hoi: {question_count}", (200, 200, 200))
        screen.blit(ct, ct.get_rect(center=(self.width // 2, 610)))

    def draw_name_input(self, screen, player_name):
        t = self.large_font.render("Nhap ten cua ban", True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=(self.width // 2, 200)))
        iw, ih, ix, iy = 500, 60, self.width // 2 - 250, 300
        pygame.draw.rect(screen, (50, 50, 70), (ix, iy, iw, ih), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 200), (ix, iy, iw, ih), 3, border_radius=10)
        ts = self.safe_render(self.medium_font, player_name + "|", (255, 255, 255))
        screen.blit(ts, ts.get_rect(midleft=(ix + 20, iy + ih // 2)))
        self.draw_button(screen, "Quay lai", self.width // 2 - 220, 420, 200, 60, (100, 100, 100), (130, 130, 130), "back")
        self.draw_button(screen, "Bat dau",  self.width // 2 + 20,  420, 200, 60, (0, 180, 0),     (0, 220, 0),     "confirm")

    def draw_hud(self, screen, player_name, score, hp, wrong, max_wrong, monsters_killed):
        pygame.draw.rect(screen, (0, 0, 0, 180), pygame.Rect(10, 10, 280, 120), border_radius=10)
        screen.blit(self.safe_render(self.small_font,  player_name,                (255, 255, 255)), (20, 20))
        screen.blit(self.safe_render(self.medium_font, f"Score: {score}",           (255, 215, 0)),   (20, 55))
        screen.blit(self.safe_render(self.small_font,  f"Quai: {monsters_killed}",  (100, 255, 100)), (20, 95))

        pygame.draw.rect(screen, (0, 0, 0, 180), pygame.Rect(self.width // 2 - 150, 10, 300, 80), border_radius=10)
        hl = self.safe_render(self.small_font, "HP Quai", (255, 255, 255))
        screen.blit(hl, hl.get_rect(center=(self.width // 2, 25)))
        bw2, bh2, bx2, by2 = 260, 30, self.width // 2 - 130, 50
        pygame.draw.rect(screen, (70, 70, 70), (bx2, by2, bw2, bh2), border_radius=5)
        pygame.draw.rect(screen, (220, 50, 50) if hp > 30 else (255, 100, 0),
                         (bx2, by2, int(bw2 * hp / 100), bh2), border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), (bx2, by2, bw2, bh2), 2, border_radius=5)
        ht = self.safe_render(self.small_font, f"{int(hp)}%", (255, 255, 255))
        screen.blit(ht, ht.get_rect(center=(self.width // 2, by2 + bh2 // 2)))

        pygame.draw.rect(screen, (0, 0, 0, 180), pygame.Rect(self.width - 160, 10, 150, 90), border_radius=10)
        screen.blit(self.safe_render(self.small_font, f"Sai: {wrong}/{max_wrong}", (255, 255, 255)),
                    (self.width - 145, 20))
        for i in range(max_wrong):
            hc = (100, 100, 100) if i < wrong else (255, 50, 50)
            hx = self.width - 140 + i * 40; hy = 65
            pygame.draw.circle(screen, hc, (hx, hy), 12)
            pygame.draw.circle(screen, hc, (hx + 15, hy), 12)
            pygame.draw.polygon(screen, hc, [(hx - 12, hy), (hx + 7, hy + 25), (hx + 27, hy)])

    # ═══════════════════════════════════════════════════════════
    #   QUESTION PANEL
    # ═══════════════════════════════════════════════════════════
    def draw_question_panel(self, screen, question, target_part, selected_answer,
                            selected_answers, user_input, show_feedback, is_correct):
        PH = 440; PY = self.height - PH
        for i in range(PH):
            srf = pygame.Surface((self.width, 1), pygame.SRCALPHA)
            srf.fill((0, 0, 0, int(238 * (1 - i / PH * 0.25))))
            screen.blit(srf, (0, PY + i))
        gl = pygame.Surface((self.width, 3), pygame.SRCALPHA)
        pygame.draw.rect(gl, (100, 150, 255, 180), (0, 0, self.width, 3))
        screen.blit(gl, (0, PY))

        lvl, bc = "NHAN BIET", (0, 180, 0)
        if   target_part == "head":  lvl, bc = "VAN DUNG",   (200, 50, 50)
        elif target_part == "body":  lvl, bc = "THONG HIEU", (200, 150, 0)
        badge = self.safe_render(self.small_font, lvl, (255, 255, 255))
        br = badge.get_rect(topleft=(50, PY + 12))
        bgr = pygame.Rect(br.x - 10, br.y - 5, br.width + 20, br.height + 10)
        pygame.draw.rect(screen, bc, bgr, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), bgr, 2, border_radius=15)
        screen.blit(badge, br)

        q_type = question.get('type', 'multiple_choice')
        tl = {'multiple_choice': "TRAC NGHIEM", 'true_false': "DUNG / SAI", 'short_answer': "TRA LOI NGAN"}
        ts = self.safe_render(self.tiny_font, tl.get(q_type, "TRAC NGHIEM"), (150, 200, 255))
        screen.blit(ts, (br.right + 18, PY + 15))

        yp = PY + 46
        if question.get('context'):
            for line in self.wrap_text(question['context'], self.micro_font, self.width - 120)[:2]:
                srf = self.safe_render(self.micro_font, line, (175, 175, 198))
                screen.blit(srf, (50, yp)); yp += 19
            yp += 3

        for line in self.wrap_text(question['question'], self.small_font, self.width - 340)[:3]:
            srf = self.safe_render(self.small_font, line, (255, 255, 255))
            screen.blit(srf, (50, yp)); yp += 30
        yp += 5

        if   q_type == 'multiple_choice': self.draw_multiple_choice(screen, question, selected_answer, selected_answers, show_feedback, yp)
        elif q_type == 'true_false':      self.draw_true_false(screen, question, selected_answers, show_feedback, yp)
        elif q_type == 'short_answer':    self.draw_short_answer(screen, question, user_input, show_feedback, is_correct, yp)

    # ── Multiple choice ──
    def draw_multiple_choice(self, screen, question, selected_answer, selected_answers, show_feedback, y_pos):
        FA = 310; cw = (self.width - 100 - FA - 20) // 2; AH = 65; AX = 50; SP = 10
        answers = question.get('answers', [])
        if not answers: return
        for i, ans in enumerate(answers):
            txt = ans.get('text', str(ans)) if isinstance(ans, dict) else str(ans)
            x = AX + (i % 2) * (cw + SP); y = y_pos + (i // 2) * (AH + SP)
            cor = question.get('correct')
            if show_feedback:
                if i == cor:                  col2, gc = (0, 200, 100),  (0, 255, 150)
                elif i in selected_answers:   col2, gc = (220, 60, 60),  (255, 100, 100)
                else:                         col2, gc = (50, 50, 70),    None
            else:
                col2, gc = ((70, 120, 255), (100, 150, 255)) if i in selected_answers else ((60, 60, 80), None)
            if gc:
                for j in range(3):
                    gr = pygame.Rect(x - j*2, y - j*2, cw + j*4, AH + j*4)
                    gs = pygame.Surface((gr.width, gr.height), pygame.SRCALPHA)
                    pygame.draw.rect(gs, (*gc, max(0, 40 - j*12)), (0, 0, gr.width, gr.height), border_radius=12)
                    screen.blit(gs, gr.topleft)
            pygame.draw.rect(screen, col2, (x, y, cw, AH), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255) if i in selected_answers else (100, 100, 130),
                             (x, y, cw, AH), 2, border_radius=10)
            lines = self.wrap_text(f"{chr(65+i)}. {txt}", self.tiny_font, cw - 28)
            ly = y + 8
            for li, line in enumerate(lines[:2]):
                srf = self.safe_render(self.tiny_font, line, (255, 255, 255))
                if srf.get_width() > cw - 14: srf = self.safe_render(self.micro_font, line, (255, 255, 255))
                screen.blit(srf, (x + 14, ly)); ly += srf.get_height() + 2
            self.buttons[f"answer_{i}"] = (x, y, cw, AH)
        if not show_feedback: self._fire_btn(screen, len(selected_answers) > 0)

    # ── True/False ──
    def draw_true_false(self, screen, question, selected_answers, show_feedback, y_pos):
        screen.blit(self.safe_render(self.tiny_font, "Chon tat ca nhan dinh DUNG:", (255, 200, 100)), (50, y_pos - 26))
        answers = question.get('answers', [])
        ci = question.get('correct_answers', [question.get('correct')])
        ci = [c for c in (ci or []) if c is not None]
        if not answers: return
        FA = 310; CB = 30; PAD = 9; AX = 50; AW = self.width - AX - FA - 20
        TX_OFF = CB + 22; TX_MAX = AW - TX_OFF - 18; LH = self.tiny_font.get_height() + 2; curr_y = y_pos
        for i, ans in enumerate(answers):
            txt = ans.get('text', str(ans)) if isinstance(ans, dict) else str(ans)
            lines = self.wrap_text(txt, self.tiny_font, TX_MAX); n = min(len(lines), 3)
            item_h = max(CB + PAD * 2, n * LH + PAD * 2 + 4)
            is_sel = i in selected_answers; is_cor = i in ci
            if show_feedback:
                if is_cor:   col2, gc = (0, 200, 100),  (0, 255, 150)
                elif is_sel: col2, gc = (220, 60, 60),  (255, 100, 100)
                else:        col2, gc = (50, 50, 70),   None
            else:
                col2, gc = ((70, 120, 255), (100, 150, 255)) if is_sel else ((60, 60, 80), None)
            if gc:
                for j in range(2):
                    gr = pygame.Rect(AX - j*2, curr_y - j*2, AW + j*4, item_h + j*4)
                    gs = pygame.Surface((gr.width, gr.height), pygame.SRCALPHA)
                    pygame.draw.rect(gs, (*gc, max(0, 50 - j*20)), (0, 0, gr.width, gr.height), border_radius=10)
                    screen.blit(gs, gr.topleft)
            pygame.draw.rect(screen, col2, (AX, curr_y, AW, item_h), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255) if is_sel else (100, 100, 130),
                             (AX, curr_y, AW, item_h), 2, border_radius=10)
            cb_y = curr_y + (item_h - CB) // 2
            pygame.draw.rect(screen, (40, 40, 60), (AX + 10, cb_y, CB, CB), border_radius=5)
            pygame.draw.rect(screen, (100, 200, 255) if is_sel else (100, 100, 120),
                             (AX + 10, cb_y, CB, CB), 2, border_radius=5)
            if is_sel:
                pygame.draw.line(screen, (255, 255, 255), (AX + 16, cb_y + 14), (AX + 22, cb_y + 20), 3)
                pygame.draw.line(screen, (255, 255, 255), (AX + 22, cb_y + 20), (AX + 34, cb_y + 8), 3)
            text_x = AX + TX_OFF; ty2 = curr_y + PAD
            for li, line in enumerate(lines[:3]):
                disp = f"{chr(65+i)}. {line}" if li == 0 else f"    {line}"
                srf = self.safe_render(self.tiny_font, disp, (255, 255, 255))
                if srf.get_width() > TX_MAX + 6: srf = self.safe_render(self.micro_font, disp, (255, 255, 255))
                if srf.get_width() > AW - TX_OFF - 8:
                    cl = pygame.Rect(text_x, ty2, AW - TX_OFF - 8, srf.get_height())
                    screen.set_clip(cl); screen.blit(srf, (text_x, ty2)); screen.set_clip(None)
                else:
                    screen.blit(srf, (text_x, ty2))
                ty2 += LH
            self.buttons[f"answer_{i}"] = (AX, curr_y, AW, item_h); curr_y += item_h + 8
        if not show_feedback: self._fire_btn(screen, len(selected_answers) > 0)

    # ── Short answer ──
    def draw_short_answer(self, screen, question, user_input, show_feedback, is_correct, y_pos):
        iw, ih, ix = 660, 62, 50
        if not show_feedback:
            for j in range(3):
                gr = pygame.Rect(ix - j*2, y_pos - j*2, iw + j*4, ih + j*4)
                gs = pygame.Surface((gr.width, gr.height), pygame.SRCALPHA)
                pygame.draw.rect(gs, (100, 150, 255, max(0, 50 - j*15)), (0, 0, gr.width, gr.height), border_radius=12)
                screen.blit(gs, gr.topleft)
        bc = (50, 50, 70) if not show_feedback else ((0, 180, 100) if is_correct else (200, 60, 60))
        pygame.draw.rect(screen, bc, (ix, y_pos, iw, ih), border_radius=10)
        pygame.draw.rect(screen, (120, 150, 255), (ix, y_pos, iw, ih), 3, border_radius=10)
        dt = user_input; cur = "|" if not show_feedback and pygame.time.get_ticks() % 1000 < 500 else ""
        mw = iw - 40
        try:
            ts = self.medium_font.render(dt + cur, True, (255, 255, 255))
            while ts.get_width() > mw and len(dt) > 0:
                dt = dt[1:]; ts = self.medium_font.render(dt + cur, True, (255, 255, 255))
            screen.blit(ts, (ix + 20, y_pos + 14))
        except: pass
        hint = "Nhap dap an" if not show_feedback else f"Dap an dung: {question.get('correct_answer', '')}"
        try: screen.blit(self.safe_render(self.tiny_font, hint, (150, 150, 180)), (ix, y_pos + ih + 6))
        except: pass
        if not show_feedback: self._fire_btn(screen, len(user_input.strip()) > 0)

    # ── BAN button ──
    def _fire_btn(self, screen, enabled):
        t = pygame.time.get_ticks()
        sx = self.width - 295; sy = self.height - 200; sw, sh = 255, 90
        if enabled:
            pulse = int(abs(math.sin(t / 240)) * 115 + 80)
            for j in range(5):
                gr = pygame.Rect(sx - j*5, sy - j*5, sw + j*10, sh + j*10)
                gs = pygame.Surface((gr.width, gr.height), pygame.SRCALPHA)
                pygame.draw.rect(gs, (0, min(255, pulse), 140, max(0, 65 - j*14)),
                                 (0, 0, gr.width, gr.height), border_radius=20)
                screen.blit(gs, gr.topleft)
            col = (0, min(255, 175 + pulse // 4), 80); hov = (0, 255, 140)
        else:
            col = (55, 55, 75); hov = (55, 55, 75)
        self.draw_button(screen, "[ BAN! ]", sx, sy, sw, sh, col, hov, "submit")
        if enabled:
            for li in range(3):
                la = int(abs(math.sin((t / 195) + li)) * 255)
                ls = pygame.Surface((20, 4), pygame.SRCALPHA)
                ls.fill((0, 255, 200, la))
                screen.blit(ls, (sx - 25, sy + 24 + li * 18))

    # ═══════════════════════════════════════════════════════════
    #   RESULT / RANKING / FILE MANAGER
    # ═══════════════════════════════════════════════════════════
    def draw_result(self, screen, player_name, score, wrong, hp, monsters_killed, won):
        tc = (0, 255, 0) if won else (255, 50, 50)
        t = self.title_font.render("CHIEN THANG!" if won else "THAT BAI!", True, tc)
        screen.blit(t, t.get_rect(center=(self.width // 2, 150)))
        bw, bh, bx, by = 500, 350, self.width // 2 - 250, 250
        pygame.draw.rect(screen, (30, 30, 50), (bx, by, bw, bh), border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), (bx, by, bw, bh), 3, border_radius=15)
        yo = by + 40
        for txt, col2, dy, fn in [
            (f"Nguoi choi: {player_name}", (255, 255, 255),   0, self.medium_font),
            (f"Diem: {score}",             (255, 215, 0),    60, self.large_font),
            (f"Quai tieu diet: {monsters_killed}", (100, 255, 100), 120, self.medium_font),
            (f"Cau sai: {wrong}/2",        (200, 200, 200), 170, self.small_font),
            (f"HP quai con lai: {int(hp)}%", (200, 200, 200), 210, self.small_font),
        ]:
            srf = fn.render(txt, True, col2)
            screen.blit(srf, srf.get_rect(center=(self.width // 2, yo + dy)))
        self.draw_button(screen, "Choi lai", self.width // 2 - 150, 620, 300, 70,
                         (0, 180, 0), (0, 220, 0), "menu")

    def draw_ranking(self, screen, rankings):
        t = self.large_font.render("BANG XEP HANG", True, (255, 215, 0))
        screen.blit(t, t.get_rect(center=(self.width // 2, 60)))
        self.draw_button(screen, "Reset", self.width - 180, 50, 140, 50, (200, 50, 50), (230, 70, 70), "reset")
        if not rankings:
            srf = self.medium_font.render("Chua co nguoi choi nao", True, (150, 150, 150))
            screen.blit(srf, srf.get_rect(center=(self.width // 2, self.height // 2)))
        else:
            yo = 130
            for i, rank in enumerate(rankings):
                rh, ry = 70, yo + i * 82
                col = [(255, 215, 0), (192, 192, 192), (205, 127, 50)][i] if i < 3 else (70, 70, 70)
                tc2 = (0, 0, 0) if i < 3 else (255, 255, 255)
                pygame.draw.rect(screen, col, (100, ry, self.width - 200, rh), border_radius=10)
                pygame.draw.rect(screen, (255, 255, 255), (100, ry, self.width - 200, rh), 2, border_radius=10)
                screen.blit(self.large_font.render(f"#{i+1}", True, tc2), (120, ry + 15))
                screen.blit(self.medium_font.render(rank['name'], True, tc2), (220, ry + 10))
                screen.blit(self.small_font.render(rank['date'][:10], True, tc2 if i < 3 else (200, 200, 200)), (220, ry + 45))
                screen.blit(self.small_font.render(f"Quai: {rank.get('monsters_killed', 0)}", True,
                             tc2 if i < 3 else (100, 255, 100)), (450, ry + 45))
                sc = self.large_font.render(str(rank['score']), True, tc2)
                screen.blit(sc, sc.get_rect(right=self.width - 250, centery=ry + rh // 2))
                st = self.small_font.render("Thang" if rank['won'] else "Thua", True,
                     (0, 100, 0) if (rank['won'] and i < 3) else ((0, 255, 0) if rank['won'] else (255, 100, 100)))
                screen.blit(st, st.get_rect(right=self.width - 130, centery=ry + rh // 2))
        self.draw_button(screen, "Quay lai", self.width // 2 - 150, self.height - 100, 300, 60,
                         (0, 100, 200), (0, 130, 230), "back")

    def draw_file_manager(self, screen, files):
        t = self.large_font.render("Quan ly File De", True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=(self.width // 2, 80)))
        self.draw_button(screen, "Tai len file moi (.txt)", self.width // 2 - 250, 150, 500, 60,
                         (0, 100, 200), (0, 130, 230), "upload")
        if not files:
            srf = self.medium_font.render("Chua co file nao duoc tai len", True, (150, 150, 150))
            screen.blit(srf, srf.get_rect(center=(self.width // 2, self.height // 2)))
        else:
            yo = 240
            for i, file in enumerate(files):
                fy = yo + i * 90
                pygame.draw.rect(screen, (50, 50, 70), (100, fy, self.width - 200, 75), border_radius=10)
                pygame.draw.rect(screen, (100, 100, 150), (100, fy, self.width - 200, 75), 2, border_radius=10)
                screen.blit(self.medium_font.render(file['name'], True, (255, 255, 255)), (120, fy + 15))
                screen.blit(self.small_font.render(f"{file['question_count']} cau hoi - {file['upload_date'][:10]}",
                            True, (200, 200, 200)), (120, fy + 48))
                self.draw_button(screen, "Xoa", self.width - 180, fy + 17, 100, 40,
                                 (200, 50, 50), (230, 70, 70), f"delete_{i}")
        self.draw_button(screen, "Quay lai", self.width // 2 - 150, self.height - 100, 300, 60,
                         (100, 100, 100), (130, 130, 130), "back")

    def check_file_delete_click(self, x, y, file_count):
        for i in range(file_count):
            if self.check_button_click(x, y, f"delete_{i}"):
                return i
        return None