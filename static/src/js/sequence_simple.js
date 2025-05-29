(function() {
    // Wait for DOM to be loaded
    document.addEventListener('DOMContentLoaded', function() {
        setupSequenceButtons();
        initializeSequences();
    });
    
    // Setup event handlers for sequence items
    function setupSequenceButtons() {
        // Move Up button handler
        document.body.addEventListener('click', function(e) {
            if (e.target.classList.contains('move-up')) {
                var item = e.target.closest('.sequence-item');
                var prev = item.previousElementSibling;
                if (prev && prev.classList.contains('sequence-item')) {
                    item.parentNode.insertBefore(item, prev);
                    updateSequence(item.closest('.sequence-container'));
                }
            }
        });
        
        // Move Down button handler
        document.body.addEventListener('click', function(e) {
            if (e.target.classList.contains('move-down')) {
                var item = e.target.closest('.sequence-item');
                var next = item.nextElementSibling;
                if (next && next.classList.contains('sequence-item')) {
                    item.parentNode.insertBefore(next, item);
                    updateSequence(item.closest('.sequence-container'));
                }
            }
        });
        
        // Randomize button handler
        document.body.addEventListener('click', function(e) {
            if (e.target.classList.contains('reset-sequence')) {
                var container = e.target.closest('.sequence-container');
                randomizeSequence(container);
            }
        });
    }
    
    // Initialize all sequences on page
    function initializeSequences() {
        var containers = document.querySelectorAll('.sequence-container');
        for (var i = 0; i < containers.length; i++) {
            randomizeSequence(containers[i]);
        }
        
        // Remove any "not implemented" warnings
        var warningElements = document.querySelectorAll('.alert-warning');
        for (var i = 0; i < warningElements.length; i++) {
            if (warningElements[i].textContent.indexOf('not yet implemented') !== -1) {
                warningElements[i].style.display = 'none';
            }
        }
    }
    
    // Randomize a sequence container
    function randomizeSequence(container) {
        if (!container) return;
        
        var list = container.querySelector('.sequence-list');
        var items = Array.from(list.querySelectorAll('.sequence-item'));
        
        // Shuffle items
        for (var i = items.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            list.appendChild(items[j]);
        }
        
        updateSequence(container);
    }
    
    // Update sequence numbers and data
    function updateSequence(container) {
        if (!container) return;
        
        var items = container.querySelectorAll('.sequence-item');
        
        // Update numbers
        for (var i = 0; i < items.length; i++) {
            var numElem = items[i].querySelector('.step-number');
            if (numElem) {
                numElem.textContent = (i + 1);
            }
        }
        
        // Update data
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
