from odoo import http, _
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class QuizController(http.Controller):
    
    @http.route('/quiz/<string:slug>', type='http', auth='public', website=True)
    def quiz_start(self, slug=None, **kwargs):
        quiz = request.env['quiz.quiz'].sudo().search([('slug', '=', slug)], limit=1)
        
        if not quiz:
            return request.render('website.404')
            
        # Check if quiz requires login
        if quiz.require_login and not request.env.user._is_public():
            return request.redirect('/web/login?redirect=/quiz/%s' % slug)
            
        # Check if user already has an in-progress session
        if not request.env.user._is_public():
            session = request.env['quiz.session'].sudo().search([
                ('user_id', '=', request.env.user.id),
                ('quiz_id', '=', quiz.id),
                ('state', '=', 'in_progress')
            ], limit=1)
            
            if session:
                return request.redirect('/quiz/%s/session/%s' % (slug, session.id))
                
        values = {
            'quiz': quiz,
            'page_name': quiz.name,
        }
        
        return request.render('quiz_custom.quiz_start_template', values)
        
    @http.route('/quiz/<string:slug>/session/new', type='http', auth='public', website=True, methods=['POST'])
    def create_session(self, slug, **post):
        quiz = request.env['quiz.quiz'].sudo().search([('slug', '=', slug)], limit=1)
        
        if not quiz:
            return request.render('website.404')
            
        # Check if quiz requires login and user is not logged in
        if quiz.require_login and request.env.user._is_public():
            return request.redirect('/web/login?redirect=/quiz/%s' % slug)
            
        # Create new session
        vals = {
            'quiz_id': quiz.id,
        }
        
        if request.env.user._is_public():
            vals.update({
                'user_name': post.get('name', 'Guest'),
                'user_email': post.get('email', ''),
            })
        else:
            vals['user_id'] = request.env.user.id
            
        session = request.env['quiz.session'].sudo().create(vals)
        
        return request.redirect('/quiz/%s/session/%s' % (slug, session.id))
        
    @http.route('/quiz/<string:slug>/session/<int:session_id>', type='http', auth='public', website=True)
    def quiz_take(self, slug, session_id, **kwargs):
        # Get quiz and session
        quiz = request.env['quiz.quiz'].sudo().search([('slug', '=', slug)], limit=1)
        session = request.env['quiz.session'].sudo().browse(session_id)
        
        # Security checks
        if not quiz or not session.exists() or session.quiz_id != quiz:
            return request.render('website.404')
            
        # Check if the session belongs to the current user
        is_owner = False
        if request.env.user._is_public():
            is_owner = not session.user_id
        else:
            is_owner = session.user_id.id == request.env.user.id
            
        if not is_owner and not request.env.user.has_group('quiz_custom.group_quiz_manager'):
            return request.render('website.404')
            
        # Check if session is already completed
        if session.state != 'in_progress':
            return request.redirect('/quiz/%s/session/%s/result' % (slug, session_id))
            
        # Get questions
        questions = request.env['quiz.question'].sudo().search([
            ('quiz_id', '=', quiz.id)
        ])
        
        if quiz.shuffle_questions:
            questions = questions.sorted(lambda q: (0, 0))  # Randomly sort
            
        # Handle one question per page
        if quiz.one_question_per_page:
            question_index = kwargs.get('question', 0)
            try:
                question_index = int(question_index)
                if question_index >= len(questions):
                    # Last question was submitted, go to results
                    return request.redirect('/quiz/%s/session/%s/result' % (slug, session_id))
            except (ValueError, TypeError):
                question_index = 0
                
            current_question = questions[question_index] if questions else False
            question_data = self._prepare_question_data(current_question)
                
            values = {
                'quiz': quiz,
                'session': session,
                'question': current_question,
                'question_data': question_data,
                'question_index': question_index,
                'total_questions': len(questions),
                'page_name': quiz.name,
            }
            
            return request.render('quiz_custom.quiz_question_template', values)
        else:
            # Show all questions at once
            all_questions_data = []
            for q in questions:
                question_data = self._prepare_question_data(q)
                all_questions_data.append({
                    'question': q,
                    'data': question_data,
                })
                
            values = {
                'quiz': quiz,
                'session': session,
                'all_questions_data': all_questions_data,
                'page_name': quiz.name,
            }
            
            return request.render('quiz_custom.quiz_all_questions_template', values)
    
    def _prepare_question_data(self, question):
        """Prepare question data for frontend rendering"""
        data = {}
        
        if question.question_type == 'mcq':
            data['options'] = question.answer_option_ids
            
        elif question.question_type == 'match':
            data['pairs'] = question.match_pair_ids
            
        elif question.question_type == 'drag':
            data['options'] = question.answer_option_ids
            
        elif question.question_type == 'fill_blank':
            data['blanks'] = question.blank_expected_ids
            
        return data
        
    @http.route('/quiz/<string:slug>/session/<int:session_id>/submit', type='http', auth='public', website=True, methods=['POST'])
    def submit_answer(self, slug, session_id, **post):
        quiz = request.env['quiz.quiz'].sudo().search([('slug', '=', slug)], limit=1)
        session = request.env['quiz.session'].sudo().browse(session_id)
        
        if not quiz or not session.exists() or session.state != 'in_progress':
            return request.redirect('/quiz/%s' % slug)
            
        # Handle question submission
        if quiz.one_question_per_page:
            # Single question submission
            question_id = int(post.get('question_id', 0))
            question = request.env['quiz.question'].sudo().browse(question_id)
            
            if not question.exists() or question.quiz_id != quiz:
                return request.redirect('/quiz/%s/session/%s' % (slug, session_id))
                
            # Process answer based on question type
            answer_data = self._process_answer_data(question, post)
            
            # Create or update response
            response = request.env['quiz.response'].sudo().search([
                ('session_id', '=', session.id),
                ('question_id', '=', question.id)
            ], limit=1)
            
            if not response:
                response = request.env['quiz.response'].sudo().create({
                    'session_id': session.id,
                    'question_id': question.id,
                    'answer_json': json.dumps(answer_data),
                })
            else:
                response.write({'answer_json': json.dumps(answer_data)})
                
            # Get next question index
            next_index = int(post.get('question_index', 0)) + 1
            
            # If there are more questions, go to next question
            if next_index < int(post.get('total_questions', 0)):
                return request.redirect('/quiz/%s/session/%s?question=%s' % (slug, session_id, next_index))
            else:
                # Complete the quiz
                session.action_evaluate()
                return request.redirect('/quiz/%s/session/%s/result' % (slug, session_id))
        else:
            # All questions submitted at once
            question_ids = post.getlist('question_ids')
            
            for qid in question_ids:
                try:
                    question_id = int(qid)
                    question = request.env['quiz.question'].sudo().browse(question_id)
                    
                    if question.exists() and question.quiz_id == quiz:
                        # Process answer for this question
                        answer_data = self._process_answer_data(question, post)
                        
                        # Create or update response
                        response = request.env['quiz.response'].sudo().search([
                            ('session_id', '=', session.id),
                            ('question_id', '=', question.id)
                        ], limit=1)
                        
                        if not response:
                            request.env['quiz.response'].sudo().create({
                                'session_id': session.id,
                                'question_id': question.id,
                                'answer_json': json.dumps(answer_data),
                            })
                        else:
                            response.write({'answer_json': json.dumps(answer_data)})
                except (ValueError, TypeError):
                    continue
                    
            # Complete the quiz
            session.action_evaluate()
            return request.redirect('/quiz/%s/session/%s/result' % (slug, session_id))

    def _process_answer_data(self, question, post):
        """Process submitted answer data based on question type"""
        answer_data = {}
        
        if question.question_type == 'mcq':
            # Get selected options
            selected_options = post.getlist('question_%s_option' % question.id)
            try:
                selected_options = [int(opt) for opt in selected_options]
            except (ValueError, TypeError):
                selected_options = []
                
            answer_data = {
                'selected_options': selected_options
            }
                
        elif question.question_type == 'match':
            # Get matched pairs
            matches = {}
            for key, value in post.items():
                if key.startswith('match_%s_' % question.id):
                    try:
                        pair_id = key.split('_')[2]
                        matches[pair_id] = value
                    except (IndexError, ValueError):
                        continue
                        
            answer_data = {
                'matches': matches
            }
                
        elif question.question_type == 'drag':
            # Get dragged positions
            positions = {}
            for key, value in post.items():
                if key.startswith('drag_%s_' % question.id):
                    try:
                        option_id = key.split('_')[2]
                        positions[option_id] = value
                    except (IndexError, ValueError):
                        continue
                        
            answer_data = {
                'positions': positions
            }
                
        elif question.question_type == 'fill_blank':
            # Get filled blanks
            blanks = {}
            for key, value in post.items():
                if key.startswith('blank_%s_' % question.id):
                    try:
                        blank_id = key.split('_')[2]
                        blanks[blank_id] = value
                    except (IndexError, ValueError):
                        continue
                        
            answer_data = {
                'blanks': blanks
            }
            
        return answer_data
        
    @http.route('/quiz/<string:slug>/session/<int:session_id>/result', type='http', auth='public', website=True)
    def quiz_result(self, slug, session_id, **kwargs):
        quiz = request.env['quiz.quiz'].sudo().search([('slug', '=', slug)], limit=1)
        session = request.env['quiz.session'].sudo().browse(session_id)
        
        if not quiz or not session.exists():
            return request.render('website.404')
            
        # Check if the session belongs to the current user or is a quiz manager
        is_owner = False
        if request.env.user._is_public():
            is_owner = not session.user_id
        else:
            is_owner = session.user_id.id == request.env.user.id
            
        if not is_owner and not request.env.user.has_group('quiz_custom.group_quiz_manager'):
            return request.render('website.404')
            
        # If session is still in progress, evaluate it
        if session.state == 'in_progress':
            session.action_evaluate()
            
        # Get response details for review
        responses = session.response_ids.sorted(lambda r: r.question_id.sequence)
        response_details = []
        
        for response in responses:
            # Build response details
            detail = {
                'question': response.question_id,
                'score': response.score,
                'max_score': response.max_score,
                'is_correct': response.is_correct,
            }
            
            # Add answer-specific details based on question type
            if response.answer_json:
                answer_data = json.loads(response.answer_json)
                
                if response.question_id.question_type == 'mcq':
                    detail['selected_options'] = request.env['quiz.answer.option'].sudo().browse(
                        answer_data.get('selected_options', []))
                    detail['correct_options'] = response.question_id.answer_option_ids.filtered(
                        lambda o: o.is_correct)
                    
                elif response.question_id.question_type == 'match':
                    detail['matches'] = answer_data.get('matches', {})
                    detail['correct_matches'] = {str(p.id): p.right_item for p in response.question_id.match_pair_ids}
                    
                elif response.question_id.question_type == 'drag':
                    detail['positions'] = answer_data.get('positions', {})
                    detail['correct_positions'] = {str(o.id): o.sequence for o in response.question_id.answer_option_ids}
                    
                elif response.question_id.question_type == 'fill_blank':
                    detail['blanks'] = answer_data.get('blanks', {})
                    detail['correct_answers'] = {
                        str(b.id): b.correct_answer for b in response.question_id.blank_expected_ids
                    }
                
            response_details.append(detail)
            
        values = {
            'quiz': quiz,
            'session': session,
            'response_details': response_details,
            'page_name': _("Result: %s") % quiz.name,
        }
        
        return request.render('quiz_custom.quiz_result_template', values)
    
    @http.route('/my/quizzes', type='http', auth='user', website=True)
    def my_quizzes(self, **kw):
        """Portal page for user's quiz attempts"""
        sessions = request.env['quiz.session'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], order="create_date desc")
        
        values = {
            'sessions': sessions,
            'page_name': 'my_quizzes',
        }
        
        return request.render('quiz_custom.portal_my_quizzes', values)
    
    # Add this method to portal controller
    @http.route(['/my/home'], type='http', auth="user", website=True)
    def portal_home_inherit_quiz(self, **kw):
        """Add quiz attempts to portal home page"""
        response = super(QuizController, self)._home_portal_redirect(**kw)
        if hasattr(response, 'qcontext'):
            session_count = request.env['quiz.session'].sudo().search_count([
                ('user_id', '=', request.env.user.id)
            ])
            response.qcontext.update({
                'quiz_session_count': session_count,
            })
        return response
