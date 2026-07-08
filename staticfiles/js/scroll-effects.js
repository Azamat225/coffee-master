(function () {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const scrollRoot = document.getElementById('siteScroll') || window;
    const hero = document.getElementById('hero');
    const heroContent = document.getElementById('heroContent');
    const heroImage = hero && hero.querySelector('.hero__image');
    const heroOverlay = hero && hero.querySelector('.hero__overlay');

    function updateHero() {
        if (!hero || reducedMotion) return;

        const rect = hero.getBoundingClientRect();
        const heroH = hero.offsetHeight;
        const scrollRect = scrollRoot === window
            ? { top: 0 }
            : scrollRoot.getBoundingClientRect();
        const scrolled = Math.max(0, scrollRect.top - rect.top);
        const progress = Math.min(scrolled / (heroH * 0.75), 1);

        if (heroContent) {
            const lift = scrolled * 0.45;
            const fade = Math.max(0, 1 - progress * 1.15);
            heroContent.style.transform = 'translate3d(0, ' + (-lift) + 'px, 0)';
            heroContent.style.opacity = String(fade);
        }

        if (heroImage) {
            const scale = 1 + progress * 0.1;
            const imgY = scrolled * 0.18;
            heroImage.style.transform = 'scale(' + scale + ') translate3d(0, ' + imgY + 'px, 0)';
        }

        if (heroOverlay) {
            heroOverlay.style.opacity = String(0.85 + progress * 0.15);
        }
    }

    function initScrollRise() {
        const items = document.querySelectorAll('.scroll-rise');
        if (!items.length) return;

        if (reducedMotion) {
            items.forEach(function (el) { el.classList.add('is-visible'); });
            return;
        }

        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            root: scrollRoot === window ? null : scrollRoot,
            threshold: 0.12,
            rootMargin: '0px 0px -8% 0px',
        });

        items.forEach(function (el) { observer.observe(el); });
    }

    let ticking = false;
    function onScroll() {
        if (!ticking) {
            window.requestAnimationFrame(function () {
                updateHero();
                ticking = false;
            });
            ticking = true;
        }
    }

    initScrollRise();
    updateHero();
    scrollRoot.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', updateHero, { passive: true });
})();
