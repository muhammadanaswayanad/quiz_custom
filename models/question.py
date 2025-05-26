from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Question(models.Model):
    _name = 'quiz.question'
    _description = 'Quiz Question'
    _order = 'sequence, id'
    
    quiz_id = fields.Many2one('quiz.quiz', string='Quiz', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    question_type = fields.Selection([
        ('fill_blank', 'Fill in the Blanks'),
        ('match', 'Match the Following'),
        ('drag', 'Drag and Drop Answer'),
        ('mcq', 'Multiple Choice Question'),
        ('drag_into_text', 'Drag and Drop Into Text'),
    ], string='Question Type', required=True, default='mcq')
    
    content = fields.Html(string='Question Content', required=True, sanitize=False)
    points = fields.Float(string='Points', default=1.0)
    negative_marks = fields.Float(string='Negative Marks', default=0.0)
    case_sensitive = fields.Boolean(string='Case Sensitive', default=False, 
                                   help="For fill in the blanks questions")
    partial_scoring = fields.Boolean(string='Partial Scoring', default=False,
                                   help="For MCQ with multiple correct options")
    
    # New field for drag_into_text question type
    text_template = fields.Html(string='Text Template', 
                               help="Text with placeholders like {{1}}, {{2}} where tokens will be dropped")
    
    # Relationship fields based on question type
    answer_option_ids = fields.One2many('quiz.answer.option', 'question_id', string='Answer Options')
    match_pair_ids = fields.One2many('quiz.match.pair', 'question_id', string='Matching Pairs')
    blank_expected_ids = fields.One2many('quiz.blank.expected', 'question_id', string='Expected Answers')
    dragtoken_ids = fields.One2many('quiz.question.dragtoken', 'question_id', string='Drag Tokens')
    
    @api.onchange('question_type')
    def _onchange_question_type(self):
        if self.question_type == 'mcq':
            self.case_sensitive = False
        elif self.question_type == 'fill_blank':
            self.partial_scoring = False
    
    def validate_question(self):
        self.ensure_one()
        if self.question_type == 'mcq' and not self.answer_option_ids:
            raise ValidationError(_("Multiple choice question must have at least one answer option."))
        if self.question_type == 'match' and len(self.match_pair_ids) < 2:
            raise ValidationError(_("Match the following must have at least two pairs."))
        if self.question_type == 'fill_blank' and not self.blank_expected_ids:
            raise ValidationError(_("Fill in the blanks question must have at least one blank to fill."))
        if self.question_type == 'drag' and not self.answer_option_ids:
            raise ValidationError(_("Drag and drop question must have at least one draggable option."))
        if self.question_type == 'drag_into_text' and not self.dragtoken_ids:
            raise ValidationError(_("Drag into text question must have at least one drag token."))
        return True


class AnswerOption(models.Model):
    _name = 'quiz.answer.option'
    _description = 'Quiz Answer Option'
    _order = 'sequence, id'
    
    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    label = fields.Char(string='Option Label', required=True)
    is_correct = fields.Boolean(string='Is Correct', default=False)
    
    @api.constrains('is_correct', 'question_id')
    def _check_has_correct_answer(self):
        for question in self.mapped('question_id'):
            if question.question_type == 'mcq':
                if not any(answer.is_correct for answer in question.answer_option_ids):
                    raise ValidationError(_("Multiple choice question must have at least one correct answer."))


class MatchPair(models.Model):
    _name = 'quiz.match.pair'
    _description = 'Quiz Match Pair'
    _order = 'id'
    
    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    left_item = fields.Char(string='Left Item', required=True)
    right_item = fields.Char(string='Right Item', required=True)


class BlankExpected(models.Model):
    _name = 'quiz.blank.expected'
    _description = 'Quiz Fill in the Blank Expected Answer'
    _order = 'id'
    
    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    placeholder_label = fields.Char(string='Placeholder Label', required=True)
    correct_answer = fields.Char(string='Correct Answer', required=True)


class DragToken(models.Model):
    _name = 'quiz.question.dragtoken'
    _description = 'Quiz Drag Token'
    _order = 'sequence, id'
    
    question_id = fields.Many2one('quiz.question', string='Question', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    label = fields.Char(string='Token Label', required=True, help="Text to be dragged")
    blank_number = fields.Integer(string='Blank Number', required=True, 
                                 help="Target blank number this token belongs to (e.g. 1 for {{1}})")
    is_correct = fields.Boolean(string='Is Correct Match', default=True, 
                               help="Whether this token is correct for its blank")
    
    @api.constrains('blank_number', 'question_id')
    def _check_blank_number_exists(self):
        for token in self:
            if token.blank_number < 1:
                raise ValidationError(_("Blank number must be a positive number."))
