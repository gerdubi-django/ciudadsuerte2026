(function () {
    const storageKeys = {
        theme: 'adminTheme',
        contrast: 'adminThemeContrast',
        density: 'adminDensity',
        animations: 'adminAnimations',
        shortcuts: 'adminShortcuts'
    };

    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    const htmlTheme = (document.documentElement.dataset.theme || '').toLowerCase();
    const storedTheme = readStorage(storageKeys.theme);
    const resolvedHtmlTheme = htmlTheme === 'dark' ? 'dark' : (htmlTheme === 'light' ? 'light' : null);
    const fallbackTheme = prefersDark.matches ? 'dark' : 'light';

    const state = {
        theme: resolvedHtmlTheme || storedTheme || fallbackTheme,
        contrast: readStorage(storageKeys.contrast) === 'true',
        density: readStorage(storageKeys.density) || 'comfortable',
        animations: readStorage(storageKeys.animations) !== 'false',
        shortcuts: readStorage(storageKeys.shortcuts) !== 'false'
    };

    const root = document.documentElement;
    const body = document.body;
    const layoutShell = document.querySelector('.admin-shell');
    const sidebar = document.querySelector('[data-admin-sidebar]');
    const sidebarScrim = document.querySelector('[data-sidebar-scrim]');
    const sidebarToggles = document.querySelectorAll('[data-sidebar-toggle]');
    const sidebarLinks = document.querySelectorAll('.admin-sidebar__link');
    const themeTrigger = document.querySelector('[data-theme-trigger]');

    applyTheme(state.theme);
    applyContrast(state.contrast);
    applyDensity(state.density);
    applyAnimations(state.animations);
    applyShortcuts(state.shortcuts);

    if (resolvedHtmlTheme && storedTheme !== resolvedHtmlTheme) {
        writeStorage(storageKeys.theme, resolvedHtmlTheme);
    }

    if (prefersDark.addEventListener) {
        prefersDark.addEventListener('change', event => {
            if (!localStorage.getItem(storageKeys.theme)) {
                setTheme(event.matches ? 'dark' : 'light');
            }
        });
    }

    if (sidebarToggles.length && sidebar) {
        sidebarToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                toggleSidebar();
            });
        });
    }

    if (sidebarScrim && sidebar) {
        sidebarScrim.addEventListener('click', () => {
            toggleSidebar(false);
        });
    }

    if (sidebarLinks.length) {
        sidebarLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.matchMedia('(max-width: 1024px)').matches) {
                    toggleSidebar(false);
                }
            });
        });
    }

    if (themeTrigger) {
        themeTrigger.addEventListener('click', () => {
            const nextTheme = state.theme === 'dark' ? 'light' : 'dark';
            setTheme(nextTheme);
        });
    }

    document.addEventListener('keyup', event => {
        if (event.key === 'Escape' && sidebar && sidebar.classList.contains('is-open')) {
            toggleSidebar(false);
        }
    });

    window.AdminUI = {
        setTheme,
        setContrast,
        setDensity,
        setAnimations,
        setShortcuts,
        getState: () => ({ ...state })
    };

    function setTheme(theme) {
        state.theme = theme === 'dark' ? 'dark' : 'light';
        applyTheme(state.theme);
        writeStorage(storageKeys.theme, state.theme);
        document.dispatchEvent(new CustomEvent('admin:theme-change', { detail: { theme: state.theme } }));
    }

    function setContrast(enabled) {
        state.contrast = Boolean(enabled);
        applyContrast(state.contrast);
        writeStorage(storageKeys.contrast, state.contrast);
    }

    function setDensity(level) {
        state.density = level === 'compact' ? 'compact' : 'comfortable';
        applyDensity(state.density);
        writeStorage(storageKeys.density, state.density);
    }

    function setAnimations(enabled) {
        state.animations = Boolean(enabled);
        applyAnimations(state.animations);
        writeStorage(storageKeys.animations, state.animations);
    }

    function setShortcuts(enabled) {
        state.shortcuts = Boolean(enabled);
        applyShortcuts(state.shortcuts);
        writeStorage(storageKeys.shortcuts, state.shortcuts);
    }

    function applyTheme(theme) {
        root.dataset.theme = theme === 'dark' ? 'dark' : 'light';
    }

    function toggleSidebar(force) {
        if (!sidebar) { return; }
        const isOpen = typeof force === 'boolean' ? force : !sidebar.classList.contains('is-open');
        sidebar.classList.toggle('is-open', isOpen);
        body.classList.toggle('admin-sidebar-open', isOpen);
        if (layoutShell) {
            layoutShell.classList.toggle('admin-shell--sidebar', isOpen);
        }
        if (sidebarScrim) {
            sidebarScrim.classList.toggle('is-visible', isOpen);
        }
        if (sidebarToggles.length) {
            sidebarToggles.forEach(toggle => {
                toggle.setAttribute('aria-expanded', String(isOpen));
            });
        }
    }

    function applyContrast(enabled) {
        body.classList.toggle('admin-contrast', Boolean(enabled));
    }

    function applyDensity(level) {
        body.classList.toggle('admin-density-compact', level === 'compact');
    }

    function applyAnimations(enabled) {
        body.classList.toggle('admin-no-animations', !enabled);
    }

    function applyShortcuts(enabled) {
        body.classList.toggle('admin-hide-shortcuts', !enabled);
    }

    function readStorage(key) {
        try {
            return window.localStorage.getItem(key);
        } catch (error) {
            console.warn('Storage read failed', error);
            return null;
        }
    }

    function writeStorage(key, value) {
        try {
            window.localStorage.setItem(key, String(value));
        } catch (error) {
            console.warn('Storage write failed', error);
        }
    }
})();
