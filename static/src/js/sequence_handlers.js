(function() {
    "use strict";

    // Run when DOM is fully loaded
    document.addEventListener('DOMContentLoaded', initAndBindEvents);
    
    /**
     * Initialize handlers and bind events
     */
    function initAndBindEvents() {
        // Direct event binding to buttons
        var upButtons = document.querySelectorAll('.move-up');
        for (var i = 0; i < upButtons.length; i++) {
            upButtons[i].onclick = function() {
                var item = this.closest('.sequence-item');
                var prev = item.previousElementSibling;
                if (prev) {
                    item.parentNode.insertBefore(item, prev);
                    updatePositions(item.closest('.sequence-container'));
                }
                return false; // Prevent default and stop propagation
            };
        }

        var downButtons = document.querySelectorAll('.move-down');
        for (var i = 0; i < downButtons.length; i++) {
            downButtons[i].onclick = function() {
                var item = this.closest('.sequence-item');
                var next = item.nextElementSibling;
                if (next) {
                    next.parentNode.insertBefore(next, item);
                    updatePositions(item.closest('.sequence-container'));
                }
                return false; // Prevent default and stop propagation
            };
        }

        var resetButtons = document.querySelectorAll('.reset-sequence');
        for (var i = 0; i < resetButtons.length; i++) {
            resetButtons[i].onclick = function() {
                randomizeOrder(this.closest('.sequence-container'));
                return false; // Prevent default and stop propagation
            };
        }

        // Apply initial randomization to all sequence containers
        var containers = document.querySelectorAll('.sequence-container');
        for (var i = 0; i < containers.length; i++) {
            randomizeOrder(containers[i]);
        }
    }
    
    /**
     * Update sequence numbers and data after position changes
     */
    function updatePositions(container) {
        if (!container) return;
        
        // Update visible numbers
        var items = container.querySelectorAll('.sequence-item');
        for (var i = 0; i < items.length; i++) {
            var numEl = items[i].querySelector('.step-number');
            if (numEl) numEl.textContent = (i + 1);
        }
        
        // Update data input
        var data = [];
        for (var i = 0; i < items.length; i++) {
            var id = items[i].getAttribute('data-step-id');
            if (id) data.push({step_id: parseInt(id), position: i + 1});
        }
        
        var input = container.querySelector('input[name="sequence_data"]');
        if (input) input.value = JSON.stringify(data);
    }
    
    /**
     * Randomize order of sequence items
     */
    function randomizeOrder(container) {
        if (!container) return;
        
        var list = container.querySelector('.sequence-list');
        var items = Array.from(list.querySelectorAll('.sequence-item'));
        
        // Shuffle the items
        for (var i = items.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            list.appendChild(items[j]);
        }
        
        updatePositions(container);
    }
})();
    }
    
    function updateSequenceData(container) {
        var items = container.querySelectorAll('.sequence-item');
        var data = [];
        
        for (var i = 0; i < items.length; i++) {
            var stepId = items[i].dataset.stepId;
            if (stepId) {
                data.push({
                    step_id: parseInt(stepId, 10),
                    position: i + 1
                });
            }
        }
        
        var input = container.querySelector('input[name="sequence_data"]');
        if (input) {
            input.value = JSON.stringify(data);
        }
    }
})();
