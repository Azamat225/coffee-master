(function () {
    const header = document.getElementById('siteHeader');
    const topbar = document.getElementById('topbar');
    const siteScroll = document.getElementById('siteScroll');
    const menuToggle = document.getElementById('menuToggle');

    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }

    function lockPageScroll() {
        document.documentElement.style.overflow = 'hidden';
        document.documentElement.style.position = 'fixed';
        document.documentElement.style.inset = '0';
        document.documentElement.style.width = '100%';
        document.body.style.overflow = 'hidden';
        document.body.style.position = 'fixed';
        document.body.style.inset = '0';
        document.body.style.width = '100%';
    }

    function resetScroll() {
        if (siteScroll) siteScroll.scrollTop = 0;
        window.scrollTo(0, 0);
    }

    function syncLayout() {
        if (!topbar || !header || !siteScroll) return;

        const topbarH = topbar.offsetHeight;
        const headerH = header.offsetHeight;
        const scrollTop = topbarH + headerH;

        topbar.style.position = 'fixed';
        topbar.style.top = '0';
        topbar.style.left = '0';
        topbar.style.right = '0';
        topbar.style.zIndex = '100002';

        header.style.position = 'fixed';
        header.style.top = topbarH + 'px';
        header.style.left = '0';
        header.style.right = '0';
        header.style.zIndex = '100001';

        siteScroll.style.position = 'fixed';
        siteScroll.style.top = scrollTop + 'px';
        siteScroll.style.left = '0';
        siteScroll.style.right = '0';
        siteScroll.style.bottom = '0';
        siteScroll.style.overflowY = 'auto';
    }

    function scrollToHash(hash) {
        if (!hash || hash === '#' || !siteScroll) return;
        const target = document.querySelector(hash);
        if (!target) return;

        const scrollRect = siteScroll.getBoundingClientRect();
        const targetRect = target.getBoundingClientRect();
        const top = siteScroll.scrollTop + targetRect.top - scrollRect.top;

        siteScroll.scrollTo({ top: top, behavior: 'smooth' });
    }

    lockPageScroll();
    syncLayout();
    resetScroll();

    if (window.location.hash) {
        history.replaceState(null, '', window.location.pathname + window.location.search);
    }

    window.addEventListener('resize', syncLayout, { passive: true });
    window.addEventListener('load', resetScroll);
    window.addEventListener('pageshow', resetScroll);

    window.addEventListener('scroll', function () {
        window.scrollTo(0, 0);
    }, { passive: true });

    document.addEventListener('click', function (event) {
        const link = event.target.closest('a[href^="#"]');
        if (!link || !siteScroll) return;

        const hash = link.getAttribute('href');
        if (!hash || hash === '#') return;

        const target = document.querySelector(hash);
        if (!target) return;

        event.preventDefault();
        scrollToHash(hash);

        if (header) header.classList.remove('header--open');
        if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
    });

    if (!header || !menuToggle) return;

    menuToggle.addEventListener('click', function () {
        const open = header.classList.toggle('header--open');
        menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
})();
