// Simple vanilla JS implementation for sequence item buttons
document.addEventListener('DOMContentLoaded', function() {
    // Find all sequence container elements
    var containers = document.querySelectorAll('.sequence-container');
    if (!containers.length) return;
    
    // Process each container
    containers.forEach(function(container) {
        // Setup buttons for this container
        setupMoveButtons(container);
        setupResetButton(container);
    });
    
    function setupMoveButtons(container) {
        // Setup move up buttons
        var moveUpButtons = container.querySelectorAll('.move-up');
        moveUpButtons.forEach(function(btn) {
            btn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                var item = this.closest('.sequence-item');
                var prev = item.previousElementSibling;
                
                if (prev && prev.classList.contains('sequence-item')) {
                    item.parentNode.insertBefore(item, prev);
                    updateSequenceOrder(container);
                }
            };
        });
        
        // Setup move down buttons
        var moveDownButtons = container.querySelectorAll('.move-down');
        moveDownButtons.forEach(function(btn) {
            btn.onclick = function(e) {
                e.preventDefault(); 
                e.stopPropagation();
                
                var item = this.closest('.sequence-item');
                var next = item.nextElementSibling;
                
                if (next && next.classList.contains('sequence-item')) {
                    item.parentNode.insertBefore(next, item);
                    updateSequenceOrder(container);
                }
            };
        });
    }
    
    function setupResetButton(container) {
        var resetButton = container.querySelector('.reset-sequence');
        if (resetButton) {
            resetButton.onclick = function(e) {
                e.preventDefault();
                randomizeItems(container);
                updateSequenceOrder(container);
            };
        }
    }
    
    function randomizeItems(container) {
        var list = container.querySelector('.sequence-list');
        var items = Array.from(list.querySelectorAll('.sequence-item'));
        
        // Fisher-Yates shuffle
        for (var i = items.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            list.appendChild(items[j]);
        }
    }
    
    function updateSequenceOrder(container) {
        // Update step numbers
        var items = container.querySelectorAll('.sequence-item');
        for (var i = 0; i < items.length; i++) {
            var numEl = items[i].querySelector('.step-number');
            if (numEl) {
                numEl.textContent = (i + 1);
            }
        }
        
        // Update hidden input with JSON data
        var data = [];
        items.forEach(function(item, index) {
            var stepId = item.getAttribute('data-step-id');
            if (stepId) {
                data.push({
                    step_id: parseInt(stepId),
                    position: index + 1
                });
            }
        });
        
        var inputEl = container.querySelector('input[name="sequence_data"]');
        if (inputEl) {
            inputEl.value = JSON.stringify(data);
        }
    }
});
