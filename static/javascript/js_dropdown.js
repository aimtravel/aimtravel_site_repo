// var element = document.getElementById('wat-usa');
// var child = document.getElementById('wat-usa-dropdown')
// element.addEventListener('click', () => {
//     if (child.style.display === "flex") {
//       child.style.display = "none";
//       child.style.opacity = 0;
//     } else {
//       child.style.display = "flex";
//       child.style.opacity = 1;
//     }
// });



// Get all the elements with the class "target-element"
var targetElements = document.querySelectorAll('.target-element');

// Loop through each target element
targetElements.forEach(function(element) {
  // Add an onclick event listener to each target element
  element.addEventListener('click', function() {
    // Get the corresponding tooltip element
    var tooltip = this.nextElementSibling;

    // Check the current display property value
    var currentDisplay = window.getComputedStyle(tooltip).display;
    // var currentOpacity = window.getComputedStyle(tooltip).opacity;

    // Toggle the display property of the tooltip element
    tooltip.style.display = currentDisplay === 'flex' ? 'none' : 'flex';
    // tooltip.style.opacity = currentOpacity === '1' ? '0' : '1';
  });
});
