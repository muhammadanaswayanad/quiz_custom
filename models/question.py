from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import re

class Question(models.Model):
    _name = 'quiz.question'
    _description = 'Quiz Question'
    _order = 'sequence, id'

    # Basic fields
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Title', compute='_compute_name', store=True)
    quiz_id = fields.Many2one('quiz.quiz', string='Quiz', required=True, ondelete='cascade')
    question_html = fields.Html(string='Question Text', sanitize=True, required=False)
    explanation = fields.Html(string='Explanation', sanitize=True,
                              help="Shown after answering the question")
    points = fields.Float(string='Points', default=1.0)
    
    # Question type selection
    type = fields.Selection([
        ('mcq_single', 'Multiple Choice (Single)'),
        ('mcq_multiple', 'Multiple Choice (Multiple)'),
        ('fill_blank', 'Fill in the Blanks'),
        ('match', 'Match the Following'),
        ('drag_text', 'Drag into Text'),
        ('drag_zone', 'Drag into Zones'),
        ('dropdown_blank', 'Dropdown in Text'),
        ('step_sequence', 'Drag and Drop - Step Sequencing')
    ], string='Type', default='mcq_single', required=True)
    
    # Text template for dropdown_blank type
    text_template = fields.Html(string='Text with Blanks', 
                             help="Use {{1}}, {{2}}, etc. to mark where dropdowns should appear")
    
    # Define relationships correctly with comodel_name
    choice_ids = fields.One2many(comodel_name='quiz.choice', inverse_name='question_id', string='Choices')
    match_pair_ids = fields.One2many(comodel_name='quiz.match.pair', inverse_name='question_id', string='Match Pairs')
    drag_token_ids = fields.One2many(comodel_name='quiz.drag.token', inverse_name='question_id', string='Drag Tokens')
    fill_blank_answer_ids = fields.One2many(comodel_name='quiz.fill.blank.answer', inverse_name='question_id', string='Fill Blank Answers')
    blank_ids = fields.One2many(comodel_name='quiz.blank', inverse_name='question_id', string='Dropdown Blanks')
    sequence_item_ids = fields.One2many('quiz.sequence.item', 'question_id', string='Sequence Items')
    sequence_step_ids = fields.One2many('quiz.sequence.step', 'question_id', string='Sequence Steps')
    
    # Fields for numerical questions
    numerical_exact_value = fields.Float(string='Exact Value', digits=(16, 6))
    numerical_min_value = fields.Float(string='Minimum Value', digits=(16, 6))
    numerical_max_value = fields.Float(string='Maximum Value', digits=(16, 6))
    numerical_tolerance = fields.Float(string='Tolerance (±)', default=0.0, digits=(16, 6))
    
    # Fields for text box questions
    correct_text_answer = fields.Char(string='Correct Answer')
    case_sensitive = fields.Boolean(string='Case Sensitive', default=False)
    allow_partial_match = fields.Boolean(string='Allow Partial Match', default=False)
    keywords = fields.Text(string='Keywords (comma separated)',
                          help="Enter keywords that must be present in the answer, separated by commas")

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
        elif self.type == 'text_box':
            return self._evaluate_text_box(answer_data)
        elif self.type == 'numerical':
            return self._evaluate_numerical(answer_data)
        elif self.type == 'matrix':
            return self._evaluate_matrix(answer_data)
        elif self.type == 'dropdown_blank':
            return self._evaluate_dropdown_blank(answer_data)
        elif self.type == 'drag_order':
            return self._evaluate_drag_order(answer_data)
        elif self.type == 'step_sequence':
            return self._evaluate_step_sequence(answer_data)
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

    def _evaluate_text_box(self, answer_data):
        """Evaluate text box answers"""
        if not answer_data or not self.correct_text_answer:
            return 0.0
        
        user_answer = answer_data.strip()
        correct_answer = self.correct_text_answer.strip()
        
        # Apply case sensitivity
        if not self.case_sensitive:
            user_answer = user_answer.lower()
            correct_answer = correct_answer.lower()
        
        # Exact match
        if user_answer == correct_answer:
            return self.points
        
        # Partial match if allowed
        if self.allow_partial_match:
            if self.keywords:
                keywords = [k.strip() for k in self.keywords.split(',')]
                # Convert to lowercase if not case sensitive
                if not self.case_sensitive:
                    keywords = [k.lower() for k in keywords]
                
                # Check if all keywords are present
                keywords_found = sum(1 for k in keywords if k in user_answer)
                if keywords_found > 0:
                    return (keywords_found / len(keywords)) * self.points
            else:
                # Simple partial match calculation if no specific keywords
                ratio = len(set(user_answer.split()) & set(correct_answer.split())) / len(set(correct_answer.split()))
                if ratio > 0.5:  # More than half the words match
                    return ratio * self.points
        
        return 0.0

    def _evaluate_numerical(self, answer_data):
        """Evaluate numerical answers"""
        if not answer_data:
            return 0.0
        
        try:
            user_value = float(answer_data)
        except (ValueError, TypeError):
            return 0.0
        
        # Exact value with tolerance
        if self.numerical_exact_value is not False:
            if abs(user_value - self.numerical_exact_value) <= self.numerical_tolerance:
                return self.points
        
        # Range check
        if self.numerical_min_value is not False and self.numerical_max_value is not False:
            if self.numerical_min_value <= user_value <= self.numerical_max_value:
                return self.points
        
        return 0.0

    def _evaluate_matrix(self, answer_data):
        """Evaluate matrix questions"""
        if not answer_data:
            return 0.0
        
        try:
            answers = json.loads(answer_data) if isinstance(answer_data, str) else answer_data
        except:
            return 0.0
        
        total_cells = len(self.matrix_row_ids) * len(self.matrix_column_ids)
        if total_cells == 0:
            return 0.0
        
        correct_count = 0
        
        for row in self.matrix_row_ids:
            for col in self.matrix_column_ids:
                cell_key = f"cell_{row.id}_{col.id}"
                expected_value = self._get_matrix_correct_value(row, col)
                
                if cell_key in answers and answers[cell_key] == expected_value:
                    correct_count += 1
        
        return (correct_count / total_cells) * self.points
    
    def _get_matrix_correct_value(self, row, col):
        """Get the correct value for a matrix cell"""
        # Find the correct cell value from the matrix_cell_values model
        cell = self.env['quiz.matrix.cell'].search([
            ('row_id', '=', row.id),
            ('column_id', '=', col.id)
        ], limit=1)
        
        return cell.is_correct if cell else False

    @api.model
    def create(self, vals):
        """Create a new question and add blank rows/columns for matrix questions"""
        res = super(Question, self).create(vals)
        if res.type == 'matrix' and not res.matrix_row_ids and not res.matrix_column_ids:
            # Add default rows and columns for new matrix questions
            self.env['quiz.matrix.row'].create({'question_id': res.id, 'name': 'Row 1'})
            self.env['quiz.matrix.row'].create({'question_id': res.id, 'name': 'Row 2'})
            self.env['quiz.matrix.column'].create({'question_id': res.id, 'name': 'Column 1'})
            self.env['quiz.matrix.column'].create({'question_id': res.id, 'name': 'Column 2'})
        return res
    
    def action_open_matrix_cells(self):
        """Open a view to edit matrix cells"""
        self.ensure_one()
        action = {
            'name': 'Matrix Cells',
            'type': 'ir.actions.act_window',
            'res_model': 'quiz.matrix.cell',
            'view_mode': 'tree',
            'views': [(self.env.ref('quiz_engine_pro.matrix_cell_view_tree').id, 'tree')],
            'domain': [('question_id', '=', self.id)],
            'context': {'default_question_id': self.id},
        }
        return action

    @api.depends('question_html', 'text_template', 'type')
    def _compute_name(self):
        for question in self:
            if question.type == 'dropdown_blank' and question.text_template:
                text = question.text_template or ''
                # Strip tags to get plain text
                text = re.sub(r'<.*?>', '', text)
            else:
                text = question.question_html or ''
                # Strip tags to get plain text
                text = re.sub(r'<.*?>', '', text)
                
            # Limit length for display
            if len(text) > 50:
                text = text[:50] + '...'
            question.name = text or _('New Question')

    @api.constrains('type', 'question_html', 'text_template')
    def _check_required_question_content(self):
        for question in self:
            if question.type == 'dropdown_blank':
                if not question.text_template:
                    raise ValidationError(_("Text template is required for Dropdown in Text questions"))
            else:
                if not question.question_html:
                    raise ValidationError(_("Question Text is required"))

    # This method will auto-fill question_html from text_template for dropdown_blank questions
    @api.onchange('text_template', 'type')
    def _onchange_text_template(self):
        if self.type == 'dropdown_blank' and self.text_template:
            # Copy text template to question_html to satisfy requirements in other parts of code
            self.question_html = self.text_template


    @api.constrains('type')
    def _check_required_fields(self):
        for question in self:
            if question.type == 'mcq_single' or question.type == 'mcq_multiple':
                if not question.choice_ids:
                    raise ValidationError(_('Multiple choice questions must have choices defined.'))
            elif question.type == 'fill_blank':
                if not question.fill_blank_answer_ids:
                    raise ValidationError(_('Fill in the blanks questions must have blank answers defined.'))
            elif question.type == 'match':
                if not question.match_pair_ids:
                    raise ValidationError(_('Match questions must have match pairs defined.'))
            elif question.type == 'drag_text' or question.type == 'drag_zone':
                if not question.drag_token_ids:
                    raise ValidationError(_('Drag and drop questions must have tokens defined.'))
            elif question.type == 'dropdown_blank':
                if not question.text_template:
                    raise ValidationError(_('Dropdown in Text questions must have a text template defined.'))
                if not question.blank_ids:
                    raise ValidationError(_('Dropdown in Text questions must have blanks with options defined.'))
            elif question.type == 'drag_order':
                if not question.sequence_item_ids:
                    raise ValidationError(_('Drag and Drop Ordering questions must have sequence items defined.'))
            elif question.type == 'step_sequence':
                if not question.sequence_step_ids:
                    raise ValidationError(_('Step Sequencing questions must have sequence steps defined.'))


