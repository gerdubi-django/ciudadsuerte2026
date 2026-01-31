(function () {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.AdminUI) { return; }
        const state = window.AdminUI.getState();

        const animationToggle = document.querySelector('[data-preference-toggle="animations"]');
        const shortcutsToggle = document.querySelector('[data-preference-toggle="shortcuts"]');
        const densityButtons = document.querySelectorAll('[data-density]');
        const themeSelect = document.querySelector('[data-theme-select]');
        const contrastToggle = document.querySelector('[data-theme-contrast]');
        const usbButton = document.querySelector('[data-usb-refresh]');
        const usbStatus = document.querySelector('[data-usb-status]');
        const usbTable = document.querySelector('[data-usb-table]');
        const usbResults = document.querySelector('[data-usb-results]');
        const tabButtons = document.querySelectorAll('[data-tab-target]');
        const tabPanels = document.querySelectorAll('[data-tab-panel]');
        const roomFormset = document.querySelector('[data-room-formset]');
        const roomForms = document.querySelector('[data-room-forms]');
        const addRoomButton = document.querySelector('[data-add-room]');
        const roomTemplate = document.querySelector('[data-room-empty-form]');

        if (tabButtons.length) {
            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    setActiveTab(button.dataset.tabTarget);
                });
            });
        }

        if (animationToggle) {
            animationToggle.checked = Boolean(state.animations);
            animationToggle.addEventListener('change', event => {
                window.AdminUI.setAnimations(event.target.checked);
            });
        }

        if (shortcutsToggle) {
            shortcutsToggle.checked = Boolean(state.shortcuts);
            shortcutsToggle.addEventListener('change', event => {
                window.AdminUI.setShortcuts(event.target.checked);
            });
        }

        if (densityButtons.length) {
            densityButtons.forEach(button => {
                if (button.dataset.density === state.density) {
                    button.classList.add('is-active');
                } else {
                    button.classList.remove('is-active');
                }
                button.addEventListener('click', () => {
                    densityButtons.forEach(item => item.classList.remove('is-active'));
                    button.classList.add('is-active');
                    window.AdminUI.setDensity(button.dataset.density);
                });
            });
        }

        if (themeSelect) {
            // Sync the stored theme with the new selector control.
            themeSelect.value = state.theme;
            themeSelect.addEventListener('change', event => {
                const nextTheme = event.target.value === 'dark' ? 'dark' : 'light';
                window.AdminUI.setTheme(nextTheme);
            });
            document.addEventListener('admin:theme-change', event => {
                const next = event.detail?.theme;
                if (!next) { return; }
                themeSelect.value = next;
            });
        }

        if (contrastToggle) {
            contrastToggle.checked = Boolean(state.contrast);
            contrastToggle.addEventListener('change', event => {
                window.AdminUI.setContrast(event.target.checked);
            });
        }

        if (usbButton && usbStatus) {
            const endpoint = usbButton.dataset.usbEndpoint;
            usbButton.addEventListener('click', () => {
                if (!endpoint) { return; }
                // Provide instant feedback before launching the USB scan.
                usbButton.disabled = true;
                usbButton.textContent = 'Buscando…';
                updateUsbStatus('Escaneando dispositivos conectados…');
                fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': readCsrfToken(),
                        'Accept': 'application/json'
                    }
                })
                    .then(response => response.json().then(data => ({ ok: response.ok, data })))
                    .then(({ ok, data }) => {
                        if (!ok) {
                            updateUsbStatus('No se pudo completar el escaneo.', true);
                            return;
                        }
                        renderUsbResults(data.usb_devices || []);
                        updateUsbStatus(
                            data.usb_devices && data.usb_devices.length
                                ? `Se detectaron ${data.usb_devices.length} dispositivo(s) conectado(s).`
                                : 'No se encontraron dispositivos USB disponibles.',
                            false
                        );
                    })
                    .catch(() => {
                        updateUsbStatus('No se pudo completar el escaneo.', true);
                    })
                    .finally(() => {
                        usbButton.disabled = false;
                        usbButton.textContent = 'Buscar dispositivos USB';
                    });
            });
        }

        // Update the USB helper banner status text and tone.
        function updateUsbStatus(message, isError = false) {
            if (!usbStatus) { return; }
            usbStatus.textContent = message;
            usbStatus.classList.toggle('admin-usb-status--error', Boolean(isError));
        }

        // Render the USB table rows dynamically after each scan.
        function renderUsbResults(devices) {
            if (!usbResults || !usbTable) { return; }
            usbResults.innerHTML = '';
            if (!devices.length) {
                usbTable.hidden = true;
                return;
            }
            devices.forEach(device => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${device.manufacturer || ''}</td>
                    <td>${device.name || ''}</td>
                    <td>${device.vendor_id || ''}</td>
                    <td>${device.product_id || ''}</td>
                `;
                usbResults.appendChild(row);
            });
            usbTable.hidden = false;
        }

        // Retrieve the CSRF token so Django accepts the POST request.
        function readCsrfToken() {
            const match = document.cookie.match(/csrftoken=([^;]+)/);
            return match ? decodeURIComponent(match[1]) : '';
        }

        function setActiveTab(target) {
            if (!target) { return; }
            tabButtons.forEach(button => {
                button.classList.toggle('is-active', button.dataset.tabTarget === target);
            });
            tabPanels.forEach(panel => {
                panel.hidden = panel.dataset.tabPanel !== target;
            });
        }

        if (roomFormset && roomForms && addRoomButton && roomTemplate) {
            const totalFormsInput = roomFormset.querySelector('input[name="rooms-TOTAL_FORMS"]');
            addRoomButton.addEventListener('click', () => {
                if (!totalFormsInput) { return; }
                const formIndex = parseInt(totalFormsInput.value, 10) || 0;
                const wrapper = document.createElement('div');
                wrapper.innerHTML = roomTemplate.innerHTML.replace(/__prefix__/g, formIndex).trim();
                const newForm = wrapper.firstElementChild;
                if (newForm) {
                    roomForms.appendChild(newForm);
                    totalFormsInput.value = formIndex + 1;
                }
            });
        }
    });
})();
