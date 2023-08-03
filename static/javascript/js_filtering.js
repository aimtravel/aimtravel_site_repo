$(document).ready(function () {
    // Handle checkbox change event
    $('input[type="checkbox"]').on('change', function () {

    });
});

$(document).ready(function() {
        // Add event listener to Apply Filters button
        $('#apply-filter').click(function() {
            // Automatically submit the form
            $('#job-offer-filter-form').submit();
        });
    });