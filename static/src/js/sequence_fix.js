// Very simple implementation
document.addEventListener('DOMContentLoaded', function() {
    console.log("Sequence buttons init");
    
    // Setup buttons
    setupButtons();
    
    // Randomize on load
    randomizeAll();
    
    // Button setup function
    function setupButtons() {
        // Up buttons
        var upBtns = document.getElementsByClassName('move-up');
        for (var i = 0; i < upBtns.length; i++) {
            upBtns[i].onclick = function(e) {
                e.preventDefault();
                var item = this.closest('.sequence-item');
                var prev = item.previousElementSibling;
                if (prev) {
                    item.parentNode.insertBefore(item, prev);
                    updateSequence(item.closest('.sequence-container'));
                }
            };
        }
        
        // Down buttons
        var downBtns = document.getElementsByClassName('move-down');
        for (var i = 0; i < downBtns.length; i++) {
            downBtns[i].onclick = function(e) {
                e.preventDefault();
                var item = this.closest('.sequence-item');
                var next = item.nextElementSibling;
                if (next) {
                    item.parentNode.insertBefore(next, item);
                    updateSequence(item.closest('.sequence-container'));
                }
            };
        }
        
        // Reset buttons
        var resetBtns = document.getElementsByClassName('reset-sequence');
        for (var i = 0; i < resetBtns.length; i++) {
            resetBtns[i].onclick = function(e) {
                e.preventDefault();
                randomizeAll();
            };
        }
    }
    
    // Randomize all sequences
    function randomizeAll() {
        var containers = document.getElementsByClassName('sequence-container');
        for (var i = 0; i < containers.length; i++) {
            randomizeItems(containers[i]);
        }
    }
    
    // Randomize a single container
    function randomizeItems(container) {
        var list = container.querySelector('.sequence-list');
        if (!list) return;
        
        var items = list.querySelectorAll('.sequence-item');
        var itemsArr = Array.prototype.slice.call(items);
        
        // Fisher-Yates shuffle
        for (var i = itemsArr.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            list.appendChild(itemsArr[j]);
        }
        
        updateSequence(container);
    }
    
    // Update numbers and data
    function updateSequence(container) {
        var items = container.querySelectorAll('.sequence-item');
        
        // Update numbers
        for (var i = 0; i < items.length; i++) {
            var numEl = items[i].querySelector('.step-number');
            if (numEl) {
                numEl.textContent = (i + 1);
            }
        }
        
        // Update data
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
        }
    }
    
    // Hide "not implemented" message
    var warnings = document.querySelectorAll('.alert-warning');
    for (var i = 0; i < warnings.length; i++) {
        if (warnings[i].textContent.includes('not yet implemented')) {
            warnings[i].style.display = 'none';
        }
    }
});
