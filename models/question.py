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
    
    # Relationships for different question types
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
        elif self.type == 'drag_zone':
            return self._evaluate_drag_zone(answer_data)
        elif self.type == 'drag_into_text':
            return self._evaluate_drag_into_text(answer_data)
        return 0.0
    
    def _evaluate_mcq_single(self, answer_data):
        choice_id = answer_data.get('choice_id')
        correct_choice = self.choice_ids.filtered('is_correct')
        return self.points if correct_choice and correct_choice.id == choice_id else 0.0
    
    def _evaluate_mcq_multi(self, answer_data):
        selected_ids = set(answer_data.get('choice_ids', []))
        correct_ids = set(self.choice_ids.filtered('is_correct').ids)
        return self.points if selected_ids == correct_ids else 0.0
    
    def _evaluate_fill_blank(self, answer_data):
        answers = answer_data.get('answers', {})
        correct = 0
        total = len(self.blank_ids)
        for blank in self.blank_ids:
            user_answer = answers.get(str(blank.id), '').strip().lower()
            if user_answer in blank.correct_answers.lower().split(','):
                correct += 1
        return (correct / total) * self.points if total > 0 else 0.0
    
    def _evaluate_match(self, answer_data):
        matches = answer_data.get('matches', {})
        correct = 0
        total = len(self.match_pair_ids)
        for pair in self.match_pair_ids:
            if matches.get(str(pair.left_id)) == pair.right_id:
                correct += 1
        return (correct / total) * self.points if total > 0 else 0.0
    
    def _evaluate_drag_zone(self, answer_data):
        placements = answer_data.get('placements', {})
        # Implementation depends on specific requirements
        return 0.0  # Placeholder
    
    def _evaluate_drag_into_text(self, answer_data):
        placements = answer_data.get('placements', {})
        correct = 0
        total_blanks = len(set(self.drag_token_ids.mapped('blank_number')))
        
        for token in self.drag_token_ids.filtered('is_correct'):
            blank_key = str(token.blank_number)
            if placements.get(blank_key) == token.label:
                correct += 1
        
        return (correct / total_blanks) * self.points if total_blanks > 0 else 0.0


class Choice(models.Model):
    _name = 'quiz.choice'
    _description = 'Quiz Choice'
    
    question_id = fields.Many2one('quiz.question', required=True, ondelete='cascade')
    text = fields.Char(string='Choice Text', required=True)
    is_correct = fields.Boolean(string='Is Correct', default=False)

    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    text = fields.Html(string='Choice Text', required=True)
    is_correct = fields.Boolean(string='Is Correct')
    
    question_id = fields.Many2one('quiz.question', required=True, ondelete='cascade')
class QuizBlank(models.Model):ring='Left Text', required=True)
    _name = 'quiz.blank'Char(string='Right Text', required=True)
    _description = 'Quiz Fill in the Blank'

    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    blank_number = fields.Integer(string='Blank Number', required=True)
    correct_answers = fields.Char(string='Correct Answers', required=True, 
                                  help='Comma-separated list of correct answers')
    question_id = fields.Many2one('quiz.question', required=True, ondelete='cascade')
    text = fields.Char(string='Token Text', required=True)
class QuizMatchPair(models.Model):eger(string='Correct for Blank Number')
    _name = 'quiz.match.pair'
    _description = 'Quiz Match Pair'
# Add missing model for fill blank answers
    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    left_text = fields.Char(string='Left Item', required=True)
    right_text = fields.Char(string='Right Item', required=True)
    left_id = fields.Integer(string='Left ID')
    right_id = fields.Integer(string='Right ID')', required=True, ondelete='cascade')
    blank_number = fields.Integer(string='Blank Number', required=True)
    correct_answer = fields.Char(string='Correct Answer', required=True)
class QuizDragZone(models.Model):
    _name = 'quiz.drag.zone'
    _description = 'Quiz Drag Zone'

    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    zone_id = fields.Char(string='Zone ID', required=True)
    zone_label = fields.Char(string='Zone Label')
    correct_items = fields.Text(string='Correct Items JSON')


class QuizDragToken(models.Model):
    _name = 'quiz.drag.token'
    _description = 'Drag Token for Questions'
    _rec_name = 'text'
    
    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    text = fields.Char(string='Token Text', required=True)
    correct_for_blank = fields.Integer(string='Correct for Blank Number', help="Which blank number (1, 2, 3...) this token is correct for")
