document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.team-bio__toggle').forEach(function (button) {
    button.addEventListener('click', function () {
      var container = button.closest('.team-bio--expandable');
      if (!container) return;

      var preview = container.querySelector('.team-bio__preview');
      var full = container.querySelector('.team-bio__full');
      var expanded = button.getAttribute('aria-expanded') === 'true';

      if (expanded) {
        preview.hidden = false;
        full.hidden = true;
        button.setAttribute('aria-expanded', 'false');
        button.textContent = 'Read more';
      } else {
        preview.hidden = true;
        full.hidden = false;
        button.setAttribute('aria-expanded', 'true');
        button.textContent = 'Read less';
      }
    });
  });
});
