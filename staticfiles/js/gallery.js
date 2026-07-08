(function () {
    const lightbox = document.getElementById('galleryLightbox');
    const lightboxImg = document.getElementById('lightboxImg');
    const lightboxClose = document.getElementById('lightboxClose');

    if (!lightbox || !lightboxImg) return;

    function openLightbox(src, alt) {
        lightboxImg.src = src;
        lightboxImg.alt = alt || '';
        lightbox.hidden = false;
        document.body.classList.add('lightbox-open');
    }

    function closeLightbox() {
        lightbox.hidden = true;
        lightboxImg.src = '';
        document.body.classList.remove('lightbox-open');
    }

    document.querySelectorAll('.gallery-item__open').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const img = btn.querySelector('img');
            openLightbox(btn.dataset.full || img.src, img.alt);
        });
    });

    if (lightboxClose) {
        lightboxClose.addEventListener('click', closeLightbox);
    }

    lightbox.addEventListener('click', function (e) {
        if (e.target === lightbox) closeLightbox();
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !lightbox.hidden) closeLightbox();
    });
})();
