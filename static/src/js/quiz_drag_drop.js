odoo.define('quiz_engine_pro.drag_drop', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.QuizDragDrop = publicWidget.Widget.extend({
        selector: '.quiz-drag-drop',
        events: {
            'dragstart .draggable-token': '_onDragStart',
            'dragover .drop-zone': '_onDragOver',
            'dragleave .drop-zone': '_onDragLeave',
            'drop .drop-zone': '_onDrop',
            'click .reset-tokens': '_resetTokens'
        },

        start: function () {
            // Make tokens draggable
            this.$('.draggable-token').attr('draggable', 'true');
            
            // Store original positions
            this.$('.draggable-token').each(function() {
                $(this).data('originalParent', $(this).parent());
            });
            
            return this._super.apply(this, arguments);
        },
        
        _updateFormData: function() {
            var data = [];
            this.$('.drop-zone').each(function() {
                var zoneId = $(this).data('zone-id');
                $(this).find('.draggable-token').each(function() {
                    data.push({
                        token_id: $(this).data('token-id'),
                        zone_id: zoneId
                    });
                });
            });
            
            this.$('input[name="drag_drop_data"]').val(JSON.stringify(data));
        },
        
        _resetTokens: function(ev) {
            if (ev) ev.preventDefault();
            
            var self = this;
            this.$('.draggable-token').each(function() {
                var originalParent = $(this).data('originalParent');
                $(this).detach().appendTo(originalParent);
            });
            this._updateFormData();
        },
        
        _onDragStart: function(ev) {
            this.currentDraggedElement = $(ev.currentTarget);
            ev.originalEvent.dataTransfer.setData('text/plain', $(ev.currentTarget).data('token-id'));
            ev.originalEvent.dataTransfer.effectAllowed = 'move';
            
            $(ev.currentTarget).addClass('dragging');
        },
        
        _onDragOver: function(ev) {
            ev.preventDefault();
            $(ev.currentTarget).addClass('drag-over');
        },
        
        _onDragLeave: function(ev) {
            $(ev.currentTarget).removeClass('drag-over');
        },
        
        _onDrop: function(ev) {
            ev.preventDefault();
            var $zone = $(ev.currentTarget);
            $zone.removeClass('drag-over');
            
            // Get dragged element
            var tokenId = ev.originalEvent.dataTransfer.getData('text/plain');
            var $token = this.$('.draggable-token[data-token-id="' + tokenId + '"]');
            
            if ($token.length) {
                // Move token to drop zone
                $token.detach().appendTo($zone);
                $token.removeClass('dragging');
                
                // Update form data
                this._updateFormData();
            }
        }
    });

    return publicWidget.registry.QuizDragDrop;
});
        _onDragLeave: function(ev) {
            $(ev.currentTarget).removeClass('drag-over');
        },
        
        /**
         * Handle drop
         */
        _onDrop: function(ev) {
            ev.preventDefault();
            var $zone = $(ev.currentTarget);
            $zone.removeClass('drag-over');
            
            // Get dragged element
            var tokenId = ev.originalEvent.dataTransfer.getData('text/plain');
            var $token = this.$('.draggable-token[data-token-id="' + tokenId + '"]');
            
            if ($token.length) {
                // Move token to drop zone
                $token.detach().appendTo($zone);
                $token.removeClass('dragging');
                
                // Update form data
                this._updateFormData();
            }
        }
    });

    return publicWidget.registry.QuizDragDrop;
});
            ev.originalEvent.dataTransfer.effectAllowed = 'move';
            
            // Add dragging class
            $(ev.currentTarget).addClass('dragging');
            
            // For Firefox
            ev.originalEvent.dataTransfer.setDragImage(ev.currentTarget, 0, 0);
        },
        
        /**
         * Handle drag over event - needed to allow dropping
         * 
         * @private
         * @param {Event} ev Event
         */
        _onDragOver: function(ev) {
            ev.preventDefault();
            $(ev.currentTarget).addClass('drag-over');
            ev.originalEvent.dataTransfer.dropEffect = 'move';
        },
        
        /**
         * Handle drag leave event
         * 
         * @private
         * @param {Event} ev Event
         */
        _onDragLeave: function(ev) {
            $(ev.currentTarget).removeClass('drag-over');
        },
        
        /**
         * Handle drop event
         * 
         * @private
         * @param {Event} ev Event
         */
        _onDrop: function(ev) {
            ev.preventDefault();
            var $target = $(ev.currentTarget);
            $target.removeClass('drag-over');
            
            // Get the dragged element
            var tokenId = ev.originalEvent.dataTransfer.getData('text/plain');
            var $token = this.$('.draggable-token[data-token-id="' + tokenId + '"]');
            
            if ($token.length) {
                // Move the token to the drop zone
                $token.detach().appendTo($target);
                $token.removeClass('dragging');
                
                // Update form data
                this._updateFormData();
            }
        },
        
        // Touch event handlers for mobile devices
        _onTouchStart: function(ev) {
            var touch = ev.originalEvent.touches[0];
            var $token = $(ev.currentTarget);
            
            this.touchDragging = true;
            this.currentDraggedElement = $token;
            
            // Store initial position
            this.touchStartX = touch.clientX;
            this.touchStartY = touch.clientY;
            
            // Clone element for visual dragging
            this.$dragVisual = $token.clone().addClass('dragging-touch')
                .css({
                    position: 'fixed',
                    top: touch.clientY - ($token.height() / 2),
                    left: touch.clientX - ($token.width() / 2),
                    zIndex: 1000,
                    opacity: 0.8,
                    width: $token.width(),
                    pointerEvents: 'none'
                })
                .appendTo('body');
            
            $token.addClass('being-dragged');
        },
        
        _onTouchMove: function(ev) {
            if (!this.touchDragging) return;
            
            ev.preventDefault();
            var touch = ev.originalEvent.touches[0];
            
            // Move the visual element
            this.$dragVisual.css({
                top: touch.clientY - (this.$dragVisual.height() / 2),
                left: touch.clientX - (this.$dragVisual.width() / 2)
            });
            
            // Check if we're over a drop zone
            this.$('.drop-zone').removeClass('drag-over');
            var dropZone = this._getTouchDropZone(touch.clientX, touch.clientY);
            if (dropZone) {
                $(dropZone).addClass('drag-over');
            }
        },
        
        _onTouchEnd: function(ev) {
            if (!this.touchDragging) return;
            
            var touch = ev.originalEvent.changedTouches[0];
            var dropZone = this._getTouchDropZone(touch.clientX, touch.clientY);
            
            if (dropZone && this.currentDraggedElement) {
                // Move the actual token to the drop zone
                this.currentDraggedElement.detach().appendTo($(dropZone));
                
                // Update form data
                this._updateFormData();
            }
            
            // Clean up
            this.currentDraggedElement.removeClass('being-dragged');
            this.$dragVisual.remove();
            this.$('.drop-zone').removeClass('drag-over');
            this.touchDragging = false;
        },
        
        _getTouchDropZone: function(x, y) {
            var result = null;
            this.$('.drop-zone').each(function() {
                var offset = $(this).offset();
                if (x >= offset.left && x <= offset.left + $(this).width() &&
                    y >= offset.top && y <= offset.top + $(this).height()) {
                    result = this;
                    return false; // Break the loop
                }
            });
            return result;
        }
    });

    return publicWidget.registry.QuizDragDrop;
});
