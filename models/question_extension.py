from odoo import models, fields, api

class Question(models.Model):
    _inherit = 'quiz.question'
    
    def action_open_matrix_cells(self):
        """Open a view to edit matrix cell values"""
        self.ensure_one()
        
        # Create cells for any missing combinations
        self._create_missing_matrix_cells()
        
        return {
            'name': 'Matrix Cells',
            'type': 'ir.actions.act_window',
            'res_model': 'quiz.matrix.cell',
            'view_mode': 'tree',
            'view_id': self.env.ref('quiz_engine_pro.matrix_cell_view_tree').id,
            'domain': [('question_id', '=', self.id)],
            'context': {'default_question_id': self.id},
            'target': 'current',
        }
    
    def _create_missing_matrix_cells(self):
        """Create matrix cells for any missing row-column combinations"""
        self.ensure_one()
        
        if not self.matrix_row_ids or not self.matrix_column_ids:
            return
        
        # Get existing cells
        existing_cells = self.env['quiz.matrix.cell'].search([
            ('question_id', '=', self.id)
        ])
        
        # Track existing combinations
        existing_combinations = {
            (cell.row_id.id, cell.column_id.id): cell
            for cell in existing_cells
        }
        
        # Create missing cells
        cells_to_create = []
        for row in self.matrix_row_ids:
            for col in self.matrix_column_ids:
                if (row.id, col.id) not in existing_combinations:
                    cells_to_create.append({
                        'row_id': row.id,
                        'column_id': col.id,
                        'is_correct': False,
                    })
        
        # Create all missing cells at once
        if cells_to_create:
            self.env['quiz.matrix.cell'].create(cells_to_create)
