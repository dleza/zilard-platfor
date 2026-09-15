(function () {
  var toggle = document.querySelector("[data-zil-nav-toggle]");
  var nav = document.getElementById("zil-primary-nav");
  if (!toggle || !nav) return;

  toggle.addEventListener("click", function () {
    var isOpen = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && nav.classList.contains("is-open")) {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.focus();
    }
  });
})();

(function () {
  var carousel = document.querySelector("[data-zil-carousel]");
  if (!carousel) return;

  var slides = Array.prototype.slice.call(carousel.querySelectorAll(".zil-slide"));
  var dots = Array.prototype.slice.call(carousel.querySelectorAll("[data-zil-dot]"));
  var prevBtn = carousel.querySelector("[data-zil-prev]");
  var nextBtn = carousel.querySelector("[data-zil-next]");
  if (slides.length < 2) return;

  var current = 0;
  var AUTOPLAY_MS = 6500;
  var timer = null;
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function show(index) {
    slides[current].classList.remove("is-active");
    slides[current].setAttribute("hidden", "");
    dots[current] && dots[current].classList.remove("is-active");

    current = (index + slides.length) % slides.length;

    slides[current].removeAttribute("hidden");
    // Force layout so the opacity transition runs on the newly-shown slide.
    void slides[current].offsetWidth;
    slides[current].classList.add("is-active");
    dots[current] && dots[current].classList.add("is-active");
  }

  function next() { show(current + 1); }
  function prev() { show(current - 1); }

  function startAutoplay() {
    if (reduceMotion) return;
    stopAutoplay();
    timer = window.setInterval(next, AUTOPLAY_MS);
  }
  function stopAutoplay() {
    if (timer) { window.clearInterval(timer); timer = null; }
  }

  nextBtn && nextBtn.addEventListener("click", function () { next(); startAutoplay(); });
  prevBtn && prevBtn.addEventListener("click", function () { prev(); startAutoplay(); });
  dots.forEach(function (dot, i) {
    dot.addEventListener("click", function () { show(i); startAutoplay(); });
  });

  carousel.addEventListener("mouseenter", stopAutoplay);
  carousel.addEventListener("mouseleave", startAutoplay);
  carousel.addEventListener("focusin", stopAutoplay);
  carousel.addEventListener("focusout", startAutoplay);

  carousel.addEventListener("keydown", function (event) {
    if (event.key === "ArrowRight") { next(); startAutoplay(); }
    if (event.key === "ArrowLeft") { prev(); startAutoplay(); }
  });

  startAutoplay();
})();
