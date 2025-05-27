from odoo import models, fields, api, _
from datetime import datetime, timedelta
import json


class QuizSession(models.Model):
    _name = 'quiz.session'
    _description = 'Quiz Session'
    _order = 'create_date desc'

    quiz_id = fields.Many2one('quiz.quiz', string='Quiz', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User')
    session_token = fields.Char(string='Session Token', required=True)
    
    # Session status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ], string='State', default='draft')
    
    # Timing
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    time_limit = fields.Integer(string='Time Limit (minutes)')
    
    # Scoring
    total_score = fields.Float(string='Total Score', compute='_compute_scores', store=True)
    max_score = fields.Float(string='Maximum Score', compute='_compute_scores', store=True)
    percentage = fields.Float(string='Percentage', compute='_compute_scores', store=True)
    passed = fields.Boolean(string='Passed', compute='_compute_passed', store=True)
    
    # Relationships
    answer_ids = fields.One2many('quiz.answer', 'session_id', string='Answers')
    
    # Participant info (for anonymous users)
    participant_name = fields.Char(string='Participant Name')
    participant_email = fields.Char(string='Participant Email')
    
    @api.depends('answer_ids.score')
    def _compute_scores(self):
        for session in self:
            session.total_score = sum(session.answer_ids.mapped('score'))
            session.max_score = session.quiz_id.total_points
            session.percentage = (session.total_score / session.max_score * 100) if session.max_score > 0 else 0
    
    @api.depends('percentage', 'quiz_id.passing_score')
    def _compute_passed(self):
        for session in self:
            session.passed = session.percentage >= session.quiz_id.passing_score
    
    def start_session(self):
        self.write({
            'state': 'in_progress',
            'start_time': fields.Datetime.now(),
            'time_limit': self.quiz_id.time_limit,
        })
    
    def complete_session(self):
        self.write({
            'state': 'completed',
            'end_time': fields.Datetime.now(),
        })
    
    def check_expiry(self):
        if self.state == 'in_progress' and self.time_limit > 0:
            if self.start_time + timedelta(minutes=self.time_limit) < datetime.now():
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


class QuizResponse(models.Model):
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
