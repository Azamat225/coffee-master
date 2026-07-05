(function () {
    const board = document.getElementById('galleryScatter');
    if (!board) return;

    const items = board.querySelectorAll('.gallery-scatter__item');
    if (!items.length) return;

    const slots = [
        { top: 4, left: 2, width: 26, rotate: -5 },
        { top: 8, left: 58, width: 30, rotate: 4 },
        { top: 3, left: 34, width: 22, rotate: -2 },
        { top: 38, left: 6, width: 28, rotate: 3 },
        { top: 42, left: 48, width: 32, rotate: -4 },
        { top: 36, left: 72, width: 24, rotate: 6 },
        { top: 68, left: 18, width: 30, rotate: -3 },
        { top: 70, left: 52, width: 26, rotate: 2 },
        { top: 64, left: 78, width: 20, rotate: -6 },
    ];

    function jitter(value, range) {
        return value + (Math.random() * range * 2 - range);
    }

    items.forEach(function (item, index) {
        const slot = slots[index % slots.length];
        const layer = index % slots.length;
        const top = Math.max(2, Math.min(72, jitter(slot.top, 4)));
        const left = Math.max(1, Math.min(78, jitter(slot.left, 5)));
        const width = Math.max(18, Math.min(36, jitter(slot.width, 3)));
        const rotate = jitter(slot.rotate, 4);

        item.style.top = top + '%';
        item.style.left = left + '%';
        item.style.width = width + '%';
        item.style.zIndex = String(10 + layer);
        item.style.transform = 'rotate(' + rotate.toFixed(1) + 'deg)';

        item.addEventListener('mouseenter', function () {
            item.style.transform = 'rotate(0deg) scale(1.04)';
        });

        item.addEventListener('mouseleave', function () {
            item.style.transform = 'rotate(' + rotate.toFixed(1) + 'deg)';
        });
    });
})();
