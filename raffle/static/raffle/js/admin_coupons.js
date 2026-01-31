(function () {
    document.addEventListener('DOMContentLoaded', () => {
        const table = document.querySelector('[data-coupon-table]');
        if (!table) { return; }

        const resetButton = document.querySelector('[data-reset-filters]');

        // Display status updates for asynchronous operations.
        const feedback = document.querySelector('[data-coupon-feedback]');
        // Obtain the CSRF token required by Django for POST requests.
        const csrfToken = readCsrfToken();

        if (resetButton) {
            resetButton.addEventListener('click', () => {
                window.location.assign(window.location.pathname);
            });
        }

        table.addEventListener('click', event => {
            const button = event.target.closest('[data-print-coupon]');
            if (!button) { return; }
            printCoupon(button);
        });

        // Send the coupon data to the backend printer endpoint.
        function printCoupon(button) {
            const url = button.dataset.printUrl;
            if (!url || !csrfToken) {
                displayFeedback('No se pudo iniciar la impresión.', true);
                return;
            }
            const originalLabel = button.textContent;
            button.disabled = true;
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
                    displayFeedback(data.message || 'Cupón enviado.', !ok);
                    button.textContent = ok ? 'Impreso' : 'Reintentar';
                    window.setTimeout(() => {
                        button.textContent = originalLabel;
                        button.disabled = false;
                    }, 1400);
                })
                .catch(() => {
                    displayFeedback('No se pudo enviar el cupón a la impresora.', true);
                    button.textContent = 'Reintentar';
                    window.setTimeout(() => {
                        button.textContent = originalLabel;
                        button.disabled = false;
                    }, 1400);
                });
        }

        // Show helper feedback messages within the listing view.
        function displayFeedback(message, isError) {
            if (!feedback) { return; }
            feedback.textContent = message;
            feedback.hidden = false;
            feedback.classList.toggle('admin-inline-feedback--error', Boolean(isError));
        }

        // Read the csrf token from the browser cookies.
        function readCsrfToken() {
            const match = document.cookie.match(/csrftoken=([^;]+)/);
            return match ? decodeURIComponent(match[1]) : null;
        }
    });
})();
