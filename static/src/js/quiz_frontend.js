odoo.define('quiz_custom.frontend', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    
    // Initialize drag and drop functionality using Sortable.js
    publicWidget.registry.QuizDragDrop = publicWidget.Widget.extend({
        selector: '.drag-container',

        start: function () {
            var self = this;
            this._super.apply(this, arguments);

            // Use Sortable.js for drag-items and drop-zones
            if (!window.Sortable) {
                $.getScript('https://cdn.jsdelivr.net/npm/sortablejs@1.14.0/Sortable.min.js', function () {
                    self._initDragDrop();
                });
            } else {
                this._initDragDrop();
            }
        },

        _initDragDrop: function () {
            var self = this;
            var $dragItems = this.$el.find('.drag-items')[0];
            var $dropZones = this.$el.find('.drop-zone');

            // Make drag-items draggable (from pool)
            if ($dragItems) {
                new Sortable($dragItems, {
                    group: {
                        name: 'quiz-drag-' + this.$el.data('questionId'),
                        pull: 'clone',
                        put: false
                    },
                    sort: false,
                    animation: 150
                });
            }

            // Each drop-zone accepts one item
            $dropZones.each(function () {
                var dropZone = this;
                new Sortable(dropZone, {
                    group: {
                        name: 'quiz-drag-' + self.$el.data('questionId'),
                        pull: false,
                        put: true
                    },
                    animation: 150,
                    sort: false,
                    onAdd: function (evt) {
                        // Only one item per drop zone
                        var $zone = $(evt.to);
                        $zone.find('.drag-item').not(evt.item).each(function () {
                            // Move any previous item back to pool
                            $dragItems.appendChild(this);
                        });
                        // Set hidden input value to the dropped answer id
                        var blankId = $zone.data('blankId');
                        var answerId = $(evt.item).data('id');
                        $('#drag_' + self.$el.data('questionId') + '_' + blankId).val(answerId);
                    },
                    onRemove: function (evt) {
                        // Reset hidden input when item is removed
                        var $zone = $(evt.from);
                        var blankId = $zone.data('blankId');
                        $('#drag_' + self.$el.data('questionId') + '_' + blankId).val('');
                    }
                });
            });
        }
    });
    
    // Timer functionality for timed quizzes
    publicWidget.registry.QuizTimer = publicWidget.Widget.extend({
        selector: '.quiz-timer',
        
        start: function () {
            var self = this;
            this._super.apply(this, arguments);
            
            var timeLimit = parseInt(this.$el.data('timeLimit'));
            if (timeLimit) {
                // Check if there's a saved time in sessionStorage
                var quizId = window.location.pathname.split('/')[2];
                var sessionId = window.location.pathname.split('/')[4];
                var storageKey = 'quiz_timer_' + quizId + '_' + sessionId;
                var savedTime = sessionStorage.getItem(storageKey);
                
                var remainingTime;
                if (savedTime) {
                    remainingTime = parseInt(savedTime);
                } else {
                    remainingTime = timeLimit;
                    sessionStorage.setItem(storageKey, remainingTime);
                }
                
                this.$el.html(this._formatTime(remainingTime));
                
                // Start the countdown
                this.timerId = setInterval(function () {
                    remainingTime -= 1;
                    sessionStorage.setItem(storageKey, remainingTime);
                    
                    self.$el.html(self._formatTime(remainingTime));
                    
                    if (remainingTime <= 0) {
                        clearInterval(self.timerId);
                        self._onTimerExpired();
                    }
                }, 1000);
            }
        },
        
        _formatTime: function (seconds) {
            var minutes = Math.floor(seconds / 60);
            var secs = seconds % 60;
            return minutes.toString().padStart(2, '0') + ':' + secs.toString().padStart(2, '0');
        },
        
        _onTimerExpired: function () {
            // Auto-submit the form when timer expires
            var form = this.$el.closest('form');
            if (form.length) {
                alert('Time is up! Your answers will be submitted automatically.');
                form.submit();
            } else {
                alert('Time is up!');
                window.location.href = '/quiz/' + window.location.pathname.split('/')[2];
            }
        },
        
        destroy: function () {
            if (this.timerId) {
                clearInterval(this.timerId);
            }
            this._super.apply(this, arguments);
        }
    });
    
    // Fill in the blanks processor - replaces [blank] tokens with input fields
    publicWidget.registry.FillBlanksProcessor = publicWidget.Widget.extend({
        selector: '.fill-blank-processor',
        
        start: function () {
            this._super.apply(this, arguments);
            var self = this;
            var questionId = this.$el.data('questionId');
            var content = this.$el.html();
            
            // Replace [blank] tags with actual input fields
            var blanks = this.$el.data('blanks');
            if (blanks && blanks.length) {
                $.each(blanks, function (index, blank) {
                    var inputHtml = `<input type="text" 
                               id="blank_${questionId}_${blank.id}" 
                               name="blank_${questionId}_${blank.id}" 
                               class="form-control d-inline-block mx-2" 
                               style="width:150px" 
                               required="required"/>`;
                               
                    content = content.replace('[blank]', inputHtml);
                });
                
                this.$el.html(content);
            }
        }
    });

    // Add functionality to enable portal page for viewing quiz sessions
    publicWidget.registry.PortalQuizzes = publicWidget.Widget.extend({
        selector: '.o_portal_my_quizzes',
        
        start: function () {
            this._super.apply(this, arguments);
        }
    });

    return {
        QuizDragDrop: publicWidget.registry.QuizDragDrop,
        QuizTimer: publicWidget.registry.QuizTimer,
        FillBlanksProcessor: publicWidget.registry.FillBlanksProcessor,
        PortalQuizzes: publicWidget.registry.PortalQuizzes,
    };
});
