{
    'name': 'Quiz Engine Pro',
    'version': '17.0.1.0.0',
    'category': 'Education',
    'summary': 'Advanced Quiz Engine with Multiple Question Types',
    'description': """
    Standalone Quiz Engine for Odoo 17
    ===================================
    
    Features:
    - Multiple Choice (single/multiple correct)
    - Fill in the Blanks
    - Match the Following
    - Drag and Drop into Zones
    - Drag and Drop Into Text
    - Advanced scoring and analytics
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'web', 'website'],
    'data': [
        'security/access_rights.csv',  # Enable the working CSV file
        'views/quiz_views.xml',
        'views/question_views.xml', 
        'views/session_views.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'quiz_engine_pro/static/src/js/drag_into_text.js',
            'quiz_engine_pro/static/src/css/quiz_styles.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
