(function () {
    const header = document.getElementById('siteHeader');
    const hero = document.getElementById('hero');
    if (!header) return;

    const THRESHOLD = 60;

    function update() {
        const overHero = hero
            ? window.scrollY < hero.offsetHeight - THRESHOLD
            : window.scrollY < THRESHOLD;

        header.classList.toggle('header--over-hero', overHero);
        header.classList.toggle('header--scrolled', !overHero);
    }

    update();
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update, { passive: true });
})();
