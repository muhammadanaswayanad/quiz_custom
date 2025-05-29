// Very simple sequence button handlers
window.onload = function() {
    console.log("Sequence buttons initialized");
    
    // Add click listeners - using global onclick properties
    var upButtons = document.getElementsByClassName('move-up');
    for (var i = 0; i < upButtons.length; i++) {
        upButtons[i].onclick = moveItemUp;
    }
    
    var downButtons = document.getElementsByClassName('move-down');
    for (var i = 0; i < downButtons.length; i++) {
        downButtons[i].onclick = moveItemDown;
    }
    
    var resetButtons = document.getElementsByClassName('reset-sequence');
    for (var i = 0; i < resetButtons.length; i++) {
        resetButtons[i].onclick = randomizeItems;
    }
    
    // Initialize with randomization
    randomizeItems();
    
    // Function to move an item up
    function moveItemUp(e) {
        e.preventDefault(); // Prevent scrolling
        
        console.log("Move up clicked");
        var item = this.parentNode.parentNode; // From button to .sequence-item
        var prev = item.previousElementSibling;
        
        if (prev) {
            var parent = item.parentNode;
            parent.insertBefore(item, prev);
            updateOrder(parent.parentNode);
        }
    }
    
    // Function to move an item down
    function moveItemDown(e) {
        e.preventDefault(); // Prevent scrolling
        
        console.log("Move down clicked");
        var item = this.parentNode.parentNode; // From button to .sequence-item
        var next = item.nextElementSibling;
        
        if (next) {
            var parent = item.parentNode;
            parent.insertBefore(next, item);
            updateOrder(parent.parentNode);
        }
    }
    
    // Function to randomize items
    function randomizeItems(e) {
        if (e) e.preventDefault();
        
        console.log("Randomize clicked");
        var containers = document.getElementsByClassName('sequence-container');
        
        for (var c = 0; c < containers.length; c++) {
            var list = containers[c].getElementsByClassName('sequence-list')[0];
            if (!list) continue;
            
            var items = list.getElementsByClassName('sequence-item');
            var itemArray = Array.prototype.slice.call(items);
            
            // Shuffle
            itemArray.sort(function() { return 0.5 - Math.random(); });
            
            // Re-append in new order
            for (var i = 0; i < itemArray.length; i++) {
                list.appendChild(itemArray[i]);
            }
            
            updateOrder(containers[c]);
        }
    }
    
    // Update numbering and data
    function updateOrder(container) {
        // Update numbers
        var items = container.getElementsByClassName('sequence-item');
        for (var i = 0; i < items.length; i++) {
            var numEl = items[i].getElementsByClassName('step-number')[0];
            if (numEl) numEl.textContent = (i + 1);
        }
        
        // Update data
        var data = [];
        for (var i = 0; i < items.length; i++) {
            var stepId = items[i].getAttribute('data-step-id');
            data.push({
                step_id: parseInt(stepId, 10),
                position: i + 1
            });
        }
        
        var input = container.getElementsByClassName('sequence-container')[0].querySelector('input[name="sequence_data"]');
        if (input) {
            input.value = JSON.stringify(data);
            console.log("Updated data: " + input.value);
        } else {
            console.log("Input not found");
        }
    }
    
    // Hide any "not yet implemented" message
    var warnings = document.getElementsByClassName('alert-warning');
    for (var i = 0; i < warnings.length; i++) {
        if (warnings[i].textContent.indexOf('not yet implemented') !== -1) {
            warnings[i].style.display = 'none';
        }
    }
};
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
