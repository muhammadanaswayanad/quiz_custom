(function() {
    "use strict";

    // Wait for DOM to be fully loaded before initializing
    document.addEventListener('DOMContentLoaded', function() {
        initializeSequences();
    });

    function initializeSequences() {
        // Fix for down buttons
        var moveDownButtons = document.querySelectorAll('.move-down');
        for (var i = 0; i < moveDownButtons.length; i++) {
            moveDownButtons[i].addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Get the sequence item containing this button
                var item = this.closest('.sequence-item');
                var next = item.nextElementSibling;
                
                if (next && next.classList.contains('sequence-item')) {
                    // Instead of using insertBefore with next.nextElementSibling
                    // We just swap the nodes directly
                    swapElements(item, next);
                    updateSequence(item.closest('.sequence-container'));
                }
            });
        }

        // Handle up buttons
        var moveUpButtons = document.querySelectorAll('.move-up');
        for (var i = 0; i < moveUpButtons.length; i++) {
            moveUpButtons[i].addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                var item = this.closest('.sequence-item');
                var prev = item.previousElementSibling;
                
                if (prev && prev.classList.contains('sequence-item')) {
                    swapElements(prev, item);
                    updateSequence(item.closest('.sequence-container'));
                }
            });
        }

        // Handle randomize button
        var randomizeButtons = document.querySelectorAll('.reset-sequence');
        for (var i = 0; i < randomizeButtons.length; i++) {
            randomizeButtons[i].addEventListener('click', function(e) {
                e.preventDefault();
                
                var container = this.closest('.sequence-container');
                randomizeItems(container);
                updateSequence(container);
            });
        }

        // Initialize sequence containers
        var containers = document.querySelectorAll('.sequence-container');
        for (var i = 0; i < containers.length; i++) {
            randomizeItems(containers[i]);
            updateSequence(containers[i]);
        }
    }

    // Helper function to swap two DOM elements
    function swapElements(el1, el2) {
        var parent = el1.parentNode;
        var nextSibling = el1.nextSibling === el2 ? el1 : el1.nextSibling;
        
        // Move el2 before el1
        el2.parentNode.insertBefore(el1, el2.nextSibling);
        
        // Move el1 to where el2 was
        parent.insertBefore(el2, nextSibling);
    }

    // Randomize the order of sequence items
    function randomizeItems(container) {
        if (!container) return;
        
        var list = container.querySelector('.sequence-list');
        if (!list) return;
        
        var items = Array.from(list.querySelectorAll('.sequence-item'));
        if (items.length < 2) return;

        // Fisher-Yates shuffle
        for (var i = items.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            if (j !== i) {
                list.insertBefore(items[j], items[i]);
            }
        }
    }

    // Update sequence numbers and data
    function updateSequence(container) {
        if (!container) return;
        
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
        for (var i = 0; i < items.length; i++) {
            var stepId = items[i].getAttribute('data-step-id');
            if (stepId) {
                data.push({
                    "step_id": parseInt(stepId, 10),
                    "position": i + 1
                });
            }
        }
        
        var input = container.querySelector('input[name="sequence_data"]');
        if (input) {
            input.value = JSON.stringify(data);
        }
    }
})();
