(function () {
    const board = document.getElementById('galleryCollage');
    if (!board) return;

    const items = board.querySelectorAll('.gallery-collage__item');
    if (!items.length) return;

    const layouts = [
        { top: 0, left: -4, width: 30, rotate: -8, z: 4 },
        { top: 3, left: 22, width: 26, rotate: 6, z: 6 },
        { top: -2, left: 44, width: 52, rotate: -2, z: 5 },
        { top: 22, left: 2, width: 28, rotate: 5, z: 8 },
        { top: 26, left: 30, width: 32, rotate: -5, z: 9 },
        { top: 24, left: 58, width: 26, rotate: 7, z: 7 },
        { top: 48, left: -3, width: 34, rotate: -4, z: 10 },
        { top: 50, left: 28, width: 30, rotate: 3, z: 11 },
        { top: 52, left: 54, width: 38, rotate: -6, z: 12 },
    ];

    items.forEach(function (item, index) {
        const layout = layouts[index % layouts.length];
        const top = layout.top;
        const left = layout.left;
        const width = layout.width;
        const rotate = layout.rotate;

        item.style.top = top + '%';
        item.style.left = left + '%';
        item.style.width = width + '%';
        item.style.zIndex = String(layout.z);
        item.style.transform = 'rotate(' + rotate + 'deg)';

        item.addEventListener('mouseenter', function () {
            item.style.transform = 'rotate(0deg) scale(1.05)';
        });

        item.addEventListener('mouseleave', function () {
            item.style.transform = 'rotate(' + rotate + 'deg)';
        });
    });
})();
