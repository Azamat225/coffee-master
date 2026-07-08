(function () {
    const STORAGE_KEY = 'gs-theme';
    const root = document.documentElement;
    const body = document.body;

    function getTheme() {
        return root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    }

    function updateToggles(theme) {
        const isDark = theme === 'dark';
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
            btn.setAttribute('aria-label', isDark ? 'Включить светлую тему' : 'Включить тёмную тему');
            btn.classList.toggle('is-dark', isDark);
        });
    }

    function applyTheme(theme) {
        const next = theme === 'dark' ? 'dark' : 'light';

        root.setAttribute('data-theme', next);
        root.style.colorScheme = next;

        if (body) {
            body.classList.remove('theme-light', 'theme-dark');
            body.classList.add(next === 'dark' ? 'theme-dark' : 'theme-light');
        }

        var meta = document.querySelector('meta[name="color-scheme"]');
        if (meta) meta.setAttribute('content', next);

        try {
            localStorage.setItem(STORAGE_KEY, next);
        } catch (e) {
            /* ignore */
        }

        updateToggles(next);
        window.dispatchEvent(new CustomEvent('gs-theme-change', { detail: { theme: next } }));
    }

    window.GSTheme = {
        get: getTheme,
        set: applyTheme,
        toggle: function () {
            applyTheme(getTheme() === 'dark' ? 'light' : 'dark');
        },
    };

    applyTheme(getTheme());

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                window.GSTheme.toggle();
            });
        });
    });
})();
