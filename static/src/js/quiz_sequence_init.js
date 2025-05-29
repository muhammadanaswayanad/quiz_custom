// Initialize sequence functionality manually as a fallback
document.addEventListener('DOMContentLoaded', function() {
    // Only run if the sequence container exists
    var container = document.querySelector('.sequence-container');
    if (!container) return;
    
    // Remove error message
    var errorMsg = document.querySelector('.alert-info');
    if (errorMsg && errorMsg.textContent && errorMsg.textContent.includes('not yet implemented')) {
        errorMsg.remove();
    }
    
    // Initialize sortable if available
    var sequenceList = container.querySelector('.sequence-list');
    if (sequenceList) {
        try {
            // Try to initialize Sortable if available
            if (typeof Sortable !== 'undefined') {
                var sortable = new Sortable(sequenceList, {
                    animation: 150,
                    ghostClass: 'sortable-ghost',
                    handle: '.sequence-handle',
                    onEnd: function() {
                        updateSequenceData();
                    }
                });
            }
        } catch (e) {
            console.error("Error initializing Sortable:", e);
        }
        
        // Randomize initially
        randomizeItems();
        
        // Set up event listeners for buttons
        setupEventListeners();
        
        // Update initial data
        updateSequenceData();
    }
    
    // Helper function to setup event listeners
    function setupEventListeners() {
        // Reset button
        var resetBtn = container.querySelector('.reset-sequence');
        if (resetBtn) {
            resetBtn.addEventListener('click', function(e) {
                e.preventDefault();
                randomizeItems();
                updateSequenceData();
            });
        }
        
        // Move up buttons
        var moveUpBtns = container.querySelectorAll('.move-up');
        for (var i = 0; i < moveUpBtns.length; i++) {
            moveUpBtns[i].addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                var item = this.closest('.sequence-item');
                var prev = item.previousElementSibling;
                
                if (prev && prev.classList.contains('sequence-item')) {
                    sequenceList.insertBefore(item, prev);
                    updateSequenceData();
                }
            });
        }
        
        // Move down buttons
        var moveDownBtns = container.querySelectorAll('.move-down');
        for (var i = 0; i < moveDownBtns.length; i++) {
            moveDownBtns[i].addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                var item = this.closest('.sequence-item');
                var next = item.nextElementSibling;
                
                if (next && next.classList.contains('sequence-item')) {
                    sequenceList.insertBefore(next, item);
                    updateSequenceData();
                }
            });
        }
    }
    
    // Helper function to randomize items
    function randomizeItems() {
        if (!sequenceList) return;
        
        var items = Array.from(sequenceList.querySelectorAll('.sequence-item'));
        if (items.length < 2) return; // No need to shuffle one item
        
        // Shuffle items
        for (var i = items.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            if (items[j] && items[j].parentNode === sequenceList) {
                sequenceList.appendChild(items[j]);
            }
        }
        
        updateStepNumbers();
    }
    
    // Helper function to update step numbers
    function updateStepNumbers() {
        var items = sequenceList.querySelectorAll('.sequence-item');
        for (var i = 0; i < items.length; i++) {
            var numberElement = items[i].querySelector('.step-number');
            if (numberElement) {
                numberElement.textContent = (i + 1);
            }
        }
    }
    
    // Helper function to update sequence data
    function updateSequenceData() {
        var data = [];
        var items = sequenceList.querySelectorAll('.sequence-item');
        
        for (var i = 0; i < items.length; i++) {
            var stepId = items[i].getAttribute('data-step-id');
            if (stepId) {
                data.push({
                    step_id: parseInt(stepId, 10),
                    position: i + 1
                });
            }
        }
        
        updateStepNumbers();
        
        var inputEl = container.querySelector('input[name="sequence_data"]');
        if (inputEl) {
            inputEl.value = JSON.stringify(data);
        }
    }
});
