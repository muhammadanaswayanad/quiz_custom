// Basic sequence buttons functionality
(function() {
    "use strict";
    
    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initSequenceButtons();
    });
    
    function initSequenceButtons() {
        // Find all up buttons and attach handlers
        var upButtons = document.querySelectorAll('.move-up');
        for(var i = 0; i < upButtons.length; i++) {
            upButtons[i].addEventListener('click', handleMoveUp);
        }
        
        // Find all down buttons and attach handlers
        var downButtons = document.querySelectorAll('.move-down');
        for(var i = 0; i < downButtons.length; i++) {
            downButtons[i].addEventListener('click', handleMoveDown);
        }
        
        // Find all reset buttons and attach handlers
        var resetButtons = document.querySelectorAll('.reset-sequence');
        for(var i = 0; i < resetButtons.length; i++) {
            resetButtons[i].addEventListener('click', handleReset);
        }
    }
    
    function handleMoveUp(event) {
        event.preventDefault();
        event.stopPropagation();
        
        var item = this.closest('.sequence-item');
        var prev = item.previousElementSibling;
        
        if(prev && prev.classList.contains('sequence-item')) {
            var parent = item.parentNode;
            parent.insertBefore(item, prev);
            updateSequence(parent);
        }
    }
    
    function handleMoveDown(event) {
        event.preventDefault();
        event.stopPropagation();
        
        var item = this.closest('.sequence-item');
        var next = item.nextElementSibling;
        
        if(next && next.classList.contains('sequence-item')) {
            var parent = item.parentNode;
            parent.insertBefore(next, item);
            updateSequence(parent);
        }
    }
    
    function handleReset(event) {
        event.preventDefault();
        
        var container = this.closest('.sequence-container');
        var list = container.querySelector('.sequence-list');
        var items = Array.from(list.querySelectorAll('.sequence-item'));
        
        // Shuffle items
        for(var i = items.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            list.appendChild(items[j]);
        }
        
        updateSequence(list);
    }
    
    function updateSequence(container) {
        // Update step numbers
        var items = container.querySelectorAll('.sequence-item');
        for(var i = 0; i < items.length; i++) {
            var numElement = items[i].querySelector('.step-number');
            if(numElement) {
                numElement.textContent = (i + 1);
            }
        }
        
        // Update hidden input
        var data = [];
        for(var i = 0; i < items.length; i++) {
            var stepId = items[i].getAttribute('data-step-id');
            if(stepId) {
                data.push({
                    step_id: parseInt(stepId, 10),
                    position: i + 1
                });
            }
        }
        
        var form = container.closest('form');
        if(form) {
            var input = form.querySelector('input[name="sequence_data"]');
            if(input) {
                input.value = JSON.stringify(data);
            }
        }
    }
})();
