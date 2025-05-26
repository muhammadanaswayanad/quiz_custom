from odoo import api, fields, models
import uuid


class Quiz(models.Model):
    _name = 'quiz.quiz'
    _description = 'Quiz'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Title', required=True, tracking=True)
    description = fields.Html(string='Description')
    is_published = fields.Boolean(string='Published', default=False, tracking=True)
    shuffle_questions = fields.Boolean(string='Shuffle Questions', default=False)
    one_question_per_page = fields.Boolean(string='One Question Per Page', default=True)
    time_limit = fields.Integer(string='Time Limit (minutes)', default=0, 
                               help="0 means no time limit")
    require_login = fields.Boolean(string='Login Required', default=False)
    slug = fields.Char(string='URL Slug', index=True, copy=False)
    
    question_ids = fields.One2many('quiz.question', 'quiz_id', string='Questions')
    session_ids = fields.One2many('quiz.session', 'quiz_id', string='Sessions')
    
    total_marks = fields.Float(compute='_compute_total_marks', string='Total Marks', store=True)
    question_count = fields.Integer(compute='_compute_question_count', string='Questions')
    session_count = fields.Integer(compute='_compute_session_count', string='Attempts')
    
    @api.depends('question_ids', 'question_ids.points')
    def _compute_total_marks(self):
        for quiz in self:
            quiz.total_marks = sum(quiz.question_ids.mapped('points'))
    
    @api.depends('question_ids')
    def _compute_question_count(self):
        for quiz in self:
            quiz.question_count = len(quiz.question_ids)
    
    @api.depends('session_ids')
    def _compute_session_count(self):
        for quiz in self:
            quiz.session_count = len(quiz.session_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('slug'):
                vals['slug'] = uuid.uuid4().hex[:8]
        return super().create(vals_list)
        
    def action_view_questions(self):
        self.ensure_one()
        return {
            'name': 'Questions',
            'type': 'ir.actions.act_window',
            'res_model': 'quiz.question',
            'view_mode': 'tree,form',
            'domain': [('quiz_id', '=', self.id)],
            'context': {'default_quiz_id': self.id},
        }
        
    def action_view_sessions(self):
        self.ensure_one()
        return {
            'name': 'Quiz Attempts',
            'type': 'ir.actions.act_window',
            'res_model': 'quiz.session',
            'view_mode': 'tree,form',
            'domain': [('quiz_id', '=', self.id)],
            'context': {'default_quiz_id': self.id},
        }
