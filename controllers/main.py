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

    @http.route(['/quiz/<string:slug>/start'], type='http', auth='public', methods=['POST'], csrf=False)
    def quiz_start(self, slug, **kwargs):
        """Start a quiz session"""
        quiz = request.env['quiz.quiz'].sudo().search([('slug', '=', slug), ('published', '=', True)], limit=1)
        if not quiz:
            return request.not_found()
        
        participant_name = kwargs.get('participant_name', 'Anonymous')
        participant_email = kwargs.get('participant_email', '')
        
        # Create session
        session = request.env['quiz.session'].sudo().create({
            'quiz_id': quiz.id,
            'participant_name': participant_name,
            'participant_email': participant_email,
            'state': 'in_progress',
            'start_time': fields.Datetime.now(),
        })
        
        return request.redirect(f'/quiz/{slug}/question/1?session={session.token}')

    @http.route(['/quiz/<string:slug>/question/<int:question_num>'], type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def quiz_question(self, slug, question_num, **kwargs):
        """Display or process a quiz question"""
        session_token = request.params.get('session')
        session = request.env['quiz.session'].sudo().search([('token', '=', session_token)], limit=1)
        
        if not session or session.state != 'in_progress':
            return request.redirect('/quiz')
        
        quiz = session.quiz_id
        question = quiz.question_ids[question_num - 1] if quiz.question_ids and len(quiz.question_ids) >= question_num else None
        
        if request.httprequest.method == 'POST' and question:
            # Handle answer submission
            answer_data = request.params.get('answer_data')
            request.env['quiz.answer'].sudo().create({
                'session_id': session.id,
                'question_id': question.id,
                'answer_data': json.dumps(answer_data),
            })
            
            if len(quiz.question_ids) == question_num:
                # Last question, complete the quiz
                session.write({'state': 'completed', 'end_time': fields.Datetime.now()})
                return request.redirect(f'/quiz/{slug}/results?session={session.token}')
            else:
                # Next question
                return request.redirect(f'/quiz/{slug}/question/{question_num + 1}?session={session.token}')
        
        return request.render('quiz_engine_pro.quiz_question', {
            'quiz': quiz,
            'session': session,
            'question': question,
            'question_index': question_num - 1,
        })

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
