from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """Add response_data field if it doesn't exist"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check if the field exists in the database
    cr.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'quiz_response' AND column_name = 'response_data';")
    if cr.fetchone()[0] == 0:
        # Field doesn't exist, add it
        cr.execute("ALTER TABLE quiz_response ADD COLUMN response_data text;")
        env.cr.commit()
