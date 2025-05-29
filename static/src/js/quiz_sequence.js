odoo.define('quiz_engine_pro.sequence', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.QuizSequence = publicWidget.Widget.extend({
        selector: '.sequence-container',
        events: {
            'click .reset-sequence': '_onResetClick'
        },

        start: function () {
            var self = this;

            // Initialize Sortable
            if (window.Sortable) {
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

                    // Randomize on start
                    this._randomizeItems();

                    // Update data
                    this._updateSequenceData();
                }
            }

            return this._super.apply(this, arguments);
        },

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

        _updateStepNumbers: function() {
            var items = this.el.querySelectorAll('.sequence-item');
            for (var i = 0; i < items.length; i++) {
                var numEl = items[i].querySelector('.step-number');
                if (numEl) {
                    numEl.textContent = (i + 1);
                }
            }
        },

        _updateSequenceData: function() {
            var data = [];
            var items = this.el.querySelectorAll('.sequence-item');

            for (var i = 0; i < items.length; i++) {
                var stepId = items[i].dataset.stepId;
                if (stepId) {
                    data.push({
                        'step_id': parseInt(stepId),
                        'position': i + 1
                    });
                }
            }

            this._updateStepNumbers();

            var inputEl = this.el.querySelector('input[name="sequence_data"]');
            if (inputEl) {
                inputEl.value = JSON.stringify(data);
            }
        },

        _onResetClick: function(ev) {
            ev.preventDefault();
            this._randomizeItems();
            this._updateSequenceData();
        }
    });

    return publicWidget.registry.QuizSequence;
});
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
