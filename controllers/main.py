from odoo import http, fields
from odoo.http import request
import json
import uuid


class QuizController(http.Controller):

    @http.route(['/quiz'], type='http', auth='public', website=True)
    def quiz_list(self, **kwargs):
        """List all published quizzes"""
        quizzes = request.env['quiz.quiz'].sudo().search([('published', '=', True)])
        
        values = {
            'quizzes': quizzes,
        }
        return request.render('quiz_engine_pro.quiz_list', values)

    @http.route(['/quiz/<string:slug>'], type='http', auth='public', website=True)
    def quiz_detail(self, slug, **kwargs):
        """Show quiz details and start form"""
        quiz = request.env['quiz.quiz'].sudo().search([('slug', '=', slug), ('published', '=', True)], limit=1)
        if not quiz:
            return request.not_found()
        
        values = {
            'quiz': quiz,
        }
        return request.render('quiz_engine_pro.quiz_detail', values)

    @http.route(['/quiz/<string:slug>/start'], type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def quiz_start(self, slug, **kwargs):
        """Start a quiz session"""
        quiz = request.env['quiz.quiz'].sudo().search([('slug', '=', slug), ('published', '=', True)], limit=1)
        if not quiz:
            return request.not_found()
        
        participant_name = kwargs.get('participant_name', 'Anonymous')
        participant_email = kwargs.get('participant_email', '')
        
        # Generate unique session token
        session_token = str(uuid.uuid4())
        
        # Create quiz session with token
        session = request.env['quiz.session'].sudo().create({
            'quiz_id': quiz.id,
            'participant_name': participant_name,
            'participant_email': participant_email,
            'session_token': session_token,
            'state': 'in_progress',
            'start_time': fields.Datetime.now(),
        })
        
        return request.redirect(f'/quiz/{slug}/question/1?session={session.session_token}')

    @http.route(['/quiz/<string:slug>/question/<int:question_num>'], type='http', auth='public', methods=['GET', 'POST'], csrf=False, website=True)
    def quiz_question(self, slug, question_num, **kwargs):
        """Display or process a quiz question"""
        session_token = request.params.get('session')
        session = request.env['quiz.session'].sudo().search([('session_token', '=', session_token)], limit=1)
        
        if not session or session.state != 'in_progress':
            return request.redirect('/quiz')
        
        quiz = session.quiz_id
        question = quiz.question_ids[question_num - 1] if quiz.question_ids and len(quiz.question_ids) >= question_num else None
        
        if not question:
            return request.redirect('/quiz')
        
        if request.httprequest.method == 'POST':
            # Handle answer submission
            answer_data = request.params.get('answer_data')
            request.env['quiz.response'].sudo().create({
                'session_id': session.id,
                'question_id': question.id,
                'answer_data': json.dumps(answer_data) if answer_data else '{}',
            })
            
            if len(quiz.question_ids) == question_num:
                # Last question, complete the quiz
                session.write({'state': 'completed', 'end_time': fields.Datetime.now()})
                return request.redirect(f'/quiz/session/{session.session_token}/results')
            else:
                # Next question
                return request.redirect(f'/quiz/{slug}/question/{question_num + 1}?session={session.session_token}')
        
        values = {
            'quiz': quiz,
            'session': session,
            'question': question,
            'question_index': question_num - 1,
        }
        return request.render('quiz_engine_pro.quiz_question', values)

    @http.route('/quiz/session/<string:token>/results', type='http', auth='public', website=True)
    def quiz_results(self, token, **kwargs):
        """View quiz results"""
        session = request.env['quiz.session'].sudo().search([('session_token', '=', token)], limit=1)
        if not session:
            return request.redirect('/quiz')
        
        # Calculate results if not already calculated
        if session.state == 'completed' and not session.total_score:
            responses = request.env['quiz.response'].sudo().search([('session_id', '=', session.id)])
            total_score = 0
            max_score = sum(session.quiz_id.question_ids.mapped('points'))
            
            # Calculate score based on responses
            for response in responses:
                # Basic scoring - this would be enhanced based on question type
                if response.answer_data:
                    total_score += response.question_id.points
            
            percentage = (total_score / max_score * 100) if max_score > 0 else 0
            
            session.write({
                'total_score': total_score,
                'percentage': percentage,
                'passed': percentage >= session.quiz_id.passing_score,
            })
        
        values = {
            'session': session,
            'quiz': session.quiz_id,
            'max_score': sum(session.quiz_id.question_ids.mapped('points')),
        }
        return request.render('quiz_engine_pro.quiz_results', values)

    def _evaluate_answer(self, question, answer_data):
        """Evaluate answer based on question type"""
        if not answer_data:
            return 0
            
        try:
            # Convert answer_data to proper format if needed
            if isinstance(answer_data, str):
                answer_data = json.loads(answer_data)
                
            # Evaluate based on question type
            if question.type == 'mcq_single':
                # ...existing code...
                pass
                
            elif question.type == 'mcq_multiple':
                # ...existing code...
                pass
                
            # ...other question types...
                
            elif question.type == 'step_sequence':
                # Sequencing evaluation
                try:
                    if not answer_data or not question.sequence_item_ids:
                        return 0.0
                        
                    data = json.loads(answer_data) if isinstance(answer_data, str) else answer_data
                    total_steps = len(question.sequence_item_ids)
                    
                    # Get correct positions from question
                    correct_positions = {}
                    for item in question.sequence_item_ids:
                        correct_positions[item.id] = item.correct_position
                    
                    # Get the user's sequence
                    user_sequence = {}
                    for entry in data:
                        step_id = entry.get('step_id')
                        position = entry.get('position')
                        if step_id and position:
                            user_sequence[step_id] = position - 1  # Adjust for 0-indexed
                    
                    # Count correct positions
                    correct_count = 0
                    for step_id, correct_pos in correct_positions.items():
                        if step_id in user_sequence and user_sequence[step_id] == correct_pos:
                            correct_count += 1
                    
                    # Calculate score as percentage of correct positions
                    return (correct_count / total_steps) * question.points
                    
                except Exception as e:
                    _logger.exception("Error evaluating sequence question: %s", e)
                    return 0.0
            
            return 0
            
        except Exception as e:
            _logger.error(f"Error evaluating answer: {e}")
            return 0
