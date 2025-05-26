from odoo import api, fields, models
import json


class QuizResponse(models.Model):
    _name = 'quiz.response'
    _description = 'Quiz Answer Response'
    
    session_id = fields.Many2one('quiz.session', string='Session', required=True, ondelete='cascade')
    question_id = fields.Many2one('quiz.question', string='Question', required=True)
    answer_json = fields.Text(string='Answer Data', help='JSON formatted answer data')
    
    score = fields.Float(string='Score Awarded', default=0.0)
    max_score = fields.Float(related='question_id.points', string='Max Score')
    is_correct = fields.Boolean(string='Is Correct', compute='_compute_is_correct', store=True)
    feedback = fields.Text(string='Feedback')
    
    @api.depends('score', 'max_score')
    def _compute_is_correct(self):
        for response in self:
            response.is_correct = response.score >= response.max_score
    
    def evaluate_answer(self):
        self.ensure_one()
        if not self.answer_json:
            self.score = 0
            return
            
        answer_data = json.loads(self.answer_json)
        question = self.question_id
        
        if question.question_type == 'mcq':
            self._evaluate_mcq(answer_data)
        elif question.question_type == 'fill_blank':
            self._evaluate_fill_blank(answer_data)
        elif question.question_type == 'match':
            self._evaluate_matching(answer_data)
        elif question.question_type == 'drag':
            self._evaluate_drag_drop(answer_data)
            
        return True
        
    def _evaluate_mcq(self, answer_data):
        question = self.question_id
        selected_ids = answer_data.get('selected_options', [])
        
        # Get all options and correct options
        all_options = self.question_id.answer_option_ids
        correct_options = all_options.filtered(lambda o: o.is_correct)
        correct_ids = correct_options.ids
        
        # Check if single-correct question is correctly answered
        if len(correct_options) == 1 and len(selected_ids) == 1:
            self.score = question.points if selected_ids[0] in correct_ids else 0
            return
            
        # Multiple correct options
        if not question.partial_scoring:
            # All or nothing
            if set(selected_ids) == set(correct_ids):
                self.score = question.points
            else:
                self.score = 0
        else:
            # Partial scoring
            total_correct = len(correct_options)
            if total_correct == 0:
                self.score = 0
                return
                
            correct_selected = sum(1 for opt_id in selected_ids if opt_id in correct_ids)
            incorrect_selected = len(selected_ids) - correct_selected
            
            # Calculate score based on correct answers minus incorrect selections
            raw_score = (correct_selected / total_correct) - (incorrect_selected / len(all_options))
            self.score = max(0, raw_score * question.points)  # Ensure non-negative score
    
    def _evaluate_fill_blank(self, answer_data):
        question = self.question_id
        submitted_answers = answer_data.get('blanks', {})
        expected_answers = {str(blank.id): blank.correct_answer for blank in question.blank_expected_ids}
        
        if not expected_answers:
            self.score = 0
            return
            
        correct_count = 0
        for blank_id, expected in expected_answers.items():
            submitted = submitted_answers.get(blank_id, '')
            
            if question.case_sensitive:
                is_correct = submitted == expected
            else:
                is_correct = submitted.lower() == expected.lower()
                
            if is_correct:
                correct_count += 1
        
        # Calculate score based on proportion of correct answers
        self.score = (correct_count / len(expected_answers)) * question.points
    
    def _evaluate_matching(self, answer_data):
        question = self.question_id
        submitted_matches = answer_data.get('matches', {})
        
        # Create a dictionary of correct matches
        correct_matches = {str(pair.id): pair.right_item for pair in question.match_pair_ids}
        
        if not correct_matches:
            self.score = 0
            return
            
        # Count correct matches
        correct_count = sum(1 for pair_id, right_item in submitted_matches.items() 
                           if pair_id in correct_matches and submitted_matches[pair_id] == correct_matches[pair_id])
        
        # Calculate score based on proportion of correct matches
        self.score = (correct_count / len(correct_matches)) * question.points
    
    def _evaluate_drag_drop(self, answer_data):
        question = self.question_id
        submitted_positions = answer_data.get('positions', {})
        
        # For drag and drop, the correct positions should be defined in the answer options
        # Each option should have an expected position/zone
        correct_positions = {str(option.id): option.sequence for option in question.answer_option_ids}
        
        if not correct_positions:
            self.score = 0
            return
            
        # Count correct placements
        correct_count = sum(1 for option_id, position in submitted_positions.items() 
                           if option_id in correct_positions and int(submitted_positions[option_id]) == correct_positions[option_id])
        
        # Calculate score based on proportion of correct placements
        self.score = (correct_count / len(correct_positions)) * question.points
