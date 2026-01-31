(function () {
    // Manage the registration workflow without requiring voucher scanning.
    const STATUS_SUCCESS = "Voucher virtual asignado correctamente.";
    const STATUS_ERROR = "Complete los datos requeridos antes de registrar.";

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("[data-register-form]").forEach(form => {
            const trigger = form.querySelector("[data-register-trigger]");
            const status = form.querySelector("[data-register-status]");
            const voucherInput = form.querySelector('input[name="voucher_code"]');
            if (!trigger || !voucherInput) {
                return;
            }

            // Update the helper message displayed below the submit button.
            const updateStatus = (message, isError = false) => {
                if (!status) {
                    return;
                }
                status.textContent = message;
                status.classList.toggle("scanner-status--error", Boolean(isError));
            };

            // Generate a unique voucher code for the registration flow.
            const createVoucherCode = () => {
                if (window.crypto && typeof window.crypto.randomUUID === "function") {
                    return window.crypto.randomUUID();
                }
                const random = Math.random().toString(36).slice(2, 8).toUpperCase();
                return `REG-${Date.now()}-${random}`;
            };

            // Submit the form once all fields are valid and the code is ready.
            trigger.addEventListener("click", () => {
                const isValid = typeof form.reportValidity === "function" ? form.reportValidity() : form.checkValidity();
                if (!isValid) {
                    updateStatus(STATUS_ERROR, true);
                    return;
                }
                voucherInput.value = createVoucherCode().toUpperCase();
                updateStatus(STATUS_SUCCESS, false);
                if (typeof form.requestSubmit === "function") {
                    form.requestSubmit();
                } else {
                    form.submit();
                }
            });
        });
    });
})();
