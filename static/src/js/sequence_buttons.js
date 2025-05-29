// Simple inline JavaScript for sequence operations
(function() {
    // Add event handler on page load
    document.addEventListener('DOMContentLoaded', function() {
        setupSequenceButtons();
        
        // Add event delegation on document for dynamically added buttons
        document.addEventListener('click', function(event) {
            var target = event.target;
            
            // Handle up button click
            if (target.classList.contains('move-up') || target.closest('.move-up')) {
                event.preventDefault();
                var button = target.classList.contains('move-up') ? target : target.closest('.move-up');
                var item = button.closest('.sequence-item');
                moveItemUp(item);
            }
            
            // Handle down button click
            if (target.classList.contains('move-down') || target.closest('.move-down')) {
                event.preventDefault();
                var button = target.classList.contains('move-down') ? target : target.closest('.move-down');
                var item = button.closest('.sequence-item');
                moveItemDown(item);
            }
            
            // Handle randomize button
            if (target.classList.contains('reset-sequence') || target.closest('.reset-sequence')) {
                event.preventDefault();
                var button = target.classList.contains('reset-sequence') ? target : target.closest('.reset-sequence');
                var container = button.closest('.sequence-container');
                randomizeItems(container);
            }
        });
        
        // Initial setup
        var containers = document.querySelectorAll('.sequence-container');
        for (var i = 0; i < containers.length; i++) {
            randomizeItems(containers[i]);
        }
    });
    
    function setupSequenceButtons() {
        console.log("Setting up sequence buttons");
    }
    
    // Function to move an item up
    function moveItemUp(item) {
        var prev = item.previousElementSibling;
        if (prev && prev.classList.contains('sequence-item')) {
            var parent = item.parentNode;
            parent.insertBefore(item, prev);
            
            // Update order
            var container = item.closest('.sequence-container');
            updateNumbers(container);
            updateData(container);
            
            console.log("Moved item up");
        }
    }
    
    // Function to move an item down
    function moveItemDown(item) {
        var next = item.nextElementSibling;
        if (next && next.classList.contains('sequence-item')) {
            var parent = item.parentNode;
            if (next.nextElementSibling) {
                parent.insertBefore(item, next.nextElementSibling);
            } else {
                parent.appendChild(item);
            }
            
            // Update order
            var container = item.closest('.sequence-container');
            updateNumbers(container);
            updateData(container);
            
            console.log("Moved item down");
        }
    }
    
    // Function to randomize items
    function randomizeItems(container) {
        var list = container.querySelector('.sequence-list');
        if (!list) return;
        
        var items = Array.from(list.querySelectorAll('.sequence-item'));
        if (items.length < 2) return;
        
        // Shuffle
        for (var i = items.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            list.appendChild(items[j]);
        }
        
        updateNumbers(container);
        updateData(container);
        
        console.log("Randomized items");
    }
    
    // Function to update step numbers
    function updateNumbers(container) {
        var items = container.querySelectorAll('.sequence-item');
        for (var i = 0; i < items.length; i++) {
            var numElem = items[i].querySelector('.step-number');
            if (numElem) {
                numElem.textContent = (i + 1);
            }
        }
    }
    
    // Function to update hidden input data
    function updateData(container) {
        var items = container.querySelectorAll('.sequence-item');
        var data = [];
        
        for (var i = 0; i < items.length; i++) {
            var stepId = items[i].getAttribute('data-step-id');
            if (stepId) {
                data.push({
                    step_id: parseInt(stepId),
                    position: i + 1
                });
            }
        }
        
        var input = container.querySelector('input[name="sequence_data"]');
        if (input) {
            input.value = JSON.stringify(data);
            console.log("Updated data:", input.value);
        }
    }
})();
