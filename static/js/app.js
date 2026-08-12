document.addEventListener("DOMContentLoaded", function () {
  var sidebar = document.getElementById("stSidebar");
  var toggle = document.getElementById("stSidebarToggle");
  if (toggle && sidebar) {
    toggle.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });
  }

  document.querySelectorAll("[data-confirm]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      if (!window.confirm(el.getAttribute("data-confirm"))) {
        e.preventDefault();
      }
    });
  });

  var flash = document.getElementById("stFlash");
  if (flash) {
    setTimeout(function () {
      flash.querySelectorAll(".alert").forEach(function (a) {
        a.classList.remove("show");
        a.classList.add("fade");
      });
    }, 6000);
  }
});
