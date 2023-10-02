// Get the navigation bar element
var navbar = document.querySelector("nav");
var logo = document.querySelector("#logo")
var navA = document.querySelectorAll(".link-a");
var btn = document.querySelector(".nav-button");
var navCont = document.querySelector("#header-nav-links-container");
const mediaQuery = window.matchMedia('(max-width: 800px)');
// Get the initial offset position of the navigation bar
var stickyOffset = navbar.offsetTop;

// Function to add the sticky class to the navigation bar when scrolling
function stickyNav() {
  if (window.pageYOffset >= stickyOffset) {
    navbar.classList.add("sticky");
    logo.classList.add("sticky-logo");
    btn.classList.add("flex-on");
    // btn.classList.add("active");
    // navCont.classList.add("sticky-left");
    navCont.classList.remove("normal-left");

    navA.forEach(element => {
      element.classList.add("sticky-font");
    });

    
  } else {
    navbar.classList.remove("sticky");
    logo.classList.remove("sticky-logo");
    btn.classList.remove("flex-on");
    // btn.classList.remove("active")
    // navCont.classList.remove("sticky-left");
    navCont.classList.add("normal-left");

    navA.forEach(element => {
      element.classList.remove("sticky-font");
    });
  }
}

// Add the stickyNav function as a scroll event listener
window.addEventListener("scroll", stickyNav);
