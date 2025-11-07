// let element = document.getElementById('wat-usa');
// let child = document.getElementById('wat-usa-dropdown')
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
let targetElements = document.querySelectorAll('.target-element');

// Loop through each target element
targetElements.forEach(function(element) {
  // Add an onclick event listener to each target element
  element.addEventListener('click', function() {
    // Get the corresponding tooltip element
    let tooltip = this.nextElementSibling;

    // Check the current display property value
    let currentDisplay = window.getComputedStyle(tooltip).display;
    // let currentOpacity = window.getComputedStyle(tooltip).opacity;

    // Toggle the display property of the tooltip element
    tooltip.style.display = currentDisplay === 'flex' ? 'none' : 'flex';
    // tooltip.style.opacity = currentOpacity === '1' ? '0' : '1';
  });
});
