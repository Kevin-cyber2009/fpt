import pygame
import json
import os
from question_manager import QuestionManager
from monster import Monster
from ui import UI

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Game states
        self.state = "MENU"
        
        # Components
        self.question_manager = QuestionManager()
        self.monsters = []
        self.current_monster_index = 0
        self.create_monsters()
        self.ui = UI(self.width, self.height)
        
        # Player data
        self.player_name = ""
        self.score = 0
        self.wrong_answers = 0
        self.max_wrong = 2
        self.monsters_killed = 0
        
        # Current question
        self.current_question = None
        self.target_part = None
        self.selected_answer = None
        self.selected_answers = []
        self.user_input = ""
        self.show_feedback = False
        self.feedback_timer = 0
        self.is_correct = False
        
        # Rankings
        self.rankings = self.load_rankings()
        
        # Crosshair
        self.crosshair_pos = pygame.mouse.get_pos()
        
        # ═══ MONSTER TRANSITION ═══
        self.monster_transition_state = "ACTIVE"  # ACTIVE, DYING, SPAWNING
        self.transition_timer = 0.0
        self.monster_death_delay = 0.8  # 0.8 giây delay sau khi chết
        self.monster_spawn_delay = 0.3  # 0.3 giây spawn animation
        
    def create_monsters(self):
        # 7 different robot types
        robot_types = ['titan_bot', 'stealth_bot', 'plasma_bot', 'war_bot', 'nano_bot', 'mech_bot', 'cyber_bot']
        for rtype in robot_types:
            self.monsters.append(Monster(self.width // 2, self.height // 2 + 50, rtype))
    
    def get_current_monster(self):
        if self.monsters:
            return self.monsters[self.current_monster_index % len(self.monsters)]
        return None
    
    def load_rankings(self):
        try:
            if os.path.exists('data/rankings.json'):
                with open('data/rankings.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_rankings(self):
        os.makedirs('data', exist_ok=True)
        with open('data/rankings.json', 'w', encoding='utf-8') as f:
            json.dump(self.rankings, f, ensure_ascii=False, indent=2)
    
    def reset_rankings(self):
        self.rankings = []
        self.save_rankings()
    
    def handle_event(self, event):
        if self.state == "MENU":
            self.handle_menu_event(event)
        elif self.state == "NAME_INPUT":
            self.handle_name_input_event(event)
        elif self.state == "GAME":
            self.handle_game_event(event)
        elif self.state == "RESULT":
            self.handle_result_event(event)
        elif self.state == "RANKING":
            self.handle_ranking_event(event)
        elif self.state == "FILE_MANAGER":
            self.handle_file_manager_event(event)
    
    def handle_menu_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.ui.check_button_click(x, y, "start"):
                self.state = "NAME_INPUT"
                self.player_name = ""
            elif self.ui.check_button_click(x, y, "upload"):
                self.state = "FILE_MANAGER"
            elif self.ui.check_button_click(x, y, "ranking"):
                self.state = "RANKING"
    
    def handle_name_input_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.player_name.strip():
                    self.start_game()
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.state = "MENU"
            else:
                if len(self.player_name) < 20 and event.unicode.isprintable():
                    self.player_name += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.ui.check_button_click(x, y, "back"):
                self.state = "MENU"
            elif self.ui.check_button_click(x, y, "confirm"):
                if self.player_name.strip():
                    self.start_game()
    
    def handle_game_event(self, event):
        # Không cho click nếu đang transition
        if self.monster_transition_state != "ACTIVE":
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN and not self.show_feedback:
            x, y = event.pos
            monster = self.get_current_monster()
            
            if self.current_question is None:
                part = monster.get_clicked_part(x, y)
                if part:
                    self.target_part = part
                    level = self.get_level_from_part(part)
                    self.current_question = self.question_manager.get_random_question(level)
                    if self.current_question:
                        self.selected_answer = None
                        self.selected_answers = []
                        self.user_input = ""
            else:
                q_type = self.current_question.get('type', 'multiple_choice')
                
                if q_type == 'multiple_choice':
                    answer_index = self.ui.check_answer_click(x, y, len(self.current_question.get('answers', [])))
                    if answer_index is not None:
                        self.selected_answer = answer_index
                        self.selected_answers = [answer_index]
                    elif self.ui.check_button_click(x, y, "submit") and self.selected_answer is not None:
                        self.submit_answer()
                
                elif q_type == 'true_false':
                    answer_index = self.ui.check_answer_click(x, y, len(self.current_question.get('answers', [])))
                    if answer_index is not None:
                        if answer_index in self.selected_answers:
                            self.selected_answers.remove(answer_index)
                        else:
                            self.selected_answers.append(answer_index)
                    elif self.ui.check_button_click(x, y, "submit") and len(self.selected_answers) > 0:
                        self.submit_answer()
                
                elif q_type == 'short_answer':
                    if self.ui.check_button_click(x, y, "submit") and self.user_input.strip():
                        self.submit_answer()
        
        elif event.type == pygame.KEYDOWN and self.current_question:
            q_type = self.current_question.get('type', 'multiple_choice')
            
            if q_type == 'short_answer' and not self.show_feedback:
                if event.key == pygame.K_RETURN:
                    if self.user_input.strip():
                        self.submit_answer()
                elif event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                elif event.unicode.isprintable():
                    if len(self.user_input) < 50:
                        self.user_input += event.unicode
    
    def handle_result_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.ui.check_button_click(x, y, "menu"):
                self.state = "MENU"
    
    def handle_ranking_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.ui.check_button_click(x, y, "back"):
                self.state = "MENU"
            elif self.ui.check_button_click(x, y, "reset"):
                self.reset_rankings()
    
    def handle_file_manager_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.ui.check_button_click(x, y, "back"):
                self.state = "MENU"
            elif self.ui.check_button_click(x, y, "upload"):
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                filename = filedialog.askopenfilename(
                    title="Chon file cau hoi",
                    filetypes=[("Text files", "*.txt")]
                )
                if filename:
                    count = self.question_manager.load_questions_from_file(filename)
                    print(f"Da tai {count} cau hoi tu {filename}")
            else:
                delete_index = self.ui.check_file_delete_click(x, y, len(self.question_manager.uploaded_files))
                if delete_index is not None:
                    self.question_manager.delete_file(delete_index)
    
    def get_level_from_part(self, part):
        if part == "head":
            return "vandung"
        elif part == "body":
            return "thonghieu"
        else:
            return "nhanbiet"
    
    def start_game(self):
        if len(self.question_manager.questions) == 0:
            print("Vui long tai file cau hoi truoc!")
            return
        
        self.state = "GAME"
        self.score = 0
        self.wrong_answers = 0
        self.monsters_killed = 0
        self.current_monster_index = 0
        for monster in self.monsters:
            monster.reset()
        self.current_question = None
        self.target_part = None
        self.selected_answer = None
        self.selected_answers = []
        self.user_input = ""
        self.show_feedback = False
        self.question_manager.reset_used_questions()
        self.monster_transition_state = "ACTIVE"
        self.transition_timer = 0.0
        pygame.mouse.set_visible(False)
    
    def submit_answer(self):
        if self.current_question is None:
            return
        
        q_type = self.current_question.get('type', 'multiple_choice')
        
        if q_type == 'multiple_choice':
            if self.selected_answer is None:
                return
            self.is_correct = (self.selected_answer == self.current_question.get('correct'))
        
        elif q_type == 'true_false':
            if len(self.selected_answers) == 0:
                return
            
            correct_answers = self.current_question.get('correct_answers', [self.current_question.get('correct')])
            selected_set = set(self.selected_answers)
            correct_set = set(correct_answers)
            self.is_correct = (selected_set == correct_set)
        
        elif q_type == 'short_answer':
            if not self.user_input.strip():
                return
            correct_ans = self.current_question.get('correct_answer', '').strip().lower()
            user_ans = self.user_input.strip().lower()
            self.is_correct = (user_ans == correct_ans)
        
        self.show_feedback = True
        self.feedback_timer = 1.5
        
        if self.is_correct:
            # ═══ TRIGGER SHOOT EFFECT ═══
            self.ui.trigger_shoot_effect()
    
    def update(self, dt):
        self.crosshair_pos = pygame.mouse.get_pos()
        
        if self.state == "GAME":
            monster = self.get_current_monster()
            
            # ═══ MONSTER TRANSITION STATE MACHINE ═══
            if self.monster_transition_state == "DYING":
                self.transition_timer -= dt
                if self.transition_timer <= 0:
                    # Chuyển sang spawn con mới
                    if self.question_manager.has_unused_questions():
                        self.current_monster_index += 1
                        next_monster = self.get_current_monster()
                        next_monster.reset()
                        self.monster_transition_state = "SPAWNING"
                        self.transition_timer = self.monster_spawn_delay
                    else:
                        # Hết câu hỏi - thắng!
                        self.end_game(True)
                        self.monster_transition_state = "ACTIVE"
            
            elif self.monster_transition_state == "SPAWNING":
                self.transition_timer -= dt
                if self.transition_timer <= 0:
                    # Spawn xong, active lại
                    self.monster_transition_state = "ACTIVE"
            
            # ═══ FEEDBACK LOGIC ═══
            if self.show_feedback:
                self.feedback_timer -= dt
                if self.feedback_timer <= 0:
                    self.show_feedback = False
                    
                    if self.is_correct:
                        damage = self.get_damage_from_part(self.target_part)
                        monster.take_damage(damage)
                        self.score += damage * 10
                        
                        if monster.hp <= 0:
                            self.monsters_killed += 1
                            # Bắt đầu transition
                            self.monster_transition_state = "DYING"
                            self.transition_timer = self.monster_death_delay
                    else:
                        self.wrong_answers += 1
                        if self.wrong_answers >= self.max_wrong:
                            self.end_game(False)
                    
                    self.current_question = None
                    self.target_part = None
                    self.selected_answer = None
                    self.selected_answers = []
                    self.user_input = ""
    
    def get_damage_from_part(self, part):
        if part == "head":
            return 40
        elif part == "body":
            return 25
        else:
            return 15
    
    def end_game(self, won):
        import datetime
        
        new_ranking = {
            "name": self.player_name,
            "score": self.score,
            "won": won,
            "monsters_killed": self.monsters_killed,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.rankings.append(new_ranking)
        self.rankings.sort(key=lambda x: x['score'], reverse=True)
        self.rankings = self.rankings[:10]
        self.save_rankings()
        
        self.state = "RESULT"
        pygame.mouse.set_visible(True)
    
    def draw(self):
        self.screen.fill((20, 20, 40))
        
        if self.state == "MENU":
            self.ui.draw_menu(self.screen, len(self.question_manager.questions))
        elif self.state == "NAME_INPUT":
            self.ui.draw_name_input(self.screen, self.player_name)
        elif self.state == "GAME":
            self.draw_game()
        elif self.state == "RESULT":
            monster = self.get_current_monster()
            self.ui.draw_result(self.screen, self.player_name, self.score, 
                              self.wrong_answers, monster.hp, 
                              self.monsters_killed, self.monsters_killed > 0)
        elif self.state == "RANKING":
            self.ui.draw_ranking(self.screen, self.rankings)
        elif self.state == "FILE_MANAGER":
            self.ui.draw_file_manager(self.screen, self.question_manager.uploaded_files)
    
    def draw_game(self):
        # ═══ DRAW BACKGROUND ═══
        self.ui.draw_background(self.screen)
        
        monster = self.get_current_monster()
        
        # ═══ DRAW MONSTER với transition effects ═══
        if self.monster_transition_state == "DYING":
            # Fade out effect
            alpha = int((self.transition_timer / self.monster_death_delay) * 255)
            monster_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            monster.draw(monster_surf, self.target_part)
            monster_surf.set_alpha(alpha)
            self.screen.blit(monster_surf, (0, 0))
            
            # Death text
            death_text = self.ui.large_font.render("ELIMINATED!", True, (255, 50, 50))
            text_alpha = int((1 - self.transition_timer / self.monster_death_delay) * 255)
            death_surf = pygame.Surface((death_text.get_width(), death_text.get_height()), pygame.SRCALPHA)
            death_surf.blit(death_text, (0, 0))
            death_surf.set_alpha(text_alpha)
            self.screen.blit(death_surf, death_text.get_rect(center=(self.width // 2, self.height // 2 - 100)))
        
        elif self.monster_transition_state == "SPAWNING":
            # Fade in effect
            alpha = int((1 - self.transition_timer / self.monster_spawn_delay) * 255)
            monster_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            monster.draw(monster_surf, None)
            monster_surf.set_alpha(alpha)
            self.screen.blit(monster_surf, (0, 0))
            
            # Spawn text
            spawn_text = self.ui.large_font.render("NEW TARGET!", True, (255, 200, 0))
            text_alpha = alpha
            spawn_surf = pygame.Surface((spawn_text.get_width(), spawn_text.get_height()), pygame.SRCALPHA)
            spawn_surf.blit(spawn_text, (0, 0))
            spawn_surf.set_alpha(text_alpha)
            self.screen.blit(spawn_surf, spawn_text.get_rect(center=(self.width // 2, self.height // 2 - 100)))
        
        else:
            # Normal draw
            monster.draw(self.screen, self.target_part)
        
        # ═══ DRAW HUD ═══
        self.ui.draw_hud(self.screen, self.player_name, self.score, 
                        monster.hp, self.wrong_answers, self.max_wrong,
                        self.monsters_killed)
        
        # ═══ DRAW GUN ═══
        show_flash = self.show_feedback and self.is_correct
        self.ui.draw_gun(self.screen, show_flash)
        
        # ═══ DRAW QUESTION PANEL ═══
        if self.current_question and self.monster_transition_state == "ACTIVE":
            self.ui.draw_question_panel(
                self.screen, 
                self.current_question, 
                self.target_part, 
                self.selected_answer,
                self.selected_answers, 
                self.user_input,
                self.show_feedback, 
                self.is_correct
            )
        
        # ═══ DRAW CROSSHAIR ═══
        if not self.current_question and self.monster_transition_state == "ACTIVE":
            # Crosshair bắn
            pygame.draw.circle(self.screen, (255, 0, 0), self.crosshair_pos, 15, 2)
            pygame.draw.circle(self.screen, (255, 0, 0), self.crosshair_pos, 2)
            pygame.draw.line(self.screen, (255, 0, 0), 
                            (self.crosshair_pos[0] - 20, self.crosshair_pos[1]),
                            (self.crosshair_pos[0] - 10, self.crosshair_pos[1]), 2)
            pygame.draw.line(self.screen, (255, 0, 0),
                            (self.crosshair_pos[0] + 10, self.crosshair_pos[1]),
                            (self.crosshair_pos[0] + 20, self.crosshair_pos[1]), 2)
            pygame.draw.line(self.screen, (255, 0, 0),
                            (self.crosshair_pos[0], self.crosshair_pos[1] - 20),
                            (self.crosshair_pos[0], self.crosshair_pos[1] - 10), 2)
            pygame.draw.line(self.screen, (255, 0, 0),
                            (self.crosshair_pos[0], self.crosshair_pos[1] + 10),
                            (self.crosshair_pos[0], self.crosshair_pos[1] + 20), 2)
        else:
            # Crosshair thường
            pygame.draw.circle(self.screen, (255, 255, 255), self.crosshair_pos, 10, 3)
            pygame.draw.circle(self.screen, (100, 150, 255), self.crosshair_pos, 6)
            pygame.draw.circle(self.screen, (150, 200, 255), self.crosshair_pos, 15, 1)