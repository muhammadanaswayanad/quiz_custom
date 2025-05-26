odoo.define('quiz_custom.frontend', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    
    // Initialize drag and drop functionality using Sortable.js
    publicWidget.registry.QuizDragDrop = publicWidget.Widget.extend({
        selector: '.drag-container',
        
        start: function () {
            var self = this;
            this._super.apply(this, arguments);
            
            if (!window.Sortable) {
                // Load Sortable.js from CDN if not available
                $.getScript('https://cdn.jsdelivr.net/npm/sortablejs@1.14.0/Sortable.min.js', function () {
                    self._initDragDrop();
                });
            } else {
                this._initDragDrop();
            }
        },
        
        _initDragDrop: function () {
            var self = this;
            var questionId = this.$el.data('questionId');
            
            // Initialize draggable items
            var dragItems = this.$el.find('.drag-items')[0];
            if (dragItems) {
                new Sortable(dragItems, {
                    group: {
                        name: 'quiz-items-' + questionId,
                        pull: 'clone',
                        put: false
                    },
                    sort: false,
                    animation: 150
                });
            }
            
            // Initialize drop zones
            var dropZones = this.$el.find('.drop-zone');
            dropZones.each(function () {
                var dropZone = this;
                var position = $(dropZone).data('position');
                
                new Sortable(dropZone, {
                    group: {
                        name: 'quiz-items-' + questionId,
                        pull: false
                    },
                    animation: 150,
                    onAdd: function (evt) {
                        // Keep only one item per drop zone
                        if ($(evt.to).children('.drag-item').length > 1) {
                            var previousItem = $(evt.to).children('.drag-item').not(evt.item);
                            dragItems.appendChild(previousItem[0]);
                        }
                        
                        // Update the hidden input with the position value
                        var itemId = $(evt.item).data('id');
                        $('#drag_' + questionId + '_' + itemId).val(position);
                    },
                    onRemove: function (evt) {
                        // Reset position value when item is removed
                        var itemId = $(evt.item).data('id');
                        $('#drag_' + questionId + '_' + itemId).val(0);
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
