from odoo import models, fields, api
import json

class Question(models.Model):
    _name = 'quiz.question'
    _description = 'Quiz Question'
    _order = 'sequence, id'

    quiz_id = fields.Many2one('quiz.quiz', string='Quiz', required=True, ondelete='cascade')
    type = fields.Selection([
        ('mcq_single', 'Multiple Choice (Single Answer)'),
        ('mcq_multi', 'Multiple Choice (Multiple Answers)'),
        ('fill_blank', 'Fill in the Blanks'),
        ('match', 'Match the Following'),
        ('drag_zone', 'Drag and Drop into Zones'),
        ('drag_into_text', 'Drag and Drop into Text'),
    ], string='Question Type', required=True, default='mcq_single')
    
    question_html = fields.Html(string='Question', required=True)
    points = fields.Float(string='Points', default=1.0)
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Relations
    choice_ids = fields.One2many('quiz.choice', 'question_id', string='Choices')
    match_pair_ids = fields.One2many('quiz.match.pair', 'question_id', string='Match Pairs')
    drag_token_ids = fields.One2many('quiz.drag.token', 'question_id', string='Drag Tokens')
    fill_blank_answer_ids = fields.One2many('quiz.fill.blank.answer', 'question_id', string='Fill Blank Answers')

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
                correct_answer = blank_answer.correct_answer.strip().lower()
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
            blank_key = str(token.correct_for_blank)
            if blank_key in placements:
                if placements[blank_key] == token.text:
                    correct_count += 1
        
        return (correct_count / total_tokens) * self.points


class Choice(models.Model):
    _name = 'quiz.choice'
    _description = 'Quiz Choice'
    
    question_id = fields.Many2one('quiz.question', required=True, ondelete='cascade')
    text = fields.Char(string='Choice Text', required=True)
    is_correct = fields.Boolean(string='Is Correct', default=False)


class MatchPair(models.Model):
    _name = 'quiz.match.pair'
    _description = 'Match Pair'
    
    question_id = fields.Many2one('quiz.question', required=True, ondelete='cascade')
    left_text = fields.Char(string='Left Text', required=True)
    right_text = fields.Char(string='Right Text', required=True)


class DragToken(models.Model):
    _name = 'quiz.drag.token'
    _description = 'Drag Token'
    
    question_id = fields.Many2one('quiz.question', required=True, ondelete='cascade')
    text = fields.Char(string='Token Text', required=True)
    correct_for_blank = fields.Integer(string='Correct for Blank Number')


class FillBlankAnswer(models.Model):
    _name = 'quiz.fill.blank.answer'
    _description = 'Fill Blank Answer'
    
    question_id = fields.Many2one('quiz.question', required=True, ondelete='cascade')
    blank_number = fields.Integer(string='Blank Number', required=True)
    correct_answer = fields.Char(string='Correct Answer', required=True)


# Placeholder models for cached database references
class QuizBlank(models.Model):
    _name = 'quiz.blank'
    _description = 'Quiz Blank (Placeholder)'
    
    name = fields.Char(string='Name')


class QuizDragZone(models.Model):
    _name = 'quiz.drag.zone'
    _description = 'Quiz Drag Zone (Placeholder)'
    
    name = fields.Char(string='Name')
