(function () {
    const reveals = document.querySelectorAll('.reveal');
    if (!reveals.length) return;

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('reveal--visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach(function (el) { observer.observe(el); });

    const hero = document.getElementById('hero');
    const heroImage = hero && hero.querySelector('.hero__image');
    if (hero && heroImage) {
        window.addEventListener('scroll', function () {
            const y = window.scrollY;
            const limit = hero.offsetHeight;
            if (y < limit) {
                heroImage.style.transform = 'scale(' + (1 + y * 0.0002) + ') translateY(' + (y * 0.25) + 'px)';
            }
        }, { passive: true });
    }
})();
