from odoo import api, fields, models
import uuid


class QuizSession(models.Model):
    _name = 'quiz.session'
    _description = 'Quiz Session'
    _order = 'create_date desc'
    
    name = fields.Char(string='Reference', default=lambda self: uuid.uuid4().hex[:8], readonly=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    user_name = fields.Char(string='Guest Name')
    user_email = fields.Char(string='Guest Email')
    quiz_id = fields.Many2one('quiz.quiz', string='Quiz', required=True)
    
    start_time = fields.Datetime(string='Start Time', default=fields.Datetime.now, readonly=True)
    end_time = fields.Datetime(string='End Time')
    time_spent = fields.Float(string='Time Spent (min)', compute='_compute_time_spent', store=True)
    
    score = fields.Float(string='Score', compute='_compute_score', store=True)
    max_score = fields.Float(related='quiz_id.total_marks', string='Max Score')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)
    
    state = fields.Selection([
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ], string='Status', default='in_progress')
    
    response_ids = fields.One2many('quiz.response', 'session_id', string='Responses')
    
    current_question_index = fields.Integer(string='Current Question', default=0)
    
    @api.depends('start_time', 'end_time')
    def _compute_time_spent(self):
        for session in self:
            if session.start_time and session.end_time:
                delta = session.end_time - session.start_time
                session.time_spent = delta.total_seconds() / 60
            else:
                session.time_spent = 0
    
    @api.depends('response_ids', 'response_ids.score')
    def _compute_score(self):
        for session in self:
            session.score = sum(response.score for response in session.response_ids)
    
    @api.depends('score', 'max_score')
    def _compute_percentage(self):
        for session in self:
            if session.max_score:
                session.percentage = (session.score / session.max_score) * 100
            else:
                session.percentage = 0
                
    def mark_completed(self):
        self.ensure_one()
        self.write({
            'state': 'completed',
            'end_time': fields.Datetime.now(),
        })
        return True
        
    def action_evaluate(self):
        self.ensure_one()
        for response in self.response_ids:
            response.evaluate_answer()
        return self.mark_completed()
