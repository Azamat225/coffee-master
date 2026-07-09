(function () {
    const header = document.getElementById('siteHeader');
    const siteScroll = document.getElementById('siteScroll');
    const menuToggle = document.getElementById('menuToggle');
    const siteNav = document.getElementById('siteNav');

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

    function syncLayout() {
        if (!header || !siteScroll) return;

        const headerH = header.offsetHeight;
        document.documentElement.style.setProperty('--site-header-h', headerH + 'px');
        header.style.position = 'fixed';
        header.style.top = '0';
        header.style.left = '0';
        header.style.right = '0';
        header.style.zIndex = '100001';

        siteScroll.style.position = 'fixed';
        siteScroll.style.top = headerH + 'px';
        siteScroll.style.left = '0';
        siteScroll.style.right = '0';
        siteScroll.style.bottom = '0';
        siteScroll.style.overflowY = 'auto';
    }

    function closeMenu() {
        if (header) header.classList.remove('site-header--open');
        if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
    }

    lockPageScroll();
    syncLayout();

    if (window.location.hash) {
        history.replaceState(null, '', window.location.pathname + window.location.search);
    }

    window.addEventListener('resize', syncLayout, { passive: true });
    window.addEventListener('load', syncLayout);
    window.addEventListener('pageshow', syncLayout);

    window.addEventListener('scroll', function () {
        window.scrollTo(0, 0);
    }, { passive: true });

    if (menuToggle && header) {
        menuToggle.addEventListener('click', function () {
            const open = header.classList.toggle('site-header--open');
            menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    }

    if (siteNav) {
        siteNav.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', closeMenu);
        });
    }

    if (siteScroll && header) {
        function updateHeaderScroll() {
            header.classList.toggle('site-header--scrolled', siteScroll.scrollTop > 16);
        }
        updateHeaderScroll();
        siteScroll.addEventListener('scroll', updateHeaderScroll, { passive: true });
    }

    document.addEventListener('click', function (event) {
        if (!header || !header.classList.contains('site-header--open')) return;
        if (header.contains(event.target)) return;
        closeMenu();
    });
})();
