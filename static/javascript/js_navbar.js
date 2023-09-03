// Get the navigation bar element
var navbar = document.querySelector("nav");
var logo = document.querySelector("#logo")
var navA = document.querySelectorAll(".link-a");
var btn = document.querySelector(".nav-button");
var navCont = document.querySelector("#header-nav-links-container");

// Get the initial offset position of the navigation bar
var stickyOffset = navbar.offsetTop;

// Function to add the sticky class to the navigation bar when scrolling
function stickyNav() {
  if (window.pageYOffset >= stickyOffset) {
    navbar.classList.add("sticky");
    logo.style.width = '50px';
    logo.style.height = '50px';
    btn.style.display = 'flex';
    btn.classList.add("active")
    navCont.style.left = '120px'
    
    navA.forEach(element => {
      element.style.fontSize = '13px'
    });

    
  } else {
    navbar.classList.remove("sticky");
    logo.style.width = '84px';
    logo.style.height = '84px';
    btn.style.display = 'none';
    btn.classList.remove("active")
    navCont.style.left = '25px'

    navA.forEach(element => {
      element.style.fontSize = '16.5px'
    });
  }
}

// Add the stickyNav function as a scroll event listener
window.addEventListener("scroll", stickyNav);
