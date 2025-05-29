from odoo import models, fields, api, _
import json


class QuizAnswer(models.Model):
    _name = 'quiz.answer'
    _description = 'Quiz Answer'

    session_id = fields.Many2one('quiz.session', string='Session', required=True, ondelete='cascade')
    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    
    # Answer data stored as JSON
    answer_data = fields.Text(string='Answer Data', help='JSON containing the answer details')
    score = fields.Float(string='Score')
    max_score = fields.Float(string='Maximum Score', related='question_id.points', store=True)
    
    # Timing
    time_spent = fields.Float(string='Time Spent (seconds)')
    answered_at = fields.Datetime(string='Answered At', default=fields.Datetime.now)
    
    @api.model
    def create(self, vals):
        answer = super().create(vals)
        answer._compute_score()
        return answer
    
    def write(self, vals):
        result = super().write(vals)
        if 'answer_data' in vals:
            self._compute_score()
        return result
    
    def _compute_score(self):
        for answer in self:
            if answer.answer_data and answer.question_id:
                try:
                    answer_data = json.loads(answer.answer_data)
                    answer.score = answer.question_id.evaluate_answer(answer_data)
                except (json.JSONDecodeError, AttributeError):
                    answer.score = 0.0
    
    def get_answer_data_dict(self):
        try:
            return json.loads(self.answer_data) if self.answer_data else {}
        except json.JSONDecodeError:
            return {}
    
    def set_answer_data_dict(self, data):
        self.answer_data = json.dumps(data)


class Response(models.Model):
    _name = 'quiz.response'
    _description = 'Quiz Response'
    
    session_id = fields.Many2one('quiz.session', required=True, ondelete='cascade')
    question_id = fields.Many2one('quiz.question', required=True, ondelete='cascade')
    answer_data = fields.Text(string='Answer Data')
    score = fields.Float(string='Score', default=0.0)
    is_correct = fields.Boolean(string='Is Correct', compute='_compute_is_correct', store=True)
    
    @api.depends('score', 'question_id.points')
    def _compute_is_correct(self):
        for record in self:
            if record.question_id.points > 0:
                record.is_correct = record.score >= record.question_id.points
            else:
                record.is_correct = False
                self.write({'state': 'expired'})
                return True
        return False


class QuizAnswer(models.Model):
    _name = 'quiz.answer'
    _description = 'Quiz Answer'

    session_id = fields.Many2one('quiz.session', string='Session', required=True, ondelete='cascade')
    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    
    # Answer data stored as JSON
    answer_data = fields.Text(string='Answer Data', help='JSON containing the answer details')
    score = fields.Float(string='Score')
    max_score = fields.Float(string='Maximum Score', related='question_id.points', store=True)
    
    # Timing
    time_spent = fields.Float(string='Time Spent (seconds)')
    answered_at = fields.Datetime(string='Answered At', default=fields.Datetime.now)
    
    @api.model
    def create(self, vals):
        answer = super().create(vals)
        answer._compute_score()
        return answer
    
    def write(self, vals):
        result = super().write(vals)
        if 'answer_data' in vals:
            self._compute_score()
        return result
    
    def _compute_score(self):
        for answer in self:
            if answer.answer_data and answer.question_id:
                try:
                    answer_data = json.loads(answer.answer_data)
                    answer.score = answer.question_id.evaluate_answer(answer_data)
                except (json.JSONDecodeError, AttributeError):
                    answer.score = 0.0
    
    def get_answer_data_dict(self):
        try:
            return json.loads(self.answer_data) if self.answer_data else {}
        except json.JSONDecodeError:
            return {}
    
    def set_answer_data_dict(self, data):
        self.answer_data = json.dumps(data)


class Response(models.Model):
    _name = 'quiz.response'
    _description = 'Quiz Response'
    
    session_id = fields.Many2one('quiz.session', required=True, ondelete='cascade')
    question_id = fields.Many2one('quiz.question', required=True, ondelete='cascade')
    answer_data = fields.Text(string='Answer Data')
    score = fields.Float(string='Score', default=0.0)
    is_correct = fields.Boolean(string='Is Correct', compute='_compute_is_correct', store=True)
    
    @api.depends('score', 'question_id.points')
    def _compute_is_correct(self):
        for record in self:
            if record.question_id.points > 0:
                record.is_correct = record.score >= record.question_id.points
            else:
                record.is_correct = False
