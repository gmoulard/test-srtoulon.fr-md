(function () {
  var burger = document.querySelector('.burger');
  var menu = document.getElementById('menu');
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      burger.setAttribute('aria-expanded', String(open));
    });
  }

  var hero = document.querySelector('.hero[data-fonds]');
  if (hero) {
    try {
      var fonds = JSON.parse(hero.getAttribute('data-fonds'));
      if (fonds.length) {
        document.getElementById('heroBg').src = fonds[Math.floor(Math.random() * fonds.length)];
      }
    } catch (e) {}
  }

  var root = document.getElementById('stories');
  if (root) {
    var track = root.querySelector('.track');
    var slides = track.querySelectorAll('.slide');
    var dots = root.querySelector('.dots');
    var current = 0;
    var timer = null;
    var stop = function () { if (timer) { clearInterval(timer); timer = null; } };
    var mark = function () {
      dots.querySelectorAll('button').forEach(function (d, i) { d.setAttribute('aria-current', String(i === current)); });
    };
    var go = function (i) {
      current = (i + slides.length) % slides.length;
      track.scrollTo({ left: current * track.clientWidth });
      mark();
    };
    slides.forEach(function (_, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', 'Récit ' + (i + 1));
      b.addEventListener('click', function () { stop(); go(i); });
      dots.appendChild(b);
    });
    track.addEventListener('scroll', function () {
      var i = Math.round(track.scrollLeft / track.clientWidth);
      if (i !== current) { current = i; mark(); }
    }, { passive: true });
    root.querySelector('.prev').addEventListener('click', function () { stop(); go(current - 1); });
    root.querySelector('.next').addEventListener('click', function () { stop(); go(current + 1); });
    track.addEventListener('pointerdown', stop);
    track.addEventListener('touchstart', stop, { passive: true });
    mark();
    if (slides.length > 1 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      timer = setInterval(function () { go(current + 1); }, 7000);
    }
  }

  var filters = document.querySelectorAll('.filters button');
  filters.forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.getAttribute('data-filtre');
      filters.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      document.querySelectorAll('.card').forEach(function (c) {
        c.hidden = !!f && c.getAttribute('data-activite') !== f;
      });
    });
  });
})();
