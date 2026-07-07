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

    function getTheme() {
        return root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    }

    function updateToggleButtons(theme) {
        const isDark = theme === 'dark';
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
            btn.setAttribute('aria-label', isDark ? 'Светлая тема' : 'Тёмная тема');
            const icon = btn.querySelector('.theme-toggle__icon');
            if (icon) {
                icon.textContent = isDark ? '☀' : '☾';
            }
        });
    }

    function applyTheme(theme) {
        const next = theme === 'dark' ? 'dark' : 'light';
        root.setAttribute('data-theme', next);
        try {
            localStorage.setItem(STORAGE_KEY, next);
        } catch {
            /* ignore */
        }
        updateToggleButtons(next);
    }

    window.GSTheme = {
        get: getTheme,
        set: applyTheme,
        toggle: function () {
            applyTheme(getTheme() === 'dark' ? 'light' : 'dark');
        },
    };

    updateToggleButtons(getTheme());

    document.addEventListener('DOMContentLoaded', function () {
        updateToggleButtons(getTheme());
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                window.GSTheme.toggle();
            });
        });
    });
})();
