(function () {
    document.addEventListener('DOMContentLoaded', () => {
        const table = document.querySelector('[data-staff-table]');
        const searchInput = document.querySelector('[data-staff-search]');
        const feedback = document.querySelector('[data-staff-feedback]');
        if (!table) { return; }

        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const csrfToken = readCsrfToken();

        table.addEventListener('click', event => {
            const button = event.target.closest('[data-reprint]');
            if (!button) { return; }
            const url = button.dataset.url;
            if (!url || !csrfToken) { return; }
            button.disabled = true;
            const original = button.textContent;
            button.textContent = 'Enviando…';
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Accept': 'application/json'
                }
            })
                .then(response => response.json().then(data => ({ ok: response.ok, data })))
                .then(({ ok, data }) => {
                    displayFeedback(data.message || 'Acción completada.', !ok);
                    if (ok) {
                        button.replaceWith(createStatusBadge());
                    } else {
                        button.disabled = false;
                        button.textContent = original;
                    }
                })
                .catch(() => {
                    displayFeedback('No se pudo completar la reimpresión.', true);
                    button.disabled = false;
                    button.textContent = original;
                });
        });

        if (searchInput) {
            searchInput.addEventListener('input', () => {
                applyFilter(searchInput.value || '');
            });
        }

        function applyFilter(query) {
            const needle = query.trim().toLowerCase();
            rows.forEach(row => {
                const haystack = [row.dataset.code, row.dataset.person, row.dataset.email, row.dataset.dni]
                    .join(' ')
                    .toLowerCase();
                row.style.display = haystack.includes(needle) ? '' : 'none';
            });
        }

        function readCsrfToken() {
            const match = document.cookie.match(/csrftoken=([^;]+)/);
            return match ? decodeURIComponent(match[1]) : '';
        }

        function displayFeedback(message, isError) {
            if (!feedback) { return; }
            feedback.textContent = message;
            feedback.hidden = false;
            feedback.classList.toggle('admin-inline-feedback--error', Boolean(isError));
        }

        function createStatusBadge() {
            const badge = document.createElement('span');
            badge.className = 'admin-chip';
            badge.textContent = 'Reimpreso';
            return badge;
        }
    });
})();
