odoo.define('quiz_engine_pro.drag_order', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    
    // Check if Sortable library is available (include it in assets if needed)
    var Sortable = window.Sortable || false;

    publicWidget.registry.QuizDragOrder = publicWidget.Widget.extend({
        selector: '.drag-order-question',
        events: {},

        /**
         * @override
         */
        start: function () {
            var self = this;
            this.sequenceList = this.el.querySelector('#sequenceList');
            this.hiddenInput = this.el.querySelector('input[name="sequence_order_data"]');
            
            if (!this.sequenceList || !this.hiddenInput) {
                console.error('Required elements not found for drag order question');
                return this._super.apply(this, arguments);
            }

            // Initialize using Sortable.js if available
            if (Sortable) {
                this.sortable = new Sortable(this.sequenceList, {
                    animation: 150,
                    ghostClass: 'sortable-ghost',
                    dragClass: 'dragging',
                    handle: '.drag-handle',
                    onEnd: function () {
                        self._updateOrderData();
                    }
                });
            } else {
                // Fallback to HTML5 Drag and Drop
                this._initHtml5DragDrop();
            }

            // Initialize the order data based on initial state
            this._updateOrderData();
            
            return this._super.apply(this, arguments);
        },
        
        /**
         * Initialize HTML5 Drag and Drop as fallback
         * @private
         */
        _initHtml5DragDrop: function () {
            var self = this;
            var items = this.sequenceList.querySelectorAll('.sequence-item');
            
            // Setup drag and drop on each item
            items.forEach(function (item) {
                item.addEventListener('dragstart', function (e) {
                    e.dataTransfer.effectAllowed = 'move';
                    e.dataTransfer.setData('text/plain', item.dataset.itemId);
                    item.classList.add('dragging');
                });
                
                item.addEventListener('dragend', function () {
                    item.classList.remove('dragging');
                });
                
                item.addEventListener('dragover', function (e) {
                    e.preventDefault();
                    return false;
                });
                
                item.addEventListener('dragenter', function () {
                    this.classList.add('sortable-ghost');
                });
                
                item.addEventListener('dragleave', function () {
                    this.classList.remove('sortable-ghost');
                });
                
                item.addEventListener('drop', function (e) {
                    e.stopPropagation();
                    e.preventDefault();
                    
                    var draggedItemId = e.dataTransfer.getData('text/plain');
                    var draggedItem = document.querySelector('.sequence-item[data-item-id="' + draggedItemId + '"]');
                    
                    if (draggedItem !== this) {
                        // Get the list and the positions
                        var list = this.parentNode;
                        var items = list.querySelectorAll('.sequence-item');
                        var draggedIndex = Array.from(items).indexOf(draggedItem);
                        var thisIndex = Array.from(items).indexOf(this);
                        
                        // Insert the dragged item
                        if (draggedIndex < thisIndex) {
                            list.insertBefore(draggedItem, this.nextSibling);
                        } else {
                            list.insertBefore(draggedItem, this);
                        }
                        
                        // Update the order data
                        self._updateOrderData();
                    }
                    
                    this.classList.remove('sortable-ghost');
                    return false;
                });
            });
        },
        
        /**
         * Update the hidden input with current order data
         * @private
         */
        _updateOrderData: function () {
            var items = this.sequenceList.querySelectorAll('.sequence-item');
            var order = Array.from(items).map(function (item) {
                return item.dataset.itemId;
            });
            
            this.hiddenInput.value = JSON.stringify(order);
        }
    });

    /**
     * Global initialization function for drag order questions
     * This is called from the inline script in the template
     */
    window.initDragOrder = function () {
        $('.drag-order-question').each(function () {
            var widget = new publicWidget.registry.QuizDragOrder();
            widget.attachTo($(this));
        });
    };

    return publicWidget.registry.QuizDragOrder;
});
