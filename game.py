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
        
        # Muzzle flash
        self.show_muzzle_flash = False
        self.muzzle_flash_timer = 0
        
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
            
            # Há»– TRá»¢ NHIá»€U ÄÃP ÃN ÄÃšNG
            correct_answers = self.current_question.get('correct_answers', [self.current_question.get('correct')])
            
            # Kiá»ƒm tra: user pháº£i chá»n CHÃNH XÃC táº¥t cáº£ Ä‘Ã¡p Ã¡n Ä‘Ãºng, khÃ´ng hÆ¡n khÃ´ng kÃ©m
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
            self.show_muzzle_flash = True
            self.muzzle_flash_timer = 0.1
    
    def update(self, dt):
        self.crosshair_pos = pygame.mouse.get_pos()
        
        if self.show_muzzle_flash:
            self.muzzle_flash_timer -= dt
            if self.muzzle_flash_timer <= 0:
                self.show_muzzle_flash = False
        
        if self.state == "GAME":
            monster = self.get_current_monster()
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
                            if self.question_manager.has_unused_questions():
                                self.current_monster_index += 1
                                next_monster = self.get_current_monster()
                                next_monster.reset()
                            else:
                                self.end_game(True)
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
        monster = self.get_current_monster()
        
        self.ui.draw_hud(self.screen, self.player_name, self.score, 
                        monster.hp, self.wrong_answers, self.max_wrong,
                        self.monsters_killed)
        
        monster.draw(self.screen, self.target_part)
        
        self.ui.draw_gun(self.screen, self.show_muzzle_flash)
        
        if self.current_question:
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
        
        if not self.current_question:
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
            pygame.draw.circle(self.screen, (255, 255, 255), self.crosshair_pos, 10, 3)
            pygame.draw.circle(self.screen, (100, 150, 255), self.crosshair_pos, 6)
            pygame.draw.circle(self.screen, (150, 200, 255), self.crosshair_pos, 15, 1)