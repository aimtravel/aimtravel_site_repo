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
// Mobile quick actions: appear only after meaningful scrolling.
(function () {
  var mq = window.matchMedia('(max-width: 800px)');
  function updateMobileActions() {
    if (!document.body) return;
    document.body.classList.toggle('mobile-actions-visible', mq.matches && window.scrollY > 420);
  }
  window.addEventListener('scroll', updateMobileActions, { passive: true });
  window.addEventListener('resize', updateMobileActions);
  document.addEventListener('DOMContentLoaded', updateMobileActions);
  updateMobileActions();
})();

// AIM Mobile Redesign v1 enhancements
(function () {
  function enhanceMobileExperience() {
    var main = document.querySelector("#main-slider");
    if (main) {
      var text = main.querySelector(".text-container");
      if (false) {
        var kicker = document.createElement("p");
        kicker.className = "mobile-hero-kicker";
        kicker.textContent = "WORK AND TRAVEL USA";
        text.insertBefore(kicker, text.firstChild);
      }
      var actions = main.querySelector(".slider-btn");
      if (actions && !actions.querySelector(".mobile-offers-link")) {
        var offers = document.createElement("a");
        offers.className = "mobile-offers-link";
        offers.href = "/rabotnioferti/";
        offers.textContent = "ВИЖ ОФЕРТИТЕ";
        actions.insertBefore(offers, actions.firstChild);
      }
    }
    var menu = document.querySelector("#ham-but-content");
    var burger = document.querySelector(".hamburger-button");
    if (burger) {
      burger.setAttribute("role", "button");
      burger.setAttribute("tabindex", "0");
      burger.setAttribute("aria-label", "Отвори меню");
    }
    if (menu && !menu.querySelector(".mobile-menu-contact")) {
      var contact = document.createElement("li");
      contact.className = "mobile-menu-contact";
      var row = document.createElement("div");
      row.className = "mobile-menu-contact-row";
      var phone = document.createElement("a");
      phone.href = "tel:+359889966583";
      phone.textContent = "☎  ОБАДИ СЕ";
      var email = document.createElement("a");
      email.href = "mailto:studentski@aimtravel.bg";
      email.textContent = "✉  ИМЕЙЛ";
      row.appendChild(phone);
      row.appendChild(email);
      contact.appendChild(row);
      menu.appendChild(contact);
    }
    if (menu && burger && !menu.dataset.mobileObserver) {
      var syncMenuState = function () {
        var open = menu.style.display === "flex";
        document.body.classList.toggle("mobile-menu-open", open);
        burger.setAttribute("aria-expanded", open ? "true" : "false");
        burger.setAttribute("aria-label", open ? "Затвори меню" : "Отвори меню");
      };
      new MutationObserver(syncMenuState).observe(menu, { attributes: true, attributeFilter: ["style"] });
      menu.dataset.mobileObserver = "1";
      syncMenuState();
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", enhanceMobileExperience);
  else enhanceMobileExperience();
})();
