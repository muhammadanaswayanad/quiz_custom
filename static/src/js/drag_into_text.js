odoo.define('quiz_custom.drag_into_text', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    
    publicWidget.registry.QuizDragIntoText = publicWidget.Widget.extend({
        selector: '.quiz-drag-into-text-container',
        events: {
            'dragstart .draggable': '_onDragStart',
            'dragover .dropzone': '_onDragOver',
            'dragleave .dropzone': '_onDragLeave',
            'drop .dropzone': '_onDrop',
            'touchstart .draggable': '_onTouchStart',
            'touchmove': '_onTouchMove',
            'touchend': '_onTouchEnd'
        },
        
        start: function () {
            this.dragElement = null;
            this.touchActive = false;
            this.dropzoneTargets = this.el.querySelectorAll('.dropzone');
            this.draggableItems = this.el.querySelectorAll('.draggable');
            
            // Make elements draggable
            this.draggableItems.forEach(item => {
                item.setAttribute('draggable', true);
            });
            
            return this._super.apply(this, arguments);
        },
        
        /**
         * When dragging starts, store the current element and add a visual cue
         */
        _onDragStart: function (ev) {
            ev.originalEvent.dataTransfer.setData('text', ev.currentTarget.dataset.value);
            ev.originalEvent.dataTransfer.effectAllowed = 'move';
            ev.currentTarget.classList.add('being-dragged');
            this.dragElement = ev.currentTarget;
        },
        
        /**
         * When dragging over a dropzone, allow the drop
         */
        _onDragOver: function (ev) {
            ev.preventDefault();
            ev.originalEvent.dataTransfer.dropEffect = 'move';
            ev.currentTarget.classList.add('dragover');
        },
        
        /**
         * When leaving a dropzone, remove visual cue
         */
        _onDragLeave: function (ev) {
            ev.currentTarget.classList.remove('dragover');
        },
        
        /**
         * When dropping onto a dropzone, handle the transfer
         */
        _onDrop: function (ev) {
            ev.preventDefault();
            const dropzone = ev.currentTarget;
            dropzone.classList.remove('dragover');
            
            const tokenValue = ev.originalEvent.dataTransfer.getData('text');
            const targetNumber = dropzone.dataset.target;
            
            // If dropzone already has a token, return that token to available tokens
            if (dropzone.querySelector('.token-content')) {
                this._returnTokenToAvailable(dropzone.querySelector('.token-content').textContent);
            }
            
            // Update the dropzone with the new token
            dropzone.innerHTML = `<span class="token-content">${tokenValue}</span>`;
            
            // Remove the original draggable if it came from the token bank
            if (this.dragElement && this.dragElement.parentNode.classList.contains('token-bank')) {
                this.dragElement.classList.add('used');
                this.dragElement.setAttribute('draggable', false);
            }
            
            // Update the hidden input field with the current state
            this._updateHiddenField();
            
            this.dragElement.classList.remove('being-dragged');
            this.dragElement = null;
        },
        
        /**
         * Return a token to the available tokens area
         */
        _returnTokenToAvailable: function (tokenValue) {
            const tokenBank = this.el.querySelector('.token-bank');
            const tokens = tokenBank.querySelectorAll('.draggable');
            
            for (let i = 0; i < tokens.length; i++) {
                if (tokens[i].dataset.value === tokenValue) {
                    tokens[i].classList.remove('used');
                    tokens[i].setAttribute('draggable', true);
                    break;
                }
            }
        },
        
        /**
         * Update the hidden field with the current state of all dropzones
         */
        _updateHiddenField: function () {
            const result = {};
            const dropzones = this.el.querySelectorAll('.dropzone');
            
            dropzones.forEach(function (zone) {
                const content = zone.querySelector('.token-content');
                if (content) {
                    result[zone.dataset.target] = content.textContent;
                } else {
                    result[zone.dataset.target] = "";
                }
            });
            
            // Update the hidden field with JSON data
            const hiddenField = this.el.querySelector('.drag-into-text-result');
            hiddenField.value = JSON.stringify(result);
        },
        
        // Touch event handlers for mobile support
        _onTouchStart: function (ev) {
            const touch = ev.originalEvent.touches[0];
            const draggable = ev.currentTarget;
            
            this.touchActive = true;
            this.dragElement = draggable;
            draggable.classList.add('being-dragged');
            
            // Store initial touch position
            this.touchOffsetX = touch.clientX - draggable.getBoundingClientRect().left;
            this.touchOffsetY = touch.clientY - draggable.getBoundingClientRect().top;
            
            // Create a clone for dragging visual
            this.touchDragImage = draggable.cloneNode(true);
            this.touchDragImage.classList.add('touch-drag-image');
            document.body.appendChild(this.touchDragImage);
            
            this._positionTouchDragImage(touch.clientX, touch.clientY);
        },
        
        _onTouchMove: function (ev) {
            if (!this.touchActive || !this.dragElement) return;
            
            ev.preventDefault(); // Prevent scrolling while dragging
            const touch = ev.originalEvent.touches[0];
            
            // Move the drag image
            this._positionTouchDragImage(touch.clientX, touch.clientY);
            
            // Check if over a dropzone
            const dropzone = this._getTouchDropzone(touch.clientX, touch.clientY);
            
            // Update visual cues
            this.dropzoneTargets.forEach(zone => {
                zone.classList.remove('dragover');
            });
            
            if (dropzone) {
                dropzone.classList.add('dragover');
            }
        },
        
        _onTouchEnd: function (ev) {
            if (!this.touchActive || !this.dragElement) return;
            
            const touch = ev.originalEvent.changedTouches[0];
            const dropzone = this._getTouchDropzone(touch.clientX, touch.clientY);
            
            if (dropzone) {
                // Handle the drop
                dropzone.classList.remove('dragover');
                
                const tokenValue = this.dragElement.dataset.value;
                const targetNumber = dropzone.dataset.target;
                
                // If dropzone already has a token, return that token
                if (dropzone.querySelector('.token-content')) {
                    this._returnTokenToAvailable(dropzone.querySelector('.token-content').textContent);
                }
                
                // Update the dropzone
                dropzone.innerHTML = `<span class="token-content">${tokenValue}</span>`;
                
                // Mark the original token as used
                if (this.dragElement.parentNode.classList.contains('token-bank')) {
                    this.dragElement.classList.add('used');
                    this.dragElement.setAttribute('draggable', false);
                }
                
                this._updateHiddenField();
            }
            
            // Clean up
            this.dragElement.classList.remove('being-dragged');
            document.body.removeChild(this.touchDragImage);
            this.touchDragImage = null;
            this.dragElement = null;
            this.touchActive = false;
        },
        
        _positionTouchDragImage: function (x, y) {
            if (!this.touchDragImage) return;
            this.touchDragImage.style.left = (x - this.touchOffsetX) + 'px';
            this.touchDragImage.style.top = (y - this.touchOffsetY) + 'px';
        },
        
        _getTouchDropzone: function (x, y) {
            let result = null;
            this.dropzoneTargets.forEach(zone => {
                const rect = zone.getBoundingClientRect();
                if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
                    result = zone;
                }
            });
            return result;
        }
    });
    
    return publicWidget.registry.QuizDragIntoText;
});
