odoo.define('quiz_engine_pro.sortable', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    
    publicWidget.registry.QuizSortable = publicWidget.Widget.extend({
        selector: '.quiz-sortable-container',
        events: {},
        
        /**
         * @override
         */
        start: function () {
            var self = this;
            this.sortables = [];
            
            // Initialize sortable on the container
            this.$('.sortable-list').each(function() {
                var sortable = new Sortable(this, {
                    group: 'shared',
                    animation: 150,
                    ghostClass: 'sortable-ghost',
                    chosenClass: 'sortable-chosen',
                    dragClass: 'sortable-drag',
                    handle: '.sortable-handle',
                    onEnd: function(evt) {
                        self._updateSortableData();
                    }
                });
                
                self.sortables.push(sortable);
            });
            
            return this._super.apply(this, arguments);
        },
        
        /**
         * Update hidden input with sortable items order
         */
        _updateSortableData: function() {
            var data = [];
            
            this.$('.sortable-item').each(function() {
                var $item = $(this);
                var zone = $item.closest('.sortable-list').data('zone-id');
                var item = $item.data('item-id');
                
                if (zone && item) {
                    data.push({
                        item_id: item,
                        zone_id: zone
                    });
                }
            });
            
            this.$('input[name="sortable_data"]').val(JSON.stringify(data));
        }
    });
    
    return publicWidget.registry.QuizSortable;
});
