// $(document).ready(function () {
//     // Handle checkbox change event
//     $('input[type="checkbox"]').on('change', function () {
//         $('#job-offer-filter-form').submit();
//     });
// });

$(document).ready(function () {
    // Add event listener to Apply Filters button
    $('.apply-filter').click(function () {

        // Automatically submit the form
        $('#job-offer-filter-form').submit();

    });
});

$(document).ready(function () {
    // Add event listener to Apply Filters button
    $('.apply-sort').click(function () {

        // Automatically submit the form
        $('#job-offer-sort-form').submit();

    });
});

$(document).ready(function scrollBarChecker() {
    var dropdown = document.querySelector(".checkbox-row");

    // Function to check if the scrollbar is needed and show/hide it accordingly
    function checkScrollbar() {
        var isScrollbarNeeded = dropdown.scrollHeight > dropdown.clientHeight;
        if (isScrollbarNeeded) {
            dropdown.style.paddingRight = "20px"; // Add space for scrollbar
        } else {
            dropdown.style.paddingRight = "0"; // Remove space if scrollbar is not needed
        }
    }

    // Check scrollbar initially and when the window is resized
    checkScrollbar();
    $(window).on("resize", checkScrollbar);
});

const filterButton = document.querySelector('#filter-button-icon-container');
const filterContainer = document.querySelector('#filter-container');

filterButton.addEventListener('click', filterDropdown);

function filterDropdown() {
    if (filterContainer.style.display === 'none') {
        filterContainer.style.display = 'flex'
    } else {
        filterContainer.style.display = 'none'
    }
}

