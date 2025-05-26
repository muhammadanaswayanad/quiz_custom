{
    'name': 'Quiz Engine Pro',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Advanced standalone quiz system',
    'description': """
        A fully independent quiz engine for Odoo 17 Community Edition that allows:
        - Advanced question types (Fill in Blanks, Match the Following, Drag and Drop, MCQ)
        - Custom quiz creation and management
        - Frontend quiz execution
        - Detailed result evaluation
    """,
    'author': 'Odoo Developer',
    'website': 'https://www.example.com',
    'depends': ['base', 'web', 'website'],
    'data': [
        'security/quiz_security.xml',
        'security/ir.model.access.csv',
        'views/quiz_views.xml',
        'views/question_views.xml',
        'views/session_views.xml',
        'views/quiz_templates.xml',
        'views/quiz_menus.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'quiz_custom/static/src/js/quiz_frontend.js',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
