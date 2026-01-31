(function () {
    const STATUS = {
        ready: "Lector activo. Escanea el voucher.",
        error: "No se detectó un voucher. Intenta nuevamente.",
        processing: "Validando voucher con la sala...",
        confirm: "Cupón Generado Correctamente",
        searching: "Buscando participante registrado...",
        invalidVoucher: "Cupón No Pertenece a la Sala",
    };

    const setStatus = (el, msg, state) => {
        el.className = "scanner-status";
        if (state) el.classList.add(`scanner-status--${state}`);
        el.textContent = msg;
    };

    document.addEventListener("DOMContentLoaded", () => {
        const form = document.querySelector("[data-entry-form]");
        if (!form) return;

        const trigger = form.querySelector("[data-scan-trigger]");
        const captureInput = form.querySelector("[data-scan-capture]");
        const hiddenInput = form.querySelector('input[name="voucher_code"]');
        const status = form.querySelector("[data-scan-status]");
        const idInput = form.querySelector('input[name="id_number"]');
        const registerUrl = form.dataset.registerUrl;
        const personLookupUrl = form.dataset.personLookupUrl;
        const validationUrl = form.dataset.validationUrl;
        const persistedStatus = form.dataset.scanStatusContent;
        const csrfToken =
            form.querySelector('input[name="csrfmiddlewaretoken"]')?.value || "";
        let reading = false;
        let buffer = "";
        let timeout = null;

        const redirectToRegister = () => {
            window.location.href = registerUrl || "/registrar/";
        };

        const fetchPersonById = async (idNumber) => {
            if (!personLookupUrl) return null;

            const response = await fetch(
                `${personLookupUrl}?id_number=${encodeURIComponent(idNumber)}`,
                { headers: { Accept: "application/json" } }
            ).catch(() => null);

            if (!response || response.status === 404) return null;
            if (!response.ok) return null;

            return response.json().catch(() => null);
        };

        const resetCapture = () => {
            buffer = "";
            captureInput.value = "";
            hiddenInput.value = "";
        };

        const finishScan = () => {
            const code = buffer.replace(/\r?\n/g, "").trim();
            if (!code) {
                setStatus(status, STATUS.error, "error");
                trigger.disabled = false;
                return;
            }
            hiddenInput.value = code.toUpperCase();
            setStatus(status, STATUS.processing, "info");
            trigger.disabled = true;

            validateVoucher(hiddenInput.value)
                .then((validation) => {
                    if (!validation.valid) {
                        setStatus(
                            status,
                            validation.message || STATUS.invalidVoucher,
                            "error"
                        );
                        trigger.disabled = false;
                        return;
                    }

                    setStatus(
                        status,
                        validation.message || STATUS.confirm,
                        "success"
                    );
                    trigger.disabled = false;
                    form.submit();
                })
                .catch(() => {
                    setStatus(status, STATUS.invalidVoucher, "error");
                    trigger.disabled = false;
                });
        };

        const validateVoucher = async (code) => {
            if (!validationUrl) {
                return { valid: true, message: STATUS.confirm };
            }

            const headers = csrfToken ? { "X-CSRFToken": csrfToken } : {};
            const body = new FormData();
            body.append("voucher_code", code);

            try {
                const response = await fetch(validationUrl, {
                    method: "POST",
                    headers,
                    body,
                });
                const data = await response.json().catch(() => null);

                if (!response.ok) {
                    return {
                        valid: false,
                        message: data?.message || STATUS.invalidVoucher,
                    };
                }

                return {
                    valid: Boolean(data?.valid),
                    message: data?.message || STATUS.confirm,
                };
            } catch (err) {
                return { valid: false, message: STATUS.invalidVoucher };
            }
        };

        const beginScan = async () => {
            resetCapture();
            const idNumber = (idInput?.value || "").trim();
            if (!idNumber) {
                redirectToRegister();
                return;
            }

            setStatus(status, STATUS.searching, "info");
            trigger.disabled = true;

            const person = await fetchPersonById(idNumber);
            if (!person) {
                trigger.disabled = false;
                redirectToRegister();
                return;
            }

            const readyMessage = person.fullName
                ? `${person.fullName}. Escanea el voucher.`
                : STATUS.ready;
            setStatus(status, readyMessage, "info");
            reading = true;
            captureInput.style.opacity = "0.1";
            captureInput.style.zIndex = "10";
            captureInput.focus();
            setTimeout(() => {
                captureInput.style.opacity = "0";
                captureInput.style.zIndex = "-1";
            }, 600);
        };

        captureInput.addEventListener("input", (e) => {
            if (!reading) return;
            buffer += e.data || "";
            clearTimeout(timeout);
            // wait 100 ms without new characters -> completed read
            timeout = setTimeout(() => {
                reading = false;
                finishScan();
            }, 100);
        });

        trigger.addEventListener("click", (e) => {
            e.preventDefault();
            beginScan();
        });

        form.addEventListener("submit", () => {
            setStatus(status, STATUS.confirm, "success");
            trigger.disabled = true;
            setTimeout(() => (window.location.href = "/"), 3000);
        });

        if (persistedStatus) {
            const state =
                persistedStatus === STATUS.confirm ? "success" : "error";
            setStatus(status, persistedStatus, state);
        }

        if (idInput) idInput.focus();
    });
})();
