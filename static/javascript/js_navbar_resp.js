const mainElements = document.querySelectorAll(".main-element");

mainElements.forEach((element) => {
    element.addEventListener("click", function () {
        const contentOptions = this.nextElementSibling;
        const arrowUp = this.querySelector(".arrow-up");
        const arrowDown = this.querySelector(".arrow-down");

        if (contentOptions.style.display === "none" || contentOptions.style.display === "") {
            contentOptions.style.display = "flex";
            arrowUp.style.display = "flex";
            arrowDown.style.display = "none";
        } else {
            contentOptions.style.display = "none";
            arrowUp.style.display = "none";
            arrowDown.style.display = "flex";
        }
    });
});