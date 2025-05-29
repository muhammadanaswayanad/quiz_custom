odoo.define('quiz_engine_pro.sequence', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.QuizSequence = publicWidget.Widget.extend({
        selector: '.sequence-container',
        events: {
            'click .reset-sequence': '_onResetClick',
            'click .move-up': '_onMoveUpClick',
            'click .move-down': '_onMoveDownClick'
        },

        /**
         * @override
         */
        start: function () {
            var self = this;

            // Check if Sortable library is available and initialize it
            if (window.Sortable !== undefined) {
                var sequenceList = this.el.querySelector('.sequence-list');
                if (sequenceList) {
                    this.sortable = new Sortable(sequenceList, {
                        animation: 150,
                        ghostClass: 'sortable-ghost',
                        handle: '.sequence-handle',
                        onEnd: function() {
                            self._updateSequenceData();
                        }
                    });

                    // Randomize on start (only on first load)
                    this._randomizeItems();

                    // Update initial data
                    this._updateSequenceData();
                }
            } else {
                // Fallback to basic functionality if Sortable is not available
                console.warn('Sortable library not loaded. Using basic controls only.');
            }

            // Remove the error message if it exists
            var errorMsg = this.el.querySelector('.alert-info');
            if (errorMsg && errorMsg.textContent.includes('not yet implemented')) {
                errorMsg.remove();
            }

            return this._super.apply(this, arguments);
        },

        /**
         * Randomize the order of sequence items
         *
         * @private
         */
        _randomizeItems: function() {
            var list = this.el.querySelector('.sequence-list');
            if (!list) return;

            var items = Array.from(list.querySelectorAll('.sequence-item'));

            // Shuffle items
            for (var i = items.length - 1; i > 0; i--) {
                var j = Math.floor(Math.random() * (i + 1));
                list.appendChild(items[j]);
            }

            this._updateStepNumbers();
        },

        /**
         * Update the step numbers displayed on items
         *
         * @private
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
         *
         * @private
         */
        _updateSequenceData: function() {
            var data = [];
            var items = this.el.querySelectorAll('.sequence-item');

            for (var i = 0; i < items.length; i++) {
                var stepId = items[i].getAttribute('data-step-id');
                var position = i + 1;

                data.push({
                    'step_id': parseInt(stepId),
                    'position': position
                });
            }

            this._updateStepNumbers();

            var inputEl = this.el.querySelector('input[name="sequence_data"]');
            if (inputEl) {
                inputEl.value = JSON.stringify(data);
            }
        },

        /**
         * Handle reset/randomize button click
         *
         * @private
         */
        _onResetClick: function(ev) {
            ev.preventDefault();
            this._randomizeItems();
            this._updateSequenceData();
        },

        /**
         * Move an item up in the sequence
         *
         * @private
         */
        _onMoveUpClick: function(ev) {
            ev.preventDefault();
            ev.stopPropagation();

            var item = ev.currentTarget.closest('.sequence-item');
            var prev = item.previousElementSibling;

            if (prev) {
                var parent = item.parentNode;
                parent.insertBefore(item, prev);
                this._updateSequenceData();
            }
        },

        /**
         * Move an item down in the sequence
         *
         * @private
         */
        _onMoveDownClick: function(ev) {
            ev.preventDefault();
            ev.stopPropagation();

            var item = ev.currentTarget.closest('.sequence-item');
            var next = item.nextElementSibling;

            if (next) {
                var parent = item.parentNode;
                parent.insertBefore(next, item);
                this._updateSequenceData();
            }
        }
    });

    return publicWidget.registry.QuizSequence;
});
