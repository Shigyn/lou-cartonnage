/* L'art du cartonnage par Lou — apercu LocWeb : menu, revelations, leger suivi de la souris sur le collage. */
(function () {
  document.documentElement.classList.add('js');
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var tete = $('[data-tete]'), burger = $('[data-burger]'), menu = $('[data-menu]');
  function hauteur() { document.documentElement.style.setProperty('--haut-tete', tete.getBoundingClientRect().bottom + 'px'); }
  addEventListener('scroll', function () { tete.classList.toggle('colle', scrollY > 10); hauteur(); }, { passive: true });
  addEventListener('resize', hauteur); hauteur();
  burger.addEventListener('click', function () { hauteur(); var o = menu.classList.toggle('ouvert'); burger.setAttribute('aria-expanded', o); });
  $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { menu.classList.remove('ouvert'); burger.setAttribute('aria-expanded', 'false'); }); });

  // Collage : les photos suivent un peu la souris (ordinateur seulement).
  var collage = $('[data-collage]');
  if (collage && matchMedia('(hover: hover) and (prefers-reduced-motion: no-preference)').matches) {
    collage.style.transition = 'transform .6s cubic-bezier(.2,.7,.2,1)';
    $('.hero').addEventListener('mousemove', function (e) {
      var x = (e.clientX / innerWidth - .5) * -16, y = (e.clientY / innerHeight - .5) * -12;
      collage.style.transform = 'translate(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px)';
    });
    $('.hero').addEventListener('mouseleave', function () { collage.style.transform = ''; });
  }

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('vu'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    $$('.revele').forEach(function (el, i) { el.style.transitionDelay = (i % 3) * 80 + 'ms'; io.observe(el); });
  } else $$('.revele').forEach(function (el) { el.classList.add('vu'); });
})();
