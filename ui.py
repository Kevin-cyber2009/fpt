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
                self._gun_recoil = 0.0
                self._gun_sway_x = 0.0
                self._gun_sway_y = 0.0
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
        self._gun_recoil=0.0; self._gun_sway_x=0.0; self._gun_sway_y=0.0

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
    #   SÚNG POV — VALORANT FIRST PERSON
    #   Góc nhìn thứ nhất, tay cầm thật, xoay theo chuột
    # ═══════════════════════════════════════════════════════════
    def draw_gun_pov(self, screen, mouse_pos, show_flash=False):
        W,H=self.width,self.height
        t=pygame.time.get_ticks()

        # Tính aim angle theo chuột
        aim_x=mouse_pos[0]-W*0.5
        aim_y=mouse_pos[1]-H*0.45

        # Smooth sway
        self._gun_sway_x+=(aim_x*0.038-self._gun_sway_x)*0.14
        self._gun_sway_y+=(aim_y*0.028-self._gun_sway_y)*0.14

        # Recoil
        if show_flash: self._gun_recoil=26.0
        self._gun_recoil*=0.70

        # ── Surface lớn để vẽ toàn bộ súng + tay ──
        GW,GH=580,340
        gs=pygame.Surface((GW,GH),pygame.SRCALPHA)

        # Điểm neo: tay cầm phải nằm ở góc dưới phải surface
        PX=GW-95   # x tay cầm trên surface
        PY=GH-68   # y tay cầm trên surface

        # Vẽ lên surface
        self._gun_full(gs,PX,PY,t,show_flash)

        # Tilt theo aim (max ±16 độ)
        tilt=max(-16,min(16, math.degrees(math.atan2(aim_y,max(abs(aim_x),1))*math.copysign(1,aim_x))*0.20))

        # Xoay surface
        rotated=pygame.transform.rotate(gs,-tilt)

        # Tính vị trí blit để pivot (PX,PY) nằm đúng ở (BASE_X,BASE_Y)
        BASE_X=W-55+self._gun_sway_x
        BASE_Y=H-18+self._gun_sway_y+self._gun_recoil

        rad=math.radians(-tilt)
        # Tìm vị trí pixel PX,PY trên surface đã xoay
        ox=PX-GW/2; oy=PY-GH/2
        rx=ox*math.cos(rad)-oy*math.sin(rad)
        ry=ox*math.sin(rad)+oy*math.cos(rad)
        blit_x=int(BASE_X-(rotated.get_width()/2+rx))
        blit_y=int(BASE_Y-(rotated.get_height()/2+ry))

        screen.blit(rotated,(blit_x,blit_y))

    def _gun_full(self, s, PX, PY, t, flash):
        """Vẽ toàn bộ súng POV: tay phải + thân + tay trái + flash"""
        # Toạ độ đầu nòng (bên trái màn hình khi súng hướng về phía trước)
        MX=PX-430   # Muzzle x
        MY=PY-100   # Muzzle y (tâm nòng)

        # ── TAY PHẢI cầm grip (vẽ trước để súng đè lên) ──
        self._right_hand(s,PX,PY,t)

        # ── THÂN SÚNG ──
        self._barrel(s,MX,MY,PX,PY,t)
        self._receiver(s,PX,PY,t)
        self._stock(s,PX,PY,t)
        self._sight(s,PX,PY,t)

        # ── TAY TRÁI giữ handguard (vẽ sau để trên nòng) ──
        HGX=MX+230; HGY=MY+30
        self._left_hand(s,HGX,HGY,t)

        # ── MUZZLE FLASH ──
        if flash:
            self._muzzle_flash(s,MX-2,MY,t)

    # ── Nòng súng (barrel + handguard) ──
    def _barrel(self,s,MX,MY,PX,PY,t):
        # Nòng chính
        bl=pygame.Rect(MX,MY+4,PX-MX-95,26)
        self._gr(s,bl,(60,68,80),(38,44,56),6)
        pygame.draw.rect(s,(82,95,115),bl,2,border_radius=6)

        # Rail trên
        rl=pygame.Rect(MX+8,MY-2,bl.width-16,8)
        pygame.draw.rect(s,(68,80,98),rl)
        for i in range(16):
            rx=rl.left+5+i*18; pygame.draw.line(s,(48,60,76),(rx,rl.top+1),(rx,rl.bottom-1),1)

        # Bands kim loại
        for bx2 in [MX+55,MX+120,MX+185,MX+255]:
            pygame.draw.rect(s,(46,54,66),(bx2,MY-2,7,32))
            pygame.draw.rect(s,(88,102,122),(bx2+2,MY,3,28))

        # Handguard dưới nòng
        hg=pygame.Rect(MX+20,MY+30,230,20)
        self._gr(s,hg,(48,56,68),(32,40,52),4)
        pygame.draw.rect(s,(72,86,106),hg,1,border_radius=4)
        for i in range(9):
            sx2=hg.left+8+i*24
            pygame.draw.rect(s,(28,34,44),(sx2,hg.top+3,16,14),border_radius=3)

        # Plasma coils (animated)
        off=(t//18)%22
        for ci in range(0,bl.width-20,22):
            cx2=bl.left+(ci+off)%bl.width
            ca=int(abs(math.sin((ci+t*0.04)*0.28))*160+60)
            ps=pygame.Surface((4,20),pygame.SRCALPHA); ps.fill((0,200,255,ca))
            s.blit(ps,(cx2,MY+8))

        # Muzzle tip
        pygame.draw.rect(s,(32,40,52),(MX-12,MY-2,16,30),border_radius=4)
        pygame.draw.rect(s,(62,78,98),(MX-12,MY-2,16,30),2,border_radius=4)
        # Slot trên suppressor
        for i in range(3):
            pygame.draw.rect(s,(22,28,38),(MX-10,MY+3+i*8,12,5),border_radius=2)

    # ── Receiver (hộp cò) ──
    def _receiver(self,s,PX,PY,t):
        RX=PX-115; RY=PY-88
        rec=pygame.Rect(RX,RY,115,62)
        self._gr(s,rec,(56,64,80),(36,44,60),8)
        pygame.draw.rect(s,(80,94,116),rec,2,border_radius=8)

        # Panel kỹ thuật
        pan=pygame.Rect(RX+8,RY+10,99,42)
        pygame.draw.rect(s,(42,50,64),pan,border_radius=5)
        for li in range(4):
            ly=pan.top+6+li*10
            pygame.draw.line(s,(30,36,48),(pan.left+5,ly),(pan.right-5,ly),1)

        # LED indicator
        for i,lc in enumerate([(0,255,100),(255,210,0),(0,170,255)]):
            lx2=RX+14+i*14; ly2=RY+8
            ba=int(abs(math.sin((t/310)+i))*200+55)
            bs=pygame.Surface((9,9),pygame.SRCALPHA); bs.fill((*lc,ba))
            s.blit(bs,(lx2,ly2))

        # Nút selector + lấy đạn
        pygame.draw.rect(s,(28,34,48),(RX+88,RY+14,14,34),border_radius=4)
        for i in range(3):
            pygame.draw.line(s,(68,80,100),(RX+89,RY+19+i*12),(RX+101,RY+19+i*12),2)

    # ── Stock báng súng ──
    def _stock(self,s,PX,PY,t):
        # Grip chính (tay cầm)
        gp=[(PX-16,PY-42),(PX+8,PY-42),(PX+14,PY+32),(PX-8,PY+36)]
        pygame.draw.polygon(s,(66,56,46),gp)
        pygame.draw.polygon(s,(46,40,34),gp,3)
        for gi in range(8):
            gy=PY-34+gi*8
            pygame.draw.line(s,(54,48,42),(PX-12,gy),(PX+6,gy+2),2)

        # Trigger guard
        pygame.draw.arc(s,(36,44,56),(PX-22,PY-34,22,32),0,math.pi,3)

        # Trigger
        pygame.draw.rect(s,(190,55,25),(PX-16,PY-24,7,16),border_radius=4)

        # Buffer tube / stock
        st=pygame.Rect(PX+8,PY-50,65,22)
        self._gr(s,st,(52,60,74),(34,42,56),5)
        pygame.draw.rect(s,(76,90,112),st,1,border_radius=5)
        pygame.draw.rect(s,(50,58,72),(st.right-12,st.top+3,10,16))

        # Magazine
        mg=pygame.Rect(PX-66,PY-6,28,55)
        self._gr(s,mg,(55,62,78),(36,44,58),5)
        pygame.draw.rect(s,(0,185,240),mg,2,border_radius=5)
        win=pygame.Rect(mg.x+5,mg.y+6,18,44)
        pygame.draw.rect(s,(18,26,40),win,border_radius=3)
        for i in range(6):
            cy2=win.top+4+i*7
            act=i<(6-(t//1300)%7)
            pygame.draw.rect(s,(0,225,175) if act else (24,40,48),(win.left+3,cy2,12,5),border_radius=2)

    # ── Kính ngắm Holographic ──
    def _sight(self,s,PX,PY,t):
        SX=PX-225; SY=PY-118
        # Mount
        pygame.draw.rect(s,(55,68,86),(SX,SY+26,54,11),border_radius=4)
        # Body
        sb=pygame.Rect(SX,SY,54,28)
        self._gr(s,sb,(52,64,86),(34,46,68),7)
        pygame.draw.rect(s,(0,175,255),sb,2,border_radius=7)
        # Lens trước
        pygame.draw.rect(s,(10,26,50),(SX+3,SY+5,14,18),border_radius=4)
        pygame.draw.rect(s,(0,160,228),(SX+3,SY+5,14,18),2,border_radius=4)
        # Reticle
        rcx=SX+32; rcy=SY+14
        pygame.draw.line(s,(0,235,255),(rcx-7,rcy),(rcx+7,rcy),1)
        pygame.draw.line(s,(0,235,255),(rcx,rcy-7),(rcx,rcy+7),1)
        pygame.draw.circle(s,(255,55,55),(rcx,rcy),2)
        # Zoom
        try: s.blit(self.micro_font.render("x8",True,(0,225,255)),(SX+32,SY+4))
        except: pass
        # Side lens LED
        pulse=int(abs(math.sin(t/380))*180+75)
        ps2=pygame.Surface((8,8),pygame.SRCALPHA); ps2.fill((0,pulse,255,180))
        s.blit(ps2,(SX+44,SY+10))

    # ── Tay phải cầm grip ──
    def _right_hand(self,s,PX,PY,t):
        # Cánh tay phải từ góc dưới phải
        arm=[
            (PX+25,PY-32),(PX+85,PY-10),
            (PX+98,PY+68),(PX+32,PY+80),
        ]
        pygame.draw.polygon(s,(56,63,80),arm)
        pygame.draw.polygon(s,(42,50,66),arm,2)
        for i in range(4):
            sy2=PY-22+i*24
            pygame.draw.line(s,(46,54,70),(PX+28,sy2),(PX+82,sy2+6),3)

        # Bàn tay
        hand=[(PX+14,PY-36),(PX+36,PY-38),(PX+40,PY+12),(PX+18,PY+16),(PX+8,PY-4)]
        pygame.draw.polygon(s,(70,78,96),hand)
        pygame.draw.polygon(s,(52,60,76),hand,2)

        # Ngón tay trên grip
        for fi in range(3):
            fr=pygame.Rect(PX+18,PY-26+fi*15,20,11)
            pygame.draw.rect(s,(64,72,90),fr,border_radius=4)
            pygame.draw.rect(s,(48,56,72),fr,1,border_radius=4)

        # Ngón cái
        pygame.draw.ellipse(s,(72,80,98),(PX+4,PY-12,15,26))
        pygame.draw.ellipse(s,(54,62,78),(PX+4,PY-12,15,26),1)

        # Knuckle armor
        for i in range(2):
            pygame.draw.rect(s,(80,90,112),(PX+16,PY-28+i*17,22,11),border_radius=3)
            pygame.draw.rect(s,(62,72,92),(PX+16,PY-28+i*17,22,11),1,border_radius=3)

    # ── Tay trái giữ handguard ──
    def _left_hand(self,s,lx,ly,t):
        arm=[(lx-52,ly-26),(lx+10,ly-20),(lx+14,ly+42),(lx-48,ly+34)]
        pygame.draw.polygon(s,(54,60,76),arm)
        pygame.draw.polygon(s,(40,48,64),arm,2)
        for i in range(3):
            sy2=ly-14+i*20; pygame.draw.line(s,(44,52,68),(lx-48,sy2),(lx+6,sy2+4),3)

        hand=[(lx-18,ly-24),(lx+10,ly-22),(lx+12,ly+24),(lx-16,ly+26),(lx-24,ly+6)]
        pygame.draw.polygon(s,(68,76,94),hand)
        pygame.draw.polygon(s,(52,60,76),hand,2)

        for fi in range(3):
            fr=pygame.Rect(lx-16,lx-16+fi*14-(lx-14),22,11)
            fr=pygame.Rect(lx-15,ly-14+fi*14,22,11)
            pygame.draw.rect(s,(64,72,90),fr,border_radius=4)
            pygame.draw.rect(s,(48,56,72),fr,1,border_radius=4)

        for i in range(2):
            pygame.draw.rect(s,(78,88,110),(lx-14,ly-20+i*17,24,11),border_radius=3)
            pygame.draw.rect(s,(60,70,90),(lx-14,ly-20+i*17,24,11),1,border_radius=3)

    # ── Gradient ngang ──
    def _gr(self,s,rect,tc,bc,r=6):
        for i in range(rect.height):
            t2=i/max(rect.height,1)
            col=tuple(min(255,max(0,int(tc[k]*(1-t2)+bc[k]*t2))) for k in range(3))
            pygame.draw.rect(s,col,(rect.x,rect.y+i,rect.width,1))
        pygame.draw.rect(s,bc,rect,2,border_radius=r)

    # ── Muzzle Flash Valorant ──
    def _muzzle_flash(self,s,fx,fy,t):
        for r in range(70,6,-12):
            a=int(255*r/70)
            fc=(230,245,255) if r>35 else (255,230,80)
            ms=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
            pygame.draw.circle(ms,(*fc,a),(r,r),r); s.blit(ms,(fx-r,fy-r))
        for i in range(14):
            ang=math.radians(i*26+random.randint(-10,10))
            ln=random.randint(48,105)
            pygame.draw.line(s,(230,248,255),(fx,fy),(fx+int(math.cos(ang)*ln),fy+int(math.sin(ang)*ln)),random.randint(2,5))
        pygame.draw.circle(s,(255,255,255),(fx,fy),26)
        pygame.draw.circle(s,(180,228,255),(fx,fy),16)
        pygame.draw.circle(s,(255,248,100),(fx,fy),8)
        for r in [56,75,94]:
            ws=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
            pygame.draw.circle(ws,(200,230,255,max(0,90-r)),(r,r),r,3); s.blit(ws,(fx-r,fy-r))
        for _ in range(20):
            ang=random.uniform(-0.5,0.5); d=random.randint(65,140)
            px=fx-int(math.cos(ang)*d); py=fy+int(math.sin(ang)*d); ps=random.randint(2,7)
            pygame.draw.circle(s,random.choice([(255,255,220),(220,242,255),(255,200,50)]),(px,py),ps)
            if ps>4: pygame.draw.circle(s,(255,255,255),(px,py),ps-3)

    # Legacy compat
    def draw_gun(self, screen, show_flash=False):
        self.draw_gun_pov(screen, pygame.mouse.get_pos(), show_flash)

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

    # ═══════════════════════════════════════════════════════════
    #   QUESTION PANEL
    # ═══════════════════════════════════════════════════════════
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

    # ── Multiple choice ──
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

    # ── True/False ──
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

    # ── Short answer ──
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

    # ── Nút BẮN (góc dưới phải, cạnh súng) ──
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
        # Glow lines
        if enabled:
            for li in range(3):
                la=int(abs(math.sin((t/195)+li))*255)
                ls=pygame.Surface((20,4),pygame.SRCALPHA); ls.fill((0,255,200,la))
                screen.blit(ls,(sx-25,sy+24+li*18))

    def check_answer_click(self,x,y,answer_count):
        for i in range(answer_count):
            if self.check_button_click(x,y,f"answer_{i}"): return i
        return None

    # ═══════════════════════════════════════════════════════════
    #   RESULT / RANKING / FILE
    # ═══════════════════════════════════════════════════════════
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