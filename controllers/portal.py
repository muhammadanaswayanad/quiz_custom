from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class QuizCustomerPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        if 'quiz_session_count' in counters:
            session_count = request.env['quiz.session'].sudo().search_count([
                ('user_id', '=', request.env.user.id)
            ])
            values['quiz_session_count'] = session_count
        
        return values