class FillBlankAnswer(models.Model):
    _name = 'quiz.fill.blank.answer'
    _description = 'Fill in the Blank Answer'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10)
    question_id = fields.Many2one(comodel_name='quiz.question', string='Question', ondelete='cascade', required=True)
    blank_number = fields.Integer(string='Blank Number', required=True,
                               help="The number in the {{n}} placeholder")
    answer_text = fields.Char(string='Answer', required=True)
    
    _sql_constraints = [
        ('unique_blank_num_per_question', 
         'UNIQUE(question_id, blank_number)',
         'Each blank number must be unique within a question')
    ]


class DragToken(models.Model):
    _name = 'quiz.drag.token'
    _description = 'Drag and Drop Token'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    question_id = fields.Many2one(comodel_name='quiz.question', string='Question', ondelete='cascade', required=True)
    text = fields.Char(string='Token Text', required=True)
    is_correct = fields.Boolean(string='Is Correct Answer', default=False)
    correct_position = fields.Integer(string='Correct Position', default=0)


class QuizBlank(models.Model):
    _name = 'quiz.blank'
    _description = 'Question Blank'
    _order = 'blank_number, id'
    
    question_id = fields.Many2one(comodel_name='quiz.question', string='Question', ondelete='cascade', required=True)
    blank_number = fields.Integer(string='Blank Number', required=True, 
                                 help="The number in the {{n}} placeholder")
    input_type = fields.Selection([
        ('text', 'Text Input'),
        ('dropdown', 'Dropdown Menu')
    ], string='Input Type', default='dropdown', required=True)
    option_ids = fields.One2many(comodel_name='quiz.option', inverse_name='blank_id', string='Options')
    
    _sql_constraints = [
        ('unique_blank_number_per_question', 
         'UNIQUE(question_id, blank_number)',
         'Each blank number must be unique within a question')
    ]
    
    @api.constrains('input_type', 'option_ids')
    def _check_dropdown_options(self):
        for blank in self:
            if blank.input_type == 'dropdown' and not blank.option_ids:
                raise ValidationError(_("Dropdown blanks must have at least one option defined"))


