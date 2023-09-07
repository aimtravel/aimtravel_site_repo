// Get all elements with class "arrow-down" and "arrow-up"
  var arrowDownButtons = document.querySelectorAll(".arrow-down");
  var arrowUpButtons = document.querySelectorAll(".arrow-up");

  // Add click event listeners to all "arrow-down" buttons
  arrowDownButtons.forEach(function(button) {
    button.addEventListener("click", function() {
      // Toggle the visibility of the description
      var description = this.parentElement.nextElementSibling;
      description.style.display = "flex";

      // Hide the arrow-down button
      this.style.display = "none";

      // Show the arrow-up button
      var arrowUpButton = this.parentElement.querySelector(".arrow-up");
      arrowUpButton.style.display = "flex";
    });
  });

  // Add click event listeners to all "arrow-up" buttons
  arrowUpButtons.forEach(function(button) {
    button.addEventListener("click", function() {
      // Toggle the visibility of the description
      var description = this.parentElement.nextElementSibling;
      description.style.display = "none";

      // Hide the arrow-up button
      this.style.display = "none";

      // Show the arrow-down button
      var arrowDownButton = this.parentElement.querySelector(".arrow-down");
      arrowDownButton.style.display = "flex";
    });
  });