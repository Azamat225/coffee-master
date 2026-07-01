(function () {
    const carousel = document.getElementById('carousel');
    if (!carousel) return;

    const slides = carousel.querySelectorAll('.carousel__slide');
    const dots = carousel.querySelectorAll('.carousel__dot');
    const prevBtn = document.getElementById('carouselPrev');
    const nextBtn = document.getElementById('carouselNext');

    if (slides.length <= 1) return;

    let current = 0;
    let autoplayTimer = null;
    const INTERVAL = 6000;

    function goTo(index) {
        slides[current].classList.remove('carousel__slide--active');
        if (dots[current]) dots[current].classList.remove('carousel__dot--active');

        current = (index + slides.length) % slides.length;

        slides[current].classList.add('carousel__slide--active');
        if (dots[current]) dots[current].classList.add('carousel__dot--active');

        const counter = document.getElementById('carouselCounter');
        if (counter) {
            const num = String(current + 1).padStart(2, '0');
            const total = String(slides.length).padStart(2, '0');
            counter.textContent = num + ' / ' + total;
        }
    }

    function next() { goTo(current + 1); }
    function prev() { goTo(current - 1); }

    function startAutoplay() {
        stopAutoplay();
        autoplayTimer = setInterval(next, INTERVAL);
    }

    function stopAutoplay() {
        if (autoplayTimer) clearInterval(autoplayTimer);
    }

    if (prevBtn) prevBtn.addEventListener('click', function () { prev(); startAutoplay(); });
    if (nextBtn) nextBtn.addEventListener('click', function () { next(); startAutoplay(); });

    dots.forEach(function (dot) {
        dot.addEventListener('click', function () {
            goTo(parseInt(dot.dataset.index, 10));
            startAutoplay();
        });
    });

    carousel.addEventListener('mouseenter', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);

    let touchStartX = 0;
    carousel.addEventListener('touchstart', function (e) {
        touchStartX = e.changedTouches[0].screenX;
        stopAutoplay();
    }, { passive: true });

    carousel.addEventListener('touchend', function (e) {
        const diff = e.changedTouches[0].screenX - touchStartX;
        if (Math.abs(diff) > 50) {
            diff < 0 ? next() : prev();
        }
        startAutoplay();
    }, { passive: true });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') { prev(); startAutoplay(); }
        if (e.key === 'ArrowRight') { next(); startAutoplay(); }
    });

    startAutoplay();
})();
