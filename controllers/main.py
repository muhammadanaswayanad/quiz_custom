from odoo import http
from odoo.http import request
import json
import uuid


class QuizController(http.Controller):
    
    @http.route('/quiz', type='http', auth='public', website=True)
    def quiz_list(self, **kwargs):
        """List all published quizzes"""
        quizzes = request.env['quiz.quiz'].sudo().search([
            ('is_published', '=', True)
        ])
        
        values = {
            'quizzes': quizzes,
        }
        return request.render('quiz_engine_pro.quiz_list_template', values)

    @http.route('/quiz/<string:slug>', type='http', auth='public', website=True)
    def quiz_start(self, slug, **kwargs):
        """Start page for a specific quiz"""
        quiz = request.env['quiz.quiz'].sudo().search([('slug', '=', slug), ('is_published', '=', True)], limit=1)
        if not quiz:
            return request.not_found()
        
        return request.render('quiz_engine_pro.quiz_start', {
            'quiz': quiz
        })

    @http.route('/quiz/<string:slug>/take', type='http', auth='public', website=True, methods=['POST'])
    def quiz_take(self, slug, **kwargs):
        """Start taking the quiz"""
        quiz = request.env['quiz.quiz'].sudo().search([('slug', '=', slug), ('is_published', '=', True)], limit=1)
        if not quiz:
            return request.not_found()
        
        # Create session
        session_token = str(uuid.uuid4())
        session = request.env['quiz.session'].sudo().create({
            'quiz_id': quiz.id,
            'user_id': request.env.user.id if request.env.user.id != request.env.ref('base.public_user').id else False,
            'session_token': session_token,
            'participant_name': kwargs.get('participant_name'),
            'participant_email': kwargs.get('participant_email'),
        })
        session.start_session()
        
        # Get questions
        questions = quiz.question_ids
        if quiz.randomize_questions:
            questions = questions.sorted(lambda x: x.id)  # Simple randomization
        
        return request.render('quiz_engine_pro.quiz_take', {
            'quiz': quiz,
            'session': session,
            'questions': questions,
            'current_question': questions[0] if questions else None,
            'question_index': 0,
        })

    @http.route('/quiz/session/<string:token>/question/<int:question_id>', type='http', auth='public', website=True)
    def quiz_question(self, token, question_id, **kwargs):
        """Display a specific question"""
        session = request.env['quiz.session'].sudo().search([('session_token', '=', token)], limit=1)
        if not session or session.state != 'in_progress':
            return request.redirect('/quiz')
        
        question = request.env['quiz.question'].sudo().browse(question_id)
        if not question or question.quiz_id != session.quiz_id:
            return request.not_found()
        
        questions = session.quiz_id.question_ids
        question_index = list(questions.ids).index(question_id)
        
        return request.render('quiz_engine_pro.quiz_question', {
            'quiz': session.quiz_id,
            'session': session,
            'question': question,
            'questions': questions,
            'question_index': question_index,
        })

    @http.route('/quiz/session/<string:token>/answer', type='json', auth='public', methods=['POST'])
    def submit_answer(self, token, **kwargs):
        """Submit answer for a question"""
        session = request.env['quiz.session'].sudo().search([('session_token', '=', token)], limit=1)
        if not session or session.state != 'in_progress':
            return {'error': 'Invalid session'}
        
        question_id = kwargs.get('question_id')
        answer_data = kwargs.get('answer_data', {})
        
        # Check if answer already exists
        existing_answer = request.env['quiz.answer'].sudo().search([
            ('session_id', '=', session.id),
            ('question_id', '=', question_id)
        ], limit=1)
        
        if existing_answer:
            existing_answer.write({
                'answer_data': json.dumps(answer_data),
                'answered_at': request.env['ir.fields'].Datetime.now(),
            })
        else:
            request.env['quiz.answer'].sudo().create({
                'session_id': session.id,
                'question_id': question_id,
                'answer_data': json.dumps(answer_data),
            })
        
        return {'success': True}

    @http.route('/quiz/session/<string:token>/complete', type='http', auth='public', website=True, methods=['POST'])
    def quiz_complete(self, token, **kwargs):
        """Complete the quiz"""
        session = request.env['quiz.session'].sudo().search([('session_token', '=', token)], limit=1)
        if not session:
            return request.redirect('/quiz')
        
        session.complete_session()
        
        return request.render('quiz_engine_pro.quiz_results', {
            'session': session,
            'quiz': session.quiz_id,
        })

    @http.route('/quiz/session/<string:token>/results', type='http', auth='public', website=True)
    def quiz_results(self, token, **kwargs):
        """View quiz results"""
        session = request.env['quiz.session'].sudo().search([('session_token', '=', token)], limit=1)
        if not session or session.state != 'completed':
            return request.redirect('/quiz')
        
        return request.render('quiz_engine_pro.quiz_results', {
            'session': session,
            'quiz': session.quiz_id,
        })
