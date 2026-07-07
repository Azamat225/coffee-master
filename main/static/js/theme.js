(function () {
    const STORAGE_KEY = 'gs-theme';
    const root = document.documentElement;

    function getStoredTheme() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch {
            return null;
        }
    }

    function applyTheme(theme) {
        const next = theme === 'dark' ? 'dark' : 'light';
        root.setAttribute('data-theme', next);
        try {
            localStorage.setItem(STORAGE_KEY, next);
        } catch {
            /* ignore */
        }
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            const isDark = next === 'dark';
            btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
            btn.setAttribute('aria-label', isDark ? 'Светлая тема' : 'Тёмная тема');
            const icon = btn.querySelector('.theme-toggle__icon');
            if (icon) {
                icon.textContent = isDark ? '☀' : '☾';
            }
        });
    }

    window.GSTheme = {
        get: function () {
            return root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
        },
        set: applyTheme,
        toggle: function () {
            applyTheme(this.get() === 'dark' ? 'light' : 'dark');
        },
    };

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                window.GSTheme.toggle();
            });
        });
    });
})();
