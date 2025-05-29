from odoo import models, fields, api, _
from datetime import datetime, timedelta

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
    response_ids = fields.One2many('quiz.response', 'session_id', string='Responses')
    
    # Participant info (for anonymous users)
    participant_name = fields.Char(string='Participant Name')
    participant_email = fields.Char(string='Participant Email')
    
    @api.depends('response_ids.score')
    def _compute_scores(self):
        for session in self:
            session.total_score = sum(session.response_ids.mapped('score'))
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
