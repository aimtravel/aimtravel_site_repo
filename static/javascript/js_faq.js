const faqHeaders = document.querySelectorAll(".faq-content-header");

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


