(function() {
    "use strict";
    
    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initSequenceHandlers();
    });
    
    function initSequenceHandlers() {
        // Set up click event delegation
        document.addEventListener('click', function(e) {
            // Move up
            if (e.target.classList.contains('move-up')) {
                e.preventDefault();
                var item = e.target.closest('.sequence-item');
                var prev = item.previousElementSibling;
                
                if (prev && prev.classList.contains('sequence-item')) {
                    var list = item.parentNode;
                    list.insertBefore(item, prev);
                    updateSequenceNumbers(list);
                    updateSequenceData(item.closest('.sequence-container'));
                }
            }
            
            // Move down
            if (e.target.classList.contains('move-down')) {
                e.preventDefault();
                var item = e.target.closest('.sequence-item');
                var next = item.nextElementSibling;
                
                if (next && next.classList.contains('sequence-item')) {
                    var list = item.parentNode;
                    if (next.nextElementSibling) {
                        list.insertBefore(item, next.nextElementSibling);
                    } else {
                        list.appendChild(item);
                    }
                    updateSequenceNumbers(list);
                    updateSequenceData(item.closest('.sequence-container'));
                }
            }
            
            // Randomize
            if (e.target.classList.contains('reset-sequence')) {
                e.preventDefault();
                var container = e.target.closest('.sequence-container');
                var list = container.querySelector('.sequence-list');
                
                randomizeItems(list);
                updateSequenceNumbers(list);
                updateSequenceData(container);
            }
        });
        
        // Initialize all sequence containers
        var containers = document.querySelectorAll('.sequence-container');
        containers.forEach(function(container) {
            var list = container.querySelector('.sequence-list');
            if (list) {
                randomizeItems(list);
                updateSequenceNumbers(list);
                updateSequenceData(container);
                
                // Hide any "not yet implemented" messages
                var warnings = document.querySelectorAll('.alert-warning');
                warnings.forEach(function(warning) {
                    if (warning.textContent.includes('not yet implemented')) {
                        warning.style.display = 'none';
                    }
                });
            }
        });
    }
    
    function randomizeItems(list) {
        var items = Array.from(list.querySelectorAll('.sequence-item'));
        if (items.length <= 1) return;
        
        // Shuffle
        for (var i = items.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            list.appendChild(items[j]);
        }
    }
    
    function updateSequenceNumbers(list) {
        var items = list.querySelectorAll('.sequence-item');
        for (var i = 0; i < items.length; i++) {
            var numEl = items[i].querySelector('.step-number');
            if (numEl) {
                numEl.textContent = (i + 1);
            }
        }
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
