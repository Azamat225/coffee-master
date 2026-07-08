(function () {
    const STORAGE_KEY = 'gs-panel-theme';
    const root = document.documentElement;
    const btn = document.getElementById('panelThemeToggle');
    if (!btn) return;

    function applyTheme(theme) {
        const next = theme === 'light' ? 'light' : 'dark';
        root.dataset.panelTheme = next;
        try {
            localStorage.setItem(STORAGE_KEY, next);
        } catch (e) {}

        const isLight = next === 'light';
        btn.setAttribute('aria-pressed', isLight ? 'true' : 'false');
        btn.textContent = isLight ? 'Тема: светлая' : 'Тема: тёмная';
    }

    function readTheme() {
        try {
            const t = localStorage.getItem(STORAGE_KEY);
            return t === 'light' ? 'light' : 'dark';
        } catch (e) {
            return 'dark';
        }
    }

    // Если inline script уже выставил dataset — подхватим.
    const initial = root.dataset.panelTheme || readTheme();
    applyTheme(initial);

    btn.addEventListener('click', function () {
        const cur = (root.dataset.panelTheme === 'light') ? 'light' : 'dark';
        applyTheme(cur === 'light' ? 'dark' : 'light');
    });
})();

