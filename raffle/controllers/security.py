from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from .admin import _admin_context


def csrf_failure(request, reason="", template_name="raffle/csrf_failure.html"):
    # Redirect unauthenticated users to login when CSRF fails.
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        messages.error(request, _("La sesión expiró. Inicie sesión nuevamente."))
        login_url = f"{reverse('raffle_admin:login')}?next={request.path}"
        return redirect(login_url)

    context = _admin_context({"reason": reason}, user=request.user)
    return render(request, template_name, context, status=403)
