$(document).ready(function() {
        // Handle checkbox change event
        $('input[type="checkbox"]').on('change', function() {
            // Submit the form
            $('#job-offer-filter-form').submit();
        });
    });