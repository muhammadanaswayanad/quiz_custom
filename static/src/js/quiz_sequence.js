odoo.define('quiz_engine_pro.sequence', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.QuizSequence = publicWidget.Widget.extend({
        selector: '.sequence-container',
        events: {
            'click .reset-sequence': '_onClickResetSequence'
        },

        /**
         * @override
         */
        start: function () {
            var self = this;

            // Initialize Sortable if library is loaded
            if (window.Sortable) {
                this.sequenceList = this.el.querySelector('.sequence-list');
                if (this.sequenceList) {
                    this.sortable = new Sortable(this.sequenceList, {
                        animation: 150,
                        ghostClass: 'sortable-ghost',
                        handle: '.sequence-handle',
                        onEnd: function() {
                            self._updateSequenceData();
                        }
                    });

                    // Randomize order on initial load
                    this._randomizeSequence();

                    // Update initial data
                    this._updateSequenceData();
                }
            }

            return this._super.apply(this, arguments);
        },

        /**
         * Randomize the order of sequence items on first load
         *
         * @private
         */
        _randomizeSequence: function() {
            if (!this.sequenceList) return;

            var items = Array.from(this.sequenceList.querySelectorAll('.sequence-item'));

            // Shuffle the items
            for (let i = items.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                this.sequenceList.appendChild(items[j]);
            }

            // Update the step numbers
            this._updateStepNumbers();
        },

        /**
         * Update the step numbers displayed on items
         *
         * @private
         */
        _updateStepNumbers: function() {
            if (!this.sequenceList) return;

            var items = this.sequenceList.querySelectorAll('.sequence-item');
            for (var i = 0; i < items.length; i++) {
                var numberElement = items[i].querySelector('.step-number');
                if (numberElement) {
                    numberElement.textContent = (i + 1);
                }
            }
        },

        /**
         * Update the hidden input with current sequence data
         *
         * @private
         */
        _updateSequenceData: function() {
            if (!this.sequenceList) return;

            var data = [];
            var items = this.sequenceList.querySelectorAll('.sequence-item');

            for (var i = 0; i < items.length; i++) {
                var stepId = items[i].getAttribute('data-step-id');
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
         * Handler for reset button click
         *
         * @private
         */
        _onClickResetSequence: function(ev) {
            ev.preventDefault();
            this._randomizeSequence();
            this._updateSequenceData();
        }
    });

    return publicWidget.registry.QuizSequence;
});
