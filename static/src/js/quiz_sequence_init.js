// Initialize sequence functionality manually as a fallback
document.addEventListener('DOMContentLoaded', function() {
    // Only run if the sequence container exists
    var container = document.querySelector('.sequence-container');
    if (!container) return;
    
    // Remove error message
    var errorMsg = container.querySelector('.alert-info');
    if (errorMsg && errorMsg.textContent.includes('not yet implemented')) {
        errorMsg.remove();
    }
    
    // Initialize sortable if available
    if (window.Sortable !== undefined) {
        var sequenceList = container.querySelector('.sequence-list');
        if (sequenceList) {
            var sortable = new Sortable(sequenceList, {
                animation: 150,
                ghostClass: 'sortable-ghost',
                handle: '.sequence-handle',
                onEnd: function() {
                    updateSequenceData();
                }
            });
            
            // Randomize initially
            randomizeItems();
            
            // Set up event listeners
            container.querySelector('.reset-sequence').addEventListener('click', function() {
                randomizeItems();
                updateSequenceData();
            });
            
            // Setup move buttons
            container.querySelectorAll('.move-up').forEach(function(btn) {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    var item = e.target.closest('.sequence-item');
                    var prev = item.previousElementSibling;
                    
                    if (prev) {
                        sequenceList.insertBefore(item, prev);
                        updateSequenceData();
                    }
                });
            });
            
            container.querySelectorAll('.move-down').forEach(function(btn) {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    var item = e.target.closest('.sequence-item');
                    var next = item.nextElementSibling;
                    
                    if (next) {
                        sequenceList.insertBefore(next, item);
                        updateSequenceData();
                    }
                });
            });
            
            // Update initial data
            updateSequenceData();
        }
    }
    
    // Helper functions
    function randomizeItems() {
        var list = container.querySelector('.sequence-list');
        if (!list) return;
        
        var items = Array.from(list.querySelectorAll('.sequence-item'));
        
        // Shuffle items
        for (var i = items.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            list.appendChild(items[j]);
        }
        
        updateStepNumbers();
    }
    
    function updateStepNumbers() {
        var items = container.querySelectorAll('.sequence-item');
        for (var i = 0; i < items.length; i++) {
            var numberElement = items[i].querySelector('.step-number');
            if (numberElement) {
                numberElement.textContent = (i + 1);
            }
        }
    }
    
    function updateSequenceData() {
        var data = [];
        var items = container.querySelectorAll('.sequence-item');
        
        for (var i = 0; i < items.length; i++) {
            var stepId = items[i].getAttribute('data-step-id');
            var position = i + 1;
            
            data.push({
                'step_id': parseInt(stepId),
                'position': position
            });
        }
        
        updateStepNumbers();
        
        var inputEl = container.querySelector('input[name="sequence_data"]');
        if (inputEl) {
            inputEl.value = JSON.stringify(data);
        }
    }
});