class QuizOption(models.Model):
    _name = 'quiz.option'
    _description = 'Dropdown Option'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10)
    blank_id = fields.Many2one(comodel_name='quiz.blank', string='Blank', ondelete='cascade', required=True)
    label = fields.Char(string='Option Text', required=True)
    is_correct = fields.Boolean(string='Is Correct Answer', default=False)
    
    @api.constrains('blank_id', 'is_correct')
    def _check_one_correct_answer(self):
        for option in self:
            if option.is_correct:
                correct_count = self.search_count([
                    ('blank_id', '=', option.blank_id.id),
                    ('is_correct', '=', True),
                    ('id', '!=', option.id)
                ])
                if correct_count > 0:
                    raise ValidationError(_("Each dropdown blank can have only one correct answer"))


class Choice(models.Model):
    _name = 'quiz.choice'
    _description = 'Multiple Choice Option'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10)
    question_id = fields.Many2one(comodel_name='quiz.question', string='Question', ondelete='cascade', required=True)
    text = fields.Char(string='Choice Text', required=True)
    is_correct = fields.Boolean(string='Is Correct', default=False)


class MatchPair(models.Model):
    _name = 'quiz.match.pair'
    _description = 'Match Pair'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10)
    question_id = fields.Many2one(comodel_name='quiz.question', string='Question', ondelete='cascade', required=True)
    left_text = fields.Char(string='Left Item', required=True)
    right_text = fields.Char(string='Right Item', required=True)
    right_text = fields.Char(string='Right Item', required=True)


class SequenceItem(models.Model):
    _name = 'quiz.sequence.item'
    _description = 'Sequence Item for Ordering Questions'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10,
                              help="Used for display order in the admin form")
    question_id = fields.Many2one('quiz.question', string='Question', 
                                 ondelete='cascade', required=True)
    label = fields.Char(string='Step Label', required=True,
                       help="The text shown for this step")
    correct_position = fields.Integer(string='Correct Position', required=True,
                                     help="The correct position in the sequence (1, 2, 3, etc.)")
    
    _sql_constraints = [
        ('unique_position_per_question', 
         'UNIQUE(question_id, correct_position)',
         'Each position in the sequence must be unique within a question.')
    ]

class SequenceStep(models.Model):
    _name = 'quiz.sequence.step'
    _description = 'Sequence Step'
    _order = 'correct_position, id'
    
    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    label = fields.Char('Step Label', required=True)
    description = fields.Text('Description')
    correct_position = fields.Integer('Correct Position', required=True)
    
    _sql_constraints = [
        ('unique_position_per_question', 
         'UNIQUE(question_id, correct_position)',
         'Each position must be unique within a question')
    ]
