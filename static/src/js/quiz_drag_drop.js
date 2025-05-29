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
            
            // Fix: Initialize token drag operations with native JavaScript as a fallback
            this._initializeNativeDragDrop();
            
            return this._super.apply(this, arguments);
        },
        
        _initializeNativeDragDrop: function() {
            var self = this;
            
            // Native JavaScript implementation as fallback
            var tokens = document.querySelectorAll('.draggable-token');
            var dropZones = document.querySelectorAll('.drop-zone');
            var tokensContainer = document.querySelector('.tokens-container');
            var resetButton = document.querySelector('.reset-tokens');
            
            if (!tokens.length || !dropZones.length) {
                return; // Exit if elements are not found
            }
            
            // Set up tokens
            tokens.forEach(function(token) {
                token.setAttribute('draggable', 'true');
                
                token.addEventListener('dragstart', function(e) {
                    e.dataTransfer.setData('text/plain', this.getAttribute('data-token-id'));
                    this.classList.add('dragging');
                });
            });
            
            // Set up drop zones
            dropZones.forEach(function(zone) {
                zone.addEventListener('dragover', function(e) {
                    e.preventDefault(); // Critical for drop to work
                    this.classList.add('drag-over');
                });
                
                zone.addEventListener('dragleave', function() {
                    this.classList.remove('drag-over');
                });
                
                zone.addEventListener('drop', function(e) {
                    e.preventDefault();
                    this.classList.remove('drag-over');
                    
                    var tokenId = e.dataTransfer.getData('text/plain');
                    var token = document.querySelector('.draggable-token[data-token-id="' + tokenId + '"]');
                    
                    if (token) {
                        this.appendChild(token);
                        token.classList.remove('dragging');
                        self._updateFormData();
                    }
                });
            });
            
            // Set up reset button
            if (resetButton && tokensContainer) {
                resetButton.addEventListener('click', function() {
                    tokens.forEach(function(token) {
                        tokensContainer.appendChild(token);
                    });
                    self._updateFormData();
                });
            }
        },
        
        _updateFormData: function() {
            var data = [];
            var dropZones = document.querySelectorAll('.drop-zone');
            
            dropZones.forEach(function(zone) {
                var zoneId = zone.getAttribute('data-zone-id');
                var zoneTokens = zone.querySelectorAll('.draggable-token');
                
                zoneTokens.forEach(function(token) {
                    data.push({
                        token_id: token.getAttribute('data-token-id'),
                        zone_id: zoneId
                    });
                });
            });
            
            var hiddenField = document.querySelector('input[name="drag_drop_data"]');
            if (hiddenField) {
                hiddenField.value = JSON.stringify(data);
            }
        },
        
        _resetTokens: function(ev) {
            if (ev) ev.preventDefault();
            
            // Use native DOM methods for consistent behavior
            var tokensContainer = document.querySelector('.tokens-container');
            var tokens = document.querySelectorAll('.draggable-token');
            
            if (tokensContainer) {
                tokens.forEach(function(token) {
                    tokensContainer.appendChild(token);
                });
            }
            
            this._updateFormData();
        },
        
        _onDragStart: function(ev) {
            ev.originalEvent.dataTransfer.setData('text/plain', ev.currentTarget.getAttribute('data-token-id'));
            ev.currentTarget.classList.add('dragging');
        },
        
        _onDragOver: function(ev) {
            ev.preventDefault(); // Critical for allowing drop
            ev.currentTarget.classList.add('drag-over');
        },
        
        _onDragLeave: function(ev) {
            ev.currentTarget.classList.remove('drag-over');
        },
        
        _onDrop: function(ev) {
            ev.preventDefault();
            var zone = ev.currentTarget;
            zone.classList.remove('drag-over');
            
            // Get dragged element using vanilla JS to avoid cross-origin issues
            var tokenId = ev.originalEvent.dataTransfer.getData('text/plain');
            var token = document.querySelector('.draggable-token[data-token-id="' + tokenId + '"]');
            
            if (token) {
                // Move token to drop zone
                zone.appendChild(token);
                token.classList.remove('dragging');
                
                // Update form data
                this._updateFormData();
            }
        }
    });

    return publicWidget.registry.QuizDragDrop;
});
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
