(function() {
    "use strict";
    
    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        setupEventListeners();
        initializeSequences();
    });
    
    function setupEventListeners() {
        // Using event delegation on document body
        document.body.addEventListener('click', function(event) {
            var target = event.target;
            
            // Move item up
            if (target.matches('.move-up')) {
                var item = target.closest('.sequence-item');
                var prev = item.previousElementSibling;
                if (prev && prev.classList.contains('sequence-item')) {
                    item.parentNode.insertBefore(item, prev);
                    updateSequence(item.closest('.sequence-container'));
                }
            }
            
            // Move item down
            else if (target.matches('.move-down')) {
                var item = target.closest('.sequence-item');
                var next = item.nextElementSibling;
                if (next && next.classList.contains('sequence-item')) {
                    next.parentNode.insertBefore(next, item);
                    updateSequence(item.closest('.sequence-container'));
                }
            }
            
            // Randomize order
            else if (target.matches('.reset-sequence')) {
                var container = target.closest('.sequence-container');
                randomizeItems(container);
            }
        });
    }
    
    function initializeSequences() {
        // Find all sequence containers and randomize
        var containers = document.querySelectorAll('.sequence-container');
        for (var i = 0; i < containers.length; i++) {
            randomizeItems(containers[i]);
        }
        
        // Hide any "not implemented" messages
        var messages = document.querySelectorAll('.alert-warning');
        for (var i = 0; i < messages.length; i++) {
            if (messages[i].textContent.indexOf('not yet implemented') >= 0) {
                messages[i].style.display = 'none';
            }
        }
    }
    
    function randomizeItems(container) {
        if (!container) return;
        
        var list = container.querySelector('.sequence-list');
        if (!list) return;
        
        var items = Array.from(list.querySelectorAll('.sequence-item'));
        if (items.length < 2) return;
        
        // Shuffle items
        for (var i = items.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            list.appendChild(items[j]);
        }
        
        updateSequence(container);
    }
    
    function updateSequence(container) {
        if (!container) return;
        
        // Update sequence numbers
        var items = container.querySelectorAll('.sequence-item');
        for (var i = 0; i < items.length; i++) {
            var numEl = items[i].querySelector('.step-number');
            if (numEl) {
                numEl.textContent = (i + 1);
            }
        }
        
        // Update hidden input value
        var data = [];
        for (var i = 0; i < items.length; i++) {
            var stepId = items[i].getAttribute('data-step-id');
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
