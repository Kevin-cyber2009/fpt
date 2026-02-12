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

    # ── helpers ──────────────────────────────────────────────────
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

    # ═══════════════════════════════════════════════════════════
    #   TRIGGER SHOOT EFFECT (FIX LỖI)
    # ═══════════════════════════════════════════════════════════
    def trigger_shoot_effect(self):
        """Trigger shooting animation"""
        self._gun_recoil = 1.0
        self._gun_kickback = 25.0
        self._muzzle_flash_timer = 0.15
        self._shoot_frame = 0

    # ═══════════════════════════════════════════════════════════
    #   BACKGROUND SCI-FI CORRIDOR (DOOM STYLE)
    # ═══════════════════════════════════════════════════════════
    def draw_background(self, screen):
        """Vẽ background sci-fi corridor như Doom"""
        W, H = self.width, self.height
        
        # Sky gradient (dark space)
        for y in range(H // 2):
            c = int(20 + (y / (H/2)) * 15)
            pygame.draw.line(screen, (c, c, c + 10), (0, y), (W, y))
        
        # Floor gradient (metal floor)
        for y in range(H // 2, H):
            progress = (y - H/2) / (H/2)
            c = int(40 + progress * 30)
            pygame.draw.line(screen, (c, c - 5, c - 10), (0, y), (W, y))
        
        # ═══ CORRIDOR WALLS (Perspective) ═══
        horizon_y = H // 2
        
        # Left wall
        wall_left_points = [
            (0, 0),
            (W * 0.25, horizon_y - 100),
            (W * 0.25, horizon_y + 100),
            (0, H)
        ]
        
        # Right wall
        wall_right_points = [
            (W, 0),
            (W * 0.75, horizon_y - 100),
            (W * 0.75, horizon_y + 100),
            (W, H)
        ]
        
        # Draw walls with texture
        for points, is_left in [(wall_left_points, True), (wall_right_points, False)]:
            # Base wall color
            pygame.draw.polygon(screen, (60, 65, 75), points)
            pygame.draw.polygon(screen, (80, 85, 95), points, 3)
            
            # Metal panels
            if is_left:
                panel_x_range = range(int(W * 0.02), int(W * 0.23), 40)
            else:
                panel_x_range = range(int(W * 0.77), int(W * 0.98), 40)
            
            for px in panel_x_range:
                for py in range(50, H - 50, 80):
                    # Panel
                    panel_rect = pygame.Rect(px, py, 35, 70)
                    pygame.draw.rect(screen, (70, 75, 85), panel_rect)
                    pygame.draw.rect(screen, (50, 55, 65), panel_rect, 2)
                    
                    # Rivets
                    for rx, ry in [(px + 5, py + 10), (px + 30, py + 10),
                                   (px + 5, py + 60), (px + 30, py + 60)]:
                        pygame.draw.circle(screen, (90, 95, 105), (rx, ry), 3)
                        pygame.draw.circle(screen, (40, 45, 55), (rx, ry), 2)
        
        # ═══ CEILING LIGHTS ═══
        for lx in range(int(W * 0.3), int(W * 0.7), 100):
            # Light fixture
            light_rect = pygame.Rect(lx, horizon_y - 120, 60, 15)
            pygame.draw.rect(screen, (80, 85, 95), light_rect)
            
            # Light glow
            for i in range(3):
                alpha = 120 - i * 40
                glow_surf = pygame.Surface((70 + i * 20, 30 + i * 10), pygame.SRCALPHA)
                pygame.draw.ellipse(glow_surf, (200, 220, 255, alpha), (0, 0, 70 + i * 20, 30 + i * 10))
                screen.blit(glow_surf, (lx - 5 - i * 10, horizon_y - 110 - i * 5))
        
        # ═══ FLOOR GRID ═══
        grid_start_y = horizon_y + 100
        for i in range(8):
            y = grid_start_y + i * 40
            # Perspective line
            width = int(W * 0.5 * (1 - i / 10))
            x_center = W // 2
            pygame.draw.line(screen, (50, 50, 60), 
                           (x_center - width, y), (x_center + width, y), 2)
        
        # ═══ DISTANT DOORWAY/MONSTER AREA ═══
        door_w = 220
        door_h = 240
        door_x = (W - door_w) // 2
        door_y = horizon_y - door_h // 2
        
        # Doorway frame
        pygame.draw.rect(screen, (50, 55, 65), (door_x - 10, door_y - 10, door_w + 20, door_h + 20))
        
        # Dark interior (where monster stands)
        pygame.draw.rect(screen, (15, 18, 25), (door_x, door_y, door_w, door_h))
        
        # Door lights (warning lights)
        for i, (dx, col) in enumerate([(-20, (255, 50, 50)), (door_w + 10, (255, 50, 50))]):
            blink = (pygame.time.get_ticks() // 400 + i) % 2
            if blink:
                light_x = door_x + dx
                light_y = door_y + 20
                pygame.draw.circle(screen, col, (light_x, light_y), 8)
                # Glow
                for j in range(2):
                    glow = pygame.Surface((30 + j * 10, 30 + j * 10), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (*col, 100 - j * 40), (15 + j * 5, 15 + j * 5), 15 + j * 5)
                    screen.blit(glow, (light_x - 15 - j * 5, light_y - 15 - j * 5))

    # ═══════════════════════════════════════════════════════════
    #   SÚNG DOOM STYLE - PIXEL ART SHOTGUN
    # ═══════════════════════════════════════════════════════════
    def draw_gun_doom(self, screen, show_flash=False):
        """Vẽ súng Doom-style pixel art shotgun/pistol"""
        W, H = self.width, self.height
        
        # Update timers
        if self._muzzle_flash_timer > 0:
            self._muzzle_flash_timer -= 1/60.0
            show_flash = True
        
        # Recoil animation
        self._gun_recoil = max(0, self._gun_recoil - 0.08)
        self._gun_kickback = max(0, self._gun_kickback - 2.0)
        
        # Gun position (bottom center)
        gun_base_x = W // 2
        gun_base_y = H - 80 + self._gun_kickback
        
        # Recoil offset
        recoil_y = -self._gun_recoil * 35
        
        # ═══ DRAW HANDS HOLDING GUN ═══
        # Left hand (supporting)
        left_hand_x = gun_base_x - 120
        left_hand_y = gun_base_y - 60 + recoil_y
        
        # Left forearm
        left_arm_points = [
            (left_hand_x - 40, H),
            (left_hand_x - 30, H),
            (left_hand_x + 10, left_hand_y + 40),
            (left_hand_x, left_hand_y + 40)
        ]
        pygame.draw.polygon(screen, (140, 120, 100), left_arm_points)
        pygame.draw.polygon(screen, (100, 85, 70), left_arm_points, 3)
        
        # Left hand
        pygame.draw.ellipse(screen, (160, 140, 120), 
                          (left_hand_x - 15, left_hand_y + 25, 45, 35))
        pygame.draw.ellipse(screen, (120, 100, 85), 
                          (left_hand_x - 15, left_hand_y + 25, 45, 35), 2)
        
        # Fingers
        for i in range(4):
            finger_x = left_hand_x - 10 + i * 12
            pygame.draw.rect(screen, (150, 130, 110), 
                           (finger_x, left_hand_y + 25, 8, 25), border_radius=3)
        
        # Right hand (trigger hand)
        right_hand_x = gun_base_x + 50
        right_hand_y = gun_base_y - 40 + recoil_y
        
        # Right forearm
        right_arm_points = [
            (right_hand_x + 40, H),
            (right_hand_x + 50, H),
            (right_hand_x + 20, right_hand_y + 50),
            (right_hand_x + 10, right_hand_y + 50)
        ]
        pygame.draw.polygon(screen, (140, 120, 100), right_arm_points)
        pygame.draw.polygon(screen, (100, 85, 70), right_arm_points, 3)
        
        # Right hand
        pygame.draw.ellipse(screen, (160, 140, 120), 
                          (right_hand_x - 10, right_hand_y + 35, 45, 35))
        pygame.draw.ellipse(screen, (120, 100, 85), 
                          (right_hand_x - 10, right_hand_y + 35, 45, 35), 2)
        
        # Fingers
        for i in range(3):
            finger_x = right_hand_x - 5 + i * 12
            pygame.draw.rect(screen, (150, 130, 110), 
                           (finger_x, right_hand_y + 35, 8, 25), border_radius=3)
        
        # Trigger finger
        trigger_finger_y = right_hand_y + 20 if self._gun_recoil > 0.3 else right_hand_y + 30
        pygame.draw.rect(screen, (150, 130, 110), 
                       (right_hand_x + 30, trigger_finger_y, 8, 20), border_radius=3)
        
        # ═══ GUN BODY (DOOM SHOTGUN STYLE) ═══
        gun_y = gun_base_y - 100 + recoil_y
        
        # Barrel (double barrel shotgun style)
        barrel_width = 35
        barrel_length = 180
        
        # Upper barrel
        upper_barrel = pygame.Rect(gun_base_x - barrel_width//2, gun_y - 25, barrel_length, 16)
        pygame.draw.rect(screen, (60, 65, 75), upper_barrel, border_radius=3)
        pygame.draw.rect(screen, (80, 85, 95), upper_barrel, 3, border_radius=3)
        
        # Lower barrel
        lower_barrel = pygame.Rect(gun_base_x - barrel_width//2, gun_y - 7, barrel_length, 16)
        pygame.draw.rect(screen, (60, 65, 75), lower_barrel, border_radius=3)
        pygame.draw.rect(screen, (80, 85, 95), lower_barrel, 3, border_radius=3)
        
        # Barrel bands
        for bx in [gun_base_x + 40, gun_base_x + 90, gun_base_x + 140]:
            pygame.draw.rect(screen, (50, 55, 65), (bx, gun_y - 28, 8, 30))
        
        # Receiver/action
        receiver = pygame.Rect(gun_base_x - 50, gun_y - 15, 70, 40)
        pygame.draw.rect(screen, (70, 75, 85), receiver, border_radius=5)
        pygame.draw.rect(screen, (90, 95, 105), receiver, 3, border_radius=5)
        
        # Pump action (animates with recoil)
        pump_x = gun_base_x - 30 - int(self._gun_recoil * 20)
        pump_rect = pygame.Rect(pump_x, gun_y - 5, 35, 20)
        pygame.draw.rect(screen, (80, 85, 95), pump_rect, border_radius=4)
        pygame.draw.rect(screen, (60, 65, 75), pump_rect, 2, border_radius=4)
        
        # Trigger guard
        pygame.draw.arc(screen, (70, 75, 85), 
                       (gun_base_x + 20, gun_y + 5, 30, 30), 
                       0, math.pi, 4)
        
        # Trigger
        trigger_y_offset = 5 if self._gun_recoil > 0.3 else 0
        pygame.draw.rect(screen, (180, 160, 140), 
                       (gun_base_x + 30, gun_y + 15 + trigger_y_offset, 6, 12), 
                       border_radius=3)
        
        # Stock
        stock_points = [
            (gun_base_x + 65, gun_y),
            (gun_base_x + 150, gun_y - 5),
            (gun_base_x + 150, gun_y + 25),
            (gun_base_x + 65, gun_y + 20)
        ]
        pygame.draw.polygon(screen, (100, 80, 60), stock_points)
        pygame.draw.polygon(screen, (80, 65, 50), stock_points, 3)
        
        # Stock details (wood grain)
        for i in range(3):
            pygame.draw.line(screen, (90, 70, 55), 
                           (gun_base_x + 70 + i * 20, gun_y + 5), 
                           (gun_base_x + 140 + i * 5, gun_y + 10), 2)
        
        # ═══ MUZZLE FLASH ═══
        if show_flash and self._muzzle_flash_timer > 0:
            flash_x = gun_base_x - barrel_width//2 - 40
            flash_y = gun_y - 16
            
            # Large flash
            for r in range(60, 10, -10):
                alpha = int((self._muzzle_flash_timer / 0.15) * 255 * (r / 60))
                flash_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                color = (255, 240, 100) if r > 30 else (255, 200, 50)
                pygame.draw.circle(flash_surf, (*color, alpha), (r, r), r)
                screen.blit(flash_surf, (flash_x - r, flash_y - r))
            
            # Flash rays
            for i in range(12):
                angle = math.radians(i * 30 + random.randint(-10, 10))
                length = random.randint(40, 80)
                end_x = flash_x + math.cos(angle) * length
                end_y = flash_y + math.sin(angle) * length
                pygame.draw.line(screen, (255, 240, 150), 
                               (flash_x, flash_y), (end_x, end_y), 
                               random.randint(2, 5))
            
            # Core
            pygame.draw.circle(screen, (255, 255, 200), (flash_x, flash_y), 15)
        
        # ═══ AMMO COUNTER (DOOM STYLE) ═══
        ammo_text = "SHELLS: 50"
        ammo_surf = self.small_font.render(ammo_text, True, (255, 200, 0))
        screen.blit(ammo_surf, (W - 200, H - 60))

    # Legacy compat
    def draw_gun(self, screen, show_flash=False):
        self.draw_gun_doom(screen, show_flash)

    # ═══════════════════════════════════════════════════════════
    #   MENU / NAME / HUD
    # ═══════════════════════════════════════════════════════════
    def draw_menu(self,screen,question_count):
        t=self.title_font.render("Monster Quiz Shooter",True,(255,215,0))
        screen.blit(t,t.get_rect(center=(self.width//2,150)))
        bw,bh,bx=400,80,self.width//2-200
        self.draw_button(screen,"BAT DAU",       bx,300,bw,bh,(0,180,0),  (0,220,0),  "start")
        self.draw_button(screen,"QUAN LY FILE",  bx,400,bw,bh,(0,100,200),(0,130,230),"upload")
        self.draw_button(screen,"BANG XEP HANG", bx,500,bw,bh,(200,150,0),(230,180,0),"ranking")
        ct=self.safe_render(self.small_font,f"Tong cau hoi: {question_count}",(200,200,200))
        screen.blit(ct,ct.get_rect(center=(self.width//2,610)))

    def draw_name_input(self,screen,player_name):
        t=self.large_font.render("Nhap ten cua ban",True,(255,255,255))
        screen.blit(t,t.get_rect(center=(self.width//2,200)))
        iw,ih,ix,iy=500,60,self.width//2-250,300
        pygame.draw.rect(screen,(50,50,70),(ix,iy,iw,ih),border_radius=10)
        pygame.draw.rect(screen,(100,100,200),(ix,iy,iw,ih),3,border_radius=10)
        ts=self.safe_render(self.medium_font,player_name+"|",(255,255,255))
        screen.blit(ts,ts.get_rect(midleft=(ix+20,iy+ih//2)))
        self.draw_button(screen,"Quay lai",self.width//2-220,420,200,60,(100,100,100),(130,130,130),"back")
        self.draw_button(screen,"Bat dau", self.width//2+20, 420,200,60,(0,180,0),(0,220,0),"confirm")

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