// Get the navigation bar element
var navbar = document.querySelector("nav");
var logo = document.querySelector("#logo")
var navA = document.querySelectorAll(".link-a");

// Get the initial offset position of the navigation bar
var stickyOffset = navbar.offsetTop;

// Function to add the sticky class to the navigation bar when scrolling
function stickyNav() {
  if (window.pageYOffset >= stickyOffset) {
    navbar.classList.add("sticky");
    logo.style.width = '50px';
    logo.style.height = '50px';
    
    navA.forEach(element => {
      element.style.fontSize = '13px'
    });

    
  } else {
    navbar.classList.remove("sticky");
    logo.style.width = '112px';
    logo.style.height = '118px';

    navA.forEach(element => {
      element.style.fontSize = '20px'
    });
  }
}

// Add the stickyNav function as a scroll event listener
window.addEventListener("scroll", stickyNav);
