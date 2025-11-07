$(document).ready(function () {
    $('#sort-by-select-resp').change(function () {
        $('#job-offer-sort-form-resp').submit();
    });
    console.log('sorting - done')
});

// Filtering behavior - when click on "FILTER" button under responsive mode,
// this will open a menu with filtering options

const filterArea = document.querySelector('#offers-page-top-row.resp-filtering')
const filterButton = document.querySelector('#show-filter');
const filterButtonText = document.querySelector('#show-filter p')
const filterContainer = document.querySelector('#filter-container-resp');
const filterTextArea = document.querySelector('#text-area');


filterButton.addEventListener('click', filterDropdown);

function filterDropdown() {
    if (filterContainer.style.display === 'none') {
        filterContainer.style.display = 'flex'
        filterTextArea.style.display = 'none'
        filterArea.classList.add('absolute-position')
        filterButtonText.textContent = 'НАЗАД'
        filterButton.style.background = 'none'
    } else {
        filterContainer.style.display = 'none'
        filterTextArea.style.display = 'flex'
        filterArea.classList.remove('absolute-position')
        filterButtonText.textContent = 'ИЗБЕРИ ФИЛТРИ'
        filterButton.style.background = 'var(--red-color)'
    }
}


//Filter options expanding

// const offerFilters = document.querySelectorAll('#filter-container-resp .dropdown.offer-filters')
// offerFilters.forEach((element) => {
//     element.addEventListener('click', function () {
//         var nextElement = element.nextElementSibling
//         console.log(nextElement)
//         if (nextElement.style.display === 'none' || nextElement.style.display === '') {
//             nextElement.style.display = 'flex'
//         } else {
//             nextElement.style.display = 'none'
//         }
//
//     })
//
// })


$(document).ready(function () {
    // Add event listener to Apply Filters button
    $('.apply-filter-resp').click(function () {

        // Automatically submit the form
        $('#job-offer-filter-form-resp').submit();

    });
});


const faqHeaders = document.querySelectorAll("#filter-container-resp .dropdown.offer-filters");

faqHeaders.forEach((header) => {
    header.addEventListener("click", function () {
        const contentDescription = this.nextElementSibling;
        const arrowUp = this.querySelector(".arrow-up");
        const arrowDown = this.querySelector(".arrow-down");

        if (contentDescription.style.display === "none" || contentDescription.style.display === "") {
            contentDescription.style.display = "flex";
            arrowUp.style.display = "flex";
            arrowDown.style.display = "none";
        } else {
            contentDescription.style.display = "none";
            arrowUp.style.display = "none";
            arrowDown.style.display = "flex";
        }
    });
});
