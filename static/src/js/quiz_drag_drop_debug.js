odoo.define('quiz_engine_pro.drag_drop_debug', function (require) {
    'use strict';
    
    $(document).ready(function() {
        console.log('Quiz drag-drop debug loaded!');
        
        // Check for draggable elements
        var draggables = $('.draggable-token').length;
        console.log('Found ' + draggables + ' draggable tokens');
        
        // Check for drop zones
        var dropZones = $('.drop-zone').length;
        console.log('Found ' + dropZones + ' drop zones');
        
        // Set up manual handlers as a fallback
        $('.draggable-token').each(function() {
            $(this).css('cursor', 'move');
            
            // Add inline style to make draggable attribute more visible
            $(this).attr('style', 'cursor: grab !important; user-select: none;');
        });
    });
});
