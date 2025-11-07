const productDivs = document.querySelectorAll('.offer-slide');

// Loop through each product div
productDivs.forEach(product => {
    // Check if it has a child element with the class "sold-out"
    if (product.querySelector('.sold-out')) {
        // Add the "grayed-out" class to the product div
        var picture = product.querySelector('.offer-pic');
        var text = product.querySelector('.offer-text-container');
        picture.style.opacity = '60%';
        text.style.opacity = '60%';
    }
});