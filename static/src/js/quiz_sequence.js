odoo.define('quiz_engine_pro.sequence', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    
    publicWidget.registry.QuizSequence = publicWidget.Widget.extend({
        selector: '.sequence-container',
        events: {
            'click .reset-sequence': '_resetSequence'
        },
        
        /**
         * @override
         */
        start: function () {
            this._super.apply(this, arguments);
            this._initSortable();
            return this._super.apply(this, arguments);
        },
        
        /**
         * Initialize Sortable.js for drag and drop functionality
         */
        _initSortable: function() {
            var self = this;
            var sequenceList = this.el.querySelector('.sequence-list');
            
            if (sequenceList && window.Sortable) {
                // Initialize sortable
                this.sortable = new Sortable(sequenceList, {
                    animation: 150,
                    ghostClass: 'sortable-ghost',
                    chosenClass: 'sortable-chosen',
                    dragClass: 'sortable-drag',
                    handle: '.sequence-handle',
                    onEnd: function() {
                        self._updateSequenceData();
                    }
                });
                
                // Randomize on initial load
                this._randomizeSequence();
                
                // Update initial data
                this._updateSequenceData();
            } else {
                console.error('Sortable.js library not loaded or sequence list not found');
            }
        },
        
        /**
         * Randomize the order of sequence items on first load
         */
        _randomizeSequence: function() {
            var items = Array.from(this.el.querySelectorAll('.sequence-item'));
            var list = this.el.querySelector('.sequence-list');
            
            if (!list || items.length === 0) return;
            
            // Shuffle the items
            for (let i = items.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                list.appendChild(items[j]);
            }
            
            this._updateStepNumbers();
        },
        
        /**
         * Update the step numbers displayed on items
         */
        _updateStepNumbers: function() {
            var items = this.el.querySelectorAll('.sequence-item');
            for (var i = 0; i < items.length; i++) {
                var numberElement = items[i].querySelector('.step-number');
                if (numberElement) {
                    numberElement.textContent = (i + 1);
                }
            }
        },
        
        /**
         * Update the hidden input with current sequence data
         */
        _updateSequenceData: function() {
            var data = [];
            var items = this.el.querySelectorAll('.sequence-item');
            
            for (var i = 0; i < items.length; i++) {
                var stepId = items[i].dataset.stepId;
                var position = i + 1;
                
                data.push({
                    'step_id': parseInt(stepId),
                    'position': position
                });
            }
            
            this._updateStepNumbers();
            
            // Update hidden input with JSON data
            var inputEl = this.el.querySelector('input[name="sequence_data"]');
            if (inputEl) {
                inputEl.value = JSON.stringify(data);
            }
        },
        
        /**
         * Reset sequence to original random order
         */
        _resetSequence: function(ev) {
            ev.preventDefault();
            this._randomizeSequence();
            this._updateSequenceData();
        }
    });
    
    return publicWidget.registry.QuizSequence;
});
