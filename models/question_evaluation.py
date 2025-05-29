from odoo import models
import json

class QuestionEvaluation(models.Model):
    _inherit = 'quiz.question'
    
    def evaluate_answer(self, answer_data):
        """Evaluate answer based on question type"""
        if self.type == 'mcq_single':
            return self._evaluate_mcq_single(answer_data)
        elif self.type == 'mcq_multi':
            return self._evaluate_mcq_multi(answer_data)
        elif self.type == 'fill_blank':
            return self._evaluate_fill_blank(answer_data)
        elif self.type == 'match':
            return self._evaluate_match(answer_data)
        elif self.type in ['drag_zone', 'drag_into_text']:
            return self._evaluate_drag_drop(answer_data)
        elif self.type == 'text_box':
            return self._evaluate_text_box(answer_data)
        elif self.type == 'numerical':
            return self._evaluate_numerical(answer_data)
        elif self.type == 'matrix':
            return self._evaluate_matrix(answer_data)
        elif self.type == 'dropdown_blank':
            return self._evaluate_dropdown_blank(answer_data)
        return 0.0

    def _evaluate_mcq_single(self, answer_data):
        """Evaluate single choice MCQ"""
        if not answer_data:
            return 0.0
        
        selected_choice_id = int(answer_data)
        correct_choice = self.choice_ids.filtered('is_correct')
        
        if correct_choice and selected_choice_id == correct_choice[0].id:
            return self.points
        return 0.0

    def _evaluate_mcq_multi(self, answer_data):
        """Evaluate multiple choice MCQ"""
        if not answer_data:
            return 0.0
        
        selected_ids = [int(x) for x in answer_data if x]
        correct_ids = self.choice_ids.filtered('is_correct').ids
        
        if set(selected_ids) == set(correct_ids):
            return self.points
        return 0.0

    def _evaluate_fill_blank(self, answer_data):
        """Evaluate fill in the blanks"""
        if not answer_data:
            return 0.0
        
        try:
            answers = json.loads(answer_data) if isinstance(answer_data, str) else answer_data
        except:
            return 0.0
        
        total_blanks = len(self.fill_blank_answer_ids)
        if total_blanks == 0:
            return 0.0
        
        correct_count = 0
        for blank_answer in self.fill_blank_answer_ids:
            blank_key = str(blank_answer.blank_number)
            if blank_key in answers:
                user_answer = answers[blank_key].strip().lower()
                correct_answer = blank_answer.answer_text.strip().lower()
                if user_answer == correct_answer:
                    correct_count += 1
        
        return (correct_count / total_blanks) * self.points

    def _evaluate_match(self, answer_data):
        """Evaluate matching questions"""
        if not answer_data:
            return 0.0
        
        try:
            matches = json.loads(answer_data) if isinstance(answer_data, str) else answer_data
        except:
            return 0.0
        
        total_pairs = len(self.match_pair_ids)
        if total_pairs == 0:
            return 0.0
        
        correct_count = 0
        for pair in self.match_pair_ids:
            left_key = f"left_{pair.id}"
            right_key = f"right_{pair.id}"
            if left_key in matches and right_key in matches:
                if matches[left_key] == matches[right_key]:
                    correct_count += 1
        
        return (correct_count / total_pairs) * self.points

    def _evaluate_drag_drop(self, answer_data):
        """Evaluate drag and drop questions"""
        if not answer_data:
            return 0.0
        
        try:
            placements = json.loads(answer_data) if isinstance(answer_data, str) else answer_data
        except:
            return 0.0
        
        total_tokens = len(self.drag_token_ids)
        if total_tokens == 0:
            return 0.0
        
        correct_count = 0
        for token in self.drag_token_ids:
            blank_key = str(token.correct_position)
            if blank_key in placements:
                if placements[blank_key] == token.text:
                    correct_count += 1
        
        return (correct_count / total_tokens) * self.points

    def _evaluate_text_box(self, answer_data):
        """Evaluate text box answers"""
        if not answer_data or not self.correct_text_answer:
            return 0.0
        
        user_answer = answer_data.strip()
        correct_answer = self.correct_text_answer.strip()
        
        # Apply case sensitivity
        if not self.case_sensitive:
            user_answer = user_answer.lower()
            correct_answer = correct_answer.lower()
        
        # Exact match
        if user_answer == correct_answer:
            return self.points
        
        # Partial match if allowed
        if self.allow_partial_match:
            if self.keywords:
                keywords = [k.strip() for k in self.keywords.split(',')]
                # Convert to lowercase if not case sensitive
                if not self.case_sensitive:
                    keywords = [k.lower() for k in keywords]
                
                # Check if all keywords are present
                keywords_found = sum(1 for k in keywords if k in user_answer)
                if keywords_found > 0:
                    return (keywords_found / len(keywords)) * self.points
            else:
                # Simple partial match calculation if no specific keywords
                ratio = len(set(user_answer.split()) & set(correct_answer.split())) / len(set(correct_answer.split()))
                if ratio > 0.5:  # More than half the words match
                    return ratio * self.points
        
        return 0.0

    def _evaluate_numerical(self, answer_data):
        """Evaluate numerical answers"""
        if not answer_data:
            return 0.0
        
        try:
            user_value = float(answer_data)
        except (ValueError, TypeError):
            return 0.0
        
        # Exact value with tolerance
        if self.numerical_exact_value is not False:
            if abs(user_value - self.numerical_exact_value) <= self.numerical_tolerance:
                return self.points
        
        # Range check
        if self.numerical_min_value is not False and self.numerical_max_value is not False:
            if self.numerical_min_value <= user_value <= self.numerical_max_value:
                return self.points
        
        return 0.0

    def _evaluate_matrix(self, answer_data):
        """Evaluate matrix questions"""
        if not answer_data:
            return 0.0
        
        try:
            answers = json.loads(answer_data) if isinstance(answer_data, str) else answer_data
        except:
            return 0.0
        
        total_cells = len(self.matrix_row_ids) * len(self.matrix_column_ids)
        if total_cells == 0:
            return 0.0
        
        correct_count = 0
        
        for row in self.matrix_row_ids:
            for col in self.matrix_column_ids:
                cell_key = f"cell_{row.id}_{col.id}"
                expected_value = self._get_matrix_correct_value(row, col)
                
                if cell_key in answers and answers[cell_key] == expected_value:
                    correct_count += 1
        
        return (correct_count / total_cells) * self.points
    
    def _evaluate_dropdown_blank(self, answer_data):
        """Evaluate dropdown in text questions"""
        if not answer_data:
            return 0.0
        
        try:
            answers = json.loads(answer_data) if isinstance(answer_data, str) else answer_data
        except:
            return 0.0
        
        total_blanks = len(self.blank_ids)
        if total_blanks == 0:
            return 0.0
        
        correct_count = 0
        
        # Process each answer
        for entry in answers:
            if 'blank_id' not in entry or 'option_id' not in entry:
                continue
                
            blank_id = entry['blank_id']
            option_id = entry['option_id']
            
            # Check if the selected option is correct
            option = self.env['quiz.option'].sudo().browse(option_id)
            if option and option.is_correct and option.blank_id.id == blank_id:
                correct_count += 1
        
        return (correct_count / total_blanks) * self.points
