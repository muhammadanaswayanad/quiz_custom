$(function() {
    // Basic drag and drop functionality
    var draggables = document.querySelectorAll('.draggable-token');
    var dropZones = document.querySelectorAll('.drop-zone');
    
    console.log('Quiz inline script found ' + draggables.length + ' draggables and ' + dropZones.length + ' zones');
    
    // Add draggable attribute directly
    draggables.forEach(function(token) {
        token.setAttribute('draggable', 'true');
        token.style.cursor = 'grab';
        
        token.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', this.getAttribute('data-token-id'));
            this.classList.add('dragging');
        });
    });
    
    // Set up drop zones
    dropZones.forEach(function(zone) {
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        zone.addEventListener('dragleave', function() {
            this.classList.remove('drag-over');
        });
        
        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            var tokenId = e.dataTransfer.getData('text/plain');
            var token = document.querySelector('.draggable-token[data-token-id="' + tokenId + '"]');
            
            if (token) {
                this.appendChild(token);
                token.classList.remove('dragging');
                
                // Update hidden field
                updateFormData();
            }
        });
    });
    
    // Reset functionality
    document.querySelectorAll('.reset-tokens').forEach(function(button) {
        button.addEventListener('click', function() {
            // Move all tokens back to the tokens container
            var tokensContainer = document.querySelector('.tokens-container');
            if (tokensContainer) {
                draggables.forEach(function(token) {
                    tokensContainer.appendChild(token);
                });
            }
        });
    });
    
    function updateFormData() {
        var data = [];
        document.querySelectorAll('.drop-zone').forEach(function(zone) {
            var zoneId = zone.getAttribute('data-zone-id');
            zone.querySelectorAll('.draggable-token').forEach(function(token) {
                data.push({
                    token_id: token.getAttribute('data-token-id'),
                    zone_id: zoneId
                });
            });
        });
        
        var hiddenField = document.querySelector('input[name="drag_drop_data"]');
        if (hiddenField) {
            hiddenField.value = JSON.stringify(data);
        }
    }
});
