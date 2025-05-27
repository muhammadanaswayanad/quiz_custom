odoo.define('quiz_engine_pro.drag_into_text', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.QuizDragIntoText = publicWidget.Widget.extend({
        selector: '.quiz-container',
        events: {
            'click #next-btn': '_onNextQuestion',
            'click #prev-btn': '_onPrevQuestion',
            'click #submit-btn': '_onSubmitQuiz',
        },

        start: function() {
            this._super.apply(this, arguments);
            this.currentQuestionIndex = 0;
            this.totalQuestions = parseInt(window.totalQuestions || 0);
            this.sessionToken = window.sessionToken;
            this.answers = {};
            this._initializeDragAndDrop();
            this._updateNavigation();
            return Promise.resolve();
        },

        _initializeDragAndDrop: function () {
            var self = this;
            
            // Process drag-into-text questions
            this.$('.drag-into-text').each(function () {
                var $container = $(this);
                self._setupDragIntoText($container);
            });
        },

        _setupDragIntoText: function ($container) {
            var self = this;
            
            // Convert {{1}}, {{2}} placeholders to drop zones
            var $questionText = $container.find('.question-with-blanks');
            var html = $questionText.html();
            html = html.replace(/\{\{(\d+)\}\}/g, function(match, blankNumber) {
                return '<span class="dropzone" data-blank="' + blankNumber + '" data-id="' + blankNumber + '">Drop here</span>';
            });
            $questionText.html(html);

            // Make tokens draggable
            $container.find('.token').each(function () {
                var $token = $(this);
                $token.attr('draggable', true);
                
                $token.on('dragstart', function (e) {
                    e.originalEvent.dataTransfer.setData('text/plain', $token.data('value'));
                    $token.addClass('dragging');
                });
                
                $token.on('dragend', function (e) {
                    $token.removeClass('dragging');
                });
            });

            // Setup drop zones
            $container.find('.dropzone').each(function () {
                var $dropzone = $(this);
                
                $dropzone.on('dragover', function (e) {
                    e.preventDefault();
                    $dropzone.addClass('drag-over');
                });
                
                $dropzone.on('dragleave', function (e) {
                    $dropzone.removeClass('drag-over');
                });
                
                $dropzone.on('drop', function (e) {
                    e.preventDefault();
                    $dropzone.removeClass('drag-over');
                    
                    var tokenValue = e.originalEvent.dataTransfer.getData('text/plain');
                    var blankId = $dropzone.data('blank');
                    
                    // Update dropzone content
                    $dropzone.text(tokenValue);
                    $dropzone.addClass('filled');
                    
                    // Hide the used token
                    $container.find('.token[data-value="' + tokenValue + '"]').hide();
                    
                    // Store answer
                    var questionId = $container.closest('.question-container').data('question-id');
                    if (!self.answers[questionId]) {
                        self.answers[questionId] = { type: 'drag_into_text', placements: {} };
                    }
                    self.answers[questionId].placements[blankId] = tokenValue;
                    
                    // Allow clearing by clicking
                    $dropzone.off('click').on('click', function () {
                        self._clearDropzone($dropzone, $container);
                    });
                });
            });
        },

        _clearDropzone: function ($dropzone, $container) {
            var tokenValue = $dropzone.text();
            var blankId = $dropzone.data('blank');
            
            // Clear dropzone
            $dropzone.text('Drop here');
            $dropzone.removeClass('filled');
            
            // Show token again
            $container.find('.token[data-value="' + tokenValue + '"]').show();
            
            // Remove from answers
            var questionId = $container.closest('.question-container').data('question-id');
            if (this.answers[questionId] && this.answers[questionId].placements) {
                delete this.answers[questionId].placements[blankId];
            }
        },

        _onNextQuestion: function (e) {
            e.preventDefault();
            this._saveCurrentAnswer();
            
            if (this.currentQuestionIndex < this.totalQuestions - 1) {
                this.currentQuestionIndex++;
                this._showQuestion(this.currentQuestionIndex);
                this._updateNavigation();
            }
        },

        _onPrevQuestion: function (e) {
            e.preventDefault();
            this._saveCurrentAnswer();
            
            if (this.currentQuestionIndex > 0) {
                this.currentQuestionIndex--;
                this._showQuestion(this.currentQuestionIndex);
                this._updateNavigation();
            }
        },

        _showQuestion: function (index) {
            this.$('.question-container').addClass('d-none');
            this.$('.question-container').eq(index).removeClass('d-none');
            this.$('#current-question').text(index + 1);
        },

        _updateNavigation: function () {
            this.$('#prev-btn').prop('disabled', this.currentQuestionIndex === 0);
            
            if (this.currentQuestionIndex === this.totalQuestions - 1) {
                this.$('#next-btn').addClass('d-none');
                this.$('#submit-btn').removeClass('d-none');
            } else {
                this.$('#next-btn').removeClass('d-none');
                this.$('#submit-btn').addClass('d-none');
            }
        },

        _saveCurrentAnswer: function () {
            var $currentQuestion = this.$('.question-container').eq(this.currentQuestionIndex);
            var questionId = $currentQuestion.data('question-id');
            var questionType = $currentQuestion.find('[class*="mcq-"], [class*="drag-"]').attr('class');
            
            if ($currentQuestion.find('.mcq-options').length > 0) {
                this._saveMCQAnswer($currentQuestion, questionId);
            }
            // Drag into text answers are saved in real-time
        },

        _saveMCQAnswer: function ($question, questionId) {
            var answerData = {};
            
            if ($question.find('input[type="radio"]').length > 0) {
                // Single choice
                var selectedChoice = $question.find('input[type="radio"]:checked').val();
                if (selectedChoice) {
                    answerData = { type: 'mcq_single', choice_id: parseInt(selectedChoice) };
                }
            } else if ($question.find('input[type="checkbox"]').length > 0) {
                // Multiple choice
                var selectedChoices = [];
                $question.find('input[type="checkbox"]:checked').each(function () {
                    selectedChoices.push(parseInt($(this).val()));
                });
                answerData = { type: 'mcq_multi', choice_ids: selectedChoices };
            }
            
            if (Object.keys(answerData).length > 0) {
                this.answers[questionId] = answerData;
            }
        },

        _onSubmitQuiz: function (e) {
            e.preventDefault();
            this._saveCurrentAnswer();
            
            // Submit all answers
            var self = this;
            var promises = [];
            
            Object.keys(this.answers).forEach(function (questionId) {
                var promise = ajax.jsonRpc('/quiz/session/' + self.sessionToken + '/answer', 'call', {
                    question_id: parseInt(questionId),
                    answer_data: self.answers[questionId]
                });
                promises.push(promise);
            });
            
            Promise.all(promises).then(function () {
                // Complete the quiz
                window.location.href = '/quiz/session/' + self.sessionToken + '/complete';
            }).catch(function (error) {
                console.error('Error submitting answers:', error);
                alert('Error submitting quiz. Please try again.');
            });
        },
    });

    return publicWidget.registry.QuizDragIntoText;
});
});
