from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Quiz(models.Model):
    _name = 'quiz.quiz'
    _description = 'Quiz'
    _order = 'create_date desc'

    name = fields.Char(string='Title', required=True)
    description = fields.Html(string='Description')
    slug = fields.Char(string='URL Slug', required=True, help="Used in public URL")
    published = fields.Boolean(string='Published', default=False)
    randomize_questions = fields.Boolean(string='Randomize Questions', default=False)
    time_limit = fields.Integer(string='Time Limit (minutes)', default=0, help='0 = No time limit')
    max_attempts = fields.Integer(string='Maximum Attempts', default=1)
    show_results = fields.Boolean(string='Show Results After Completion', default=True)
    passing_score = fields.Float(string='Passing Score (%)', default=60.0)
    
    # Relationships
    question_ids = fields.One2many('quiz.question', 'quiz_id', string='Questions')
    session_ids = fields.One2many('quiz.session', 'quiz_id', string='Quiz Sessions')
    
    # Computed fields
    total_questions = fields.Integer(string='Total Questions', compute='_compute_total_questions')
    total_points = fields.Float(string='Total Points', compute='_compute_total_points')
    
    @api.depends('question_ids')
    def _compute_total_questions(self):
        for quiz in self:
            quiz.total_questions = len(quiz.question_ids)
    
    @api.depends('question_ids.points')
    def _compute_total_points(self):
        for quiz in self:
            quiz.total_points = sum(quiz.question_ids.mapped('points'))
    
    @api.constrains('slug')
    def _check_slug_unique(self):
        for quiz in self:
            if self.search([('slug', '=', quiz.slug), ('id', '!=', quiz.id)]):
                raise ValidationError(_('URL Slug must be unique.'))
    
    @api.model
    def create(self, vals):
        if not vals.get('slug'):
            vals['slug'] = self._generate_slug(vals.get('name', ''))
        return super().create(vals)
    
    def _generate_slug(self, name):
        """Generate URL-friendly slug from name"""
        import re
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    def action_view_public_url(self):
        """Open the public quiz URL in a new tab"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        quiz_url = f"{base_url}/quiz/{self.slug}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': quiz_url,
            'target': 'new',
        }
        return {
            'type': 'ir.actions.act_url',
            'url': quiz_url,
            'target': 'new',
        }
