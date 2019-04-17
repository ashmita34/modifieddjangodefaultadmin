(function($) {
    'use strict';
    $(function() {
        $('.cancel-link').click(function(e) {
            e.preventDefault();
            window.history.back();
        });
    });
})(django.jQuery);

(function($) {
    // Custom JavaScript logic leveraging the Django admin built-in jQuery libray
    $(document).ready(function() {
        $('.deletelink').on('click',function() {
            if( !confirm('Are you sure you want to delete this record ?')) {
                return false;
            }
        });
    });
})(django.jQuery);
