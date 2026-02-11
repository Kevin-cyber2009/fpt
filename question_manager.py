import os
import json
import random
from datetime import datetime

class QuestionManager:
    def __init__(self):
        self.questions = []
        self.uploaded_files = []
        self.used_questions = []
        self.load_saved_data()
    
    def load_saved_data(self):
        """Load questions and file list from saved data"""
        try:
            if os.path.exists('data/questions_data.json'):
                with open('data/questions_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.questions = data.get('questions', [])
                    self.uploaded_files = data.get('files', [])
        except:
            pass
    
    def save_data(self):
        """Save questions and file list"""
        os.makedirs('data', exist_ok=True)
        with open('data/questions_data.json', 'w', encoding='utf-8') as f:
            json.dump({
                'questions': self.questions,
                'files': self.uploaded_files
            }, f, ensure_ascii=False, indent=2)
    
    def load_questions_from_file(self, filepath):
        """Load questions from a text file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            parsed = self.parse_questions(content)
            
            if len(parsed) == 0:
                return 0
            
            file_info = {
                'name': os.path.basename(filepath),
                'path': filepath,
                'question_count': len(parsed),
                'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.uploaded_files.append(file_info)
            self.questions.extend(parsed)
            self.save_data()
            
            return len(parsed)
        except Exception as e:
            print(f"Error loading file: {e}")
            return 0
    
    def parse_questions(self, content):
        """Parse questions - Há»– TRá»¢ FORMAT Ä/S vÃ  NHIá»€U ÄÃP ÃN ÄÃšNG"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        questions = []
        current_question = None
        in_context = False
        context_text = ""
        
        for line in lines:
            # Check if starting a question
            if line.startswith('CÃ¢u') or line.startswith('Cau') or (line[0].isdigit() and '.' in line[:5]):
                # Save previous question
                if current_question and current_question.get('question'):
                    if 'type' not in current_question:
                        current_question['type'] = 'multiple_choice'
                    
                    # Auto-detect true/false if multiple correct answers
                    if len(current_question.get('correct_answers', [])) > 1:
                        current_question['type'] = 'true_false'
                    
                    if current_question['type'] == 'multiple_choice' and len(current_question.get('answers', [])) > 0:
                        questions.append(current_question)
                    elif current_question['type'] in ['true_false', 'short_answer']:
                        questions.append(current_question)
                
                # Start new question
                question_text = line
                if line.startswith('CÃ¢u') or line.startswith('Cau'):
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        question_text = parts[1].strip()
                elif line[0].isdigit():
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        question_text = parts[1].strip()
                
                current_question = {
                    'question': question_text,
                    'context': '',
                    'type': 'multiple_choice',
                    'answers': [],
                    'correct': None,
                    'correct_answers': [],  # Support multiple correct
                    'level': 'thonghieu'
                }
                in_context = False
                context_text = ""
            
            # Check for context (quoted text)
            elif line.startswith('"') or in_context:
                in_context = True
                context_text += line + " "
                if current_question:
                    current_question['context'] = context_text.strip()
                if line.endswith('"'):
                    in_context = False
            
            # Check for short answer (marked with *)
            elif line.startswith('*') and current_question:
                current_question['type'] = 'short_answer'
                current_question['correct_answer'] = line[1:].strip()
                current_question['correct'] = 0
                current_question['answers'] = []
            
            # Check if it's an answer line - Há»– TRá»¢ FORMAT Ä/S
            elif line and line[0].lower() in 'abcd' and len(line) > 1 and (line[1] == '.' or line[1] == ')' or line[1] == ' '):
                if current_question and current_question['type'] != 'short_answer':
                    answer_text = line[2:].strip() if len(line) > 2 else line[1:].strip()
                    
                    # Check for Ä/S format at end (SUPPORT Ä S d s)
                    is_correct_ds = False
                    if answer_text.endswith(' Ä') or answer_text.endswith(' Ä‘') or answer_text.endswith(' D') or answer_text.endswith(' d'):
                        is_correct_ds = True
                        answer_text = answer_text[:-2].strip()
                    elif answer_text.endswith(' S') or answer_text.endswith(' s'):
                        is_correct_ds = False
                        answer_text = answer_text[:-2].strip()
                    
                    # Check for * format
                    is_correct_star = '*' in answer_text or '(ÄÃºng)' in answer_text or '(dung)' in answer_text or '(Dung)' in answer_text
                    answer_text = answer_text.replace('*', '').replace('(ÄÃºng)', '').replace('(dung)', '').replace('(Dung)', '').strip()
                    
                    is_correct = is_correct_ds or is_correct_star
                    
                    current_question['answers'].append({
                        'text': answer_text,
                        'is_statement': True
                    })
                    
                    if is_correct:
                        answer_index = len(current_question['answers']) - 1
                        current_question['correct_answers'].append(answer_index)
                        
                        if current_question['correct'] is None:
                            current_question['correct'] = answer_index
            
            # Check for level
            elif 'muc:' in line.lower() or 'má»©c:' in line.lower() or 'do kho:' in line.lower() or 'Ä‘á»™ khÃ³:' in line.lower():
                if current_question:
                    line_lower = line.lower()
                    if 'nhan biet' in line_lower or 'nháº­n biáº¿t' in line_lower:
                        current_question['level'] = 'nhanbiet'
                    elif 'thong hieu' in line_lower or 'thÃ´ng hiá»ƒu' in line_lower:
                        current_question['level'] = 'thonghieu'
                    elif 'van dung' in line_lower or 'váº­n dá»¥ng' in line_lower:
                        current_question['level'] = 'vandung'
            
            # Check for answer key
            elif 'dap an:' in line.lower() or 'Ä‘Ã¡p Ã¡n:' in line.lower():
                if current_question:
                    for char in line.upper():
                        if char in 'ABCD':
                            current_question['correct'] = ord(char) - ord('A')
                            break
        
        # Add last question
        if current_question and current_question.get('question'):
            if 'type' not in current_question:
                current_question['type'] = 'multiple_choice'
            
            # Auto-detect true/false if multiple correct
            if len(current_question.get('correct_answers', [])) > 1:
                current_question['type'] = 'true_false'
            
            if current_question['type'] == 'multiple_choice' and len(current_question.get('answers', [])) > 0:
                questions.append(current_question)
            elif current_question['type'] in ['true_false', 'short_answer']:
                questions.append(current_question)
        
        return questions
    
    def get_random_question(self, level=None):
        """Get a random question with shuffled answers"""
        available = [q for q in self.questions if q not in self.used_questions]
        
        if level:
            level_questions = [q for q in available if q['level'] == level]
            if level_questions:
                available = level_questions
        
        if not available:
            available = self.questions
            if level:
                level_questions = [q for q in available if q['level'] == level]
                if level_questions:
                    available = level_questions
        
        if available:
            question = random.choice(available).copy()
            self.used_questions.append(question)
            
            if 'type' not in question:
                question['type'] = 'multiple_choice'
            
            # Handle different question types
            if question['type'] == 'multiple_choice':
                answers = question.get('answers', [])
                if not answers:
                    return None
                
                formatted_answers = []
                for i, ans in enumerate(answers):
                    if isinstance(ans, dict):
                        formatted_answers.append((i, ans['text']))
                    else:
                        formatted_answers.append((i, ans))
                
                random.shuffle(formatted_answers)
                
                shuffled_question = question.copy()
                shuffled_question['answers'] = [ans for _, ans in formatted_answers]
                
                for new_idx, (old_idx, _) in enumerate(formatted_answers):
                    if old_idx == question.get('correct'):
                        shuffled_question['correct'] = new_idx
                        break
                
                return shuffled_question
            
            elif question['type'] == 'true_false':
                # Shuffle statements vÃ  update correct_answers indices
                shuffled_question = question.copy()
                answers = question.get('answers', [])
                correct_answers = question.get('correct_answers', [question.get('correct')])
                
                # Handle None in correct_answers
                correct_answers = [c for c in correct_answers if c is not None]
                
                statements = []
                for i, a in enumerate(answers):
                    text = a['text'] if isinstance(a, dict) else a
                    is_correct = (i in correct_answers)
                    statements.append((i, text, is_correct))
                
                random.shuffle(statements)
                
                shuffled_question['statements'] = statements
                shuffled_question['answers'] = [s[1] for s in statements]
                
                # Update correct_answers vá»›i shuffled indices
                new_correct_answers = []
                for new_idx, (old_idx, text, is_correct) in enumerate(statements):
                    if is_correct:
                        new_correct_answers.append(new_idx)
                
                shuffled_question['correct_answers'] = new_correct_answers
                
                # Set correct to first correct answer (for compatibility)
                if new_correct_answers:
                    shuffled_question['correct'] = new_correct_answers[0]
                
                return shuffled_question
            
            elif question['type'] == 'short_answer':
                return question
        
        return None
    
    def has_unused_questions(self):
        """Check if there are unused questions"""
        return len(self.used_questions) < len(self.questions)
    
    def reset_used_questions(self):
        """Reset the list of used questions"""
        self.used_questions = []
    
    def delete_file(self, index):
        """Delete a file and its questions"""
        if 0 <= index < len(self.uploaded_files):
            file_info = self.uploaded_files[index]
            
            questions_before = sum(f['question_count'] for f in self.uploaded_files[:index])
            questions_to_delete = file_info['question_count']
            
            self.questions = (
                self.questions[:questions_before] + 
                self.questions[questions_before + questions_to_delete:]
            )
            
            self.uploaded_files.pop(index)
            
            self.save_data()