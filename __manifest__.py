{
    'name': 'Quiz Engine Pro',
    'version': '17.0.1.0.3',
    'category': 'Education',
    'summary': 'Advanced Quiz Engine with Multiple Question Types',
    'description': """
        Comprehensive quiz engine supporting:
        - Multiple Choice Questions
        - Fill in the Blanks
        - Drag and Drop
        - Matching Questions
        - Real-time scoring
        - Public quiz access
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'website'],
    'external_dependencies': {'python': []},
    'data': [
        'security/ir.model.access.csv',
        'views/quiz_views.xml',
        'views/question_views.xml', 
        'views/session_views.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'quiz_engine_pro/static/src/css/quiz_styles.css',
            'quiz_engine_pro/static/src/css/quiz_drag_drop.css',
            'quiz_engine_pro/static/src/js/simple_drag_drop.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
