from odoo import api, fields, models
import uuid
import json
import logging

_logger = logging.getLogger(__name__)


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

class QuizResponse(models.Model):
    _name = 'quiz.response'
    _description = 'Quiz Question Response'
    _order = 'id'
    
    session_id = fields.Many2one('quiz.session', string='Session', required=True, ondelete='cascade')
    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    response_data = fields.Text(string='Response Data', help='JSON data containing the user response')
    score = fields.Float(string='Score', default=0)
    max_score = fields.Float(string='Max Score', compute='_compute_max_score', store=True)
    is_correct = fields.Boolean(string='Is Correct', default=False)
    
    @api.depends('question_id')
    def _compute_max_score(self):
        for response in self:
            response.max_score = response.question_id.points
    
    def evaluate_response(self):
        """Evaluate the response and assign a score based on question type"""
        for response in self:
            if not response.response_data:
                continue
                
            try:
                data = json.loads(response.response_data)
                question = response.question_id
                score = 0.0
                is_correct = False
                
                if question.question_type == 'mcq':
                    # For multiple choice questions
                    selected_options = data.get('selected_options', [])
                    
                    if isinstance(selected_options, str):
                        selected_options = [selected_options]
                        
                    selected_options = [int(opt_id) for opt_id in selected_options if opt_id]
                    
                    if selected_options:
                        # Get all options for this question
                        all_options = self.env['quiz.answer.option'].sudo().search([
                            ('question_id', '=', question.id)
                        ])
                        
                        correct_options = all_options.filtered(lambda o: o.is_correct)
                        selected_correct = len(set(selected_options).intersection(set(correct_options.ids)))
                        selected_incorrect = len(selected_options) - selected_correct
                        
                        # Calculate score
                        if question.partial_scoring:
                            # Partial scoring: correct answers add points, incorrect ones subtract
                            score = (selected_correct / len(correct_options)) * question.points
                            if question.negative_marks > 0 and selected_incorrect:
                                score -= selected_incorrect * question.negative_marks
                            score = max(0, score)  # Don't allow negative scores
                        else:
                            # All or nothing
                            if selected_correct == len(correct_options) and selected_incorrect == 0:
                                score = question.points
                                
                        # Mark as correct if all correct options are selected and no incorrect ones
                        is_correct = selected_correct == len(correct_options) and selected_incorrect == 0
                    
                elif question.question_type == 'fill_blank':
                    # For fill in the blanks
                    blanks = data.get('blanks', {})
                    if blanks:
                        total_blanks = len(question.blank_expected_ids)
                        correct_blanks = 0
                        
                        for blank in question.blank_expected_ids:
                            user_answer = blanks.get(str(blank.id), '').strip()
                            correct_answer = blank.correct_answer.strip()
                            
                            if question.case_sensitive:
                                if user_answer == correct_answer:
                                    correct_blanks += 1
                            else:
                                if user_answer.lower() == correct_answer.lower():
                                    correct_blanks += 1
                        
                        # Calculate score based on proportion of correct blanks
                        score = (correct_blanks / total_blanks) * question.points
                        is_correct = correct_blanks == total_blanks
                
                elif question.question_type == 'match':
                    # For matching questions
                    matches = data.get('matches', {})
                    if matches:
                        total_pairs = len(question.match_pair_ids)
                        correct_matches = 0
                        
                        for pair in question.match_pair_ids:
                            user_match = matches.get(str(pair.id), '')
                            if user_match == pair.right_item:
                                correct_matches += 1
                        
                        # Calculate score based on proportion of correct matches
                        score = (correct_matches / total_pairs) * question.points
                        is_correct = correct_matches == total_pairs
                
                elif question.question_type == 'drag':
                    # For drag and drop questions
                    positions = data.get('positions', {})
                    if positions:
                        total_options = len(question.answer_option_ids)
                        correct_positions = 0
                        
                        for option in question.answer_option_ids:
                            user_position = positions.get(str(option.id), '')
                            if str(user_position) == str(option.sequence):
                                correct_positions += 1
                        
                        # Calculate score based on proportion of correct positions
                        score = (correct_positions / total_options) * question.points
                        is_correct = correct_positions == total_options
                
                # Update response with evaluation
                response.write({
                    'score': score,
                    'is_correct': is_correct
                })
                
            except Exception as e:
                _logger.error("Error evaluating response: %s", str(e))
                continue
                
        # Return the updated records
        return True
