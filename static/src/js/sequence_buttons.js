// Simple inline JavaScript for sequence operations
(function() {
    // Add event handler on page load
    document.addEventListener('DOMContentLoaded', function() {
        // Find all move-up buttons
        var upButtons = document.querySelectorAll('.move-up');
        for (var i = 0; i < upButtons.length; i++) {
            upButtons[i].addEventListener('click', moveItemUp);
        }

        // Find all move-down buttons
        var downButtons = document.querySelectorAll('.move-down');
        for (var i = 0; i < downButtons.length; i++) {
            downButtons[i].addEventListener('click', moveItemDown);
        }

        // Find all reset buttons
        var resetButtons = document.querySelectorAll('.reset-sequence');
        for (var i = 0; i < resetButtons.length; i++) {
            resetButtons[i].addEventListener('click', randomizeItems);
        }

        // Randomize on first load
        var containers = document.querySelectorAll('.sequence-container');
        for (var i = 0; i < containers.length; i++) {
            randomize(containers[i].querySelector('.sequence-list'));
            updateNumbers(containers[i].querySelector('.sequence-list'));
            updateData(containers[i]);
        }
    });

    // Function to move an item up
    function moveItemUp(e) {
        var item = this.closest('.sequence-item');
        var prev = item.previousElementSibling;
        
        if (prev) {
            item.parentNode.insertBefore(item, prev);
            updateNumbers(item.parentNode);
            updateData(item.closest('.sequence-container'));
        }
    }

    // Function to move an item down
    function moveItemDown(e) {
        var item = this.closest('.sequence-item');
        var next = item.nextElementSibling;
        
        if (next) {
            item.parentNode.insertBefore(next, item);
            updateNumbers(item.parentNode);
            updateData(item.closest('.sequence-container'));
        }
    }

    // Function to randomize items
    function randomizeItems(e) {
        var container = this.closest('.sequence-container');
        var list = container.querySelector('.sequence-list');
        
        randomize(list);
        updateNumbers(list);
        updateData(container);
    }

    // Helper function to randomize items in a list
    function randomize(list) {
        var items = Array.from(list.children);
        items.sort(function() { return 0.5 - Math.random(); });
        
        for (var i = 0; i < items.length; i++) {
            list.appendChild(items[i]);
        }
    }

    // Function to update step numbers
    function updateNumbers(list) {
        var items = list.querySelectorAll('.sequence-item');
        
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
            data.push({
                step_id: parseInt(stepId, 10),
                position: i + 1
            });
        }
        
        var input = container.querySelector('input[name="sequence_data"]');
        if (input) {
            input.value = JSON.stringify(data);
        }
    }
})();
