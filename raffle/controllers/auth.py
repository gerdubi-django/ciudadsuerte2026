from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse


UserModel = get_user_model()


def user_is_administrator(user) -> bool:
    # Check whether the user belongs to the administrator role.
    return bool(user and user.is_authenticated and user.is_admin())


def user_is_operator(user) -> bool:
    # Check whether the user can access the operator panel.
    return bool(user and user.is_authenticated and user.has_operator_access)


def admin_required(view_func):
    # Compose authentication and authorization checks for admin views.
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = f"{reverse('raffle_admin:login')}?next={request.path}"
            return redirect(login_url)
        if not user_is_administrator(request.user):
            messages.error(request, "No posee permisos para acceder al panel.")
            return redirect("raffle_admin:login")
        return view_func(request, *args, **kwargs)

    return wrapped_view


def staff_required(view_func):
    # Ensure the view is accessed by authenticated users.
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = f"{reverse('raffle_admin:login')}?next={request.path}"
            return redirect(login_url)
        if not user_is_operator(request.user):
            messages.error(request, "No posee permisos para acceder a esta sección.")
            return redirect("raffle_admin:login")
        return view_func(request, *args, **kwargs)

    return wrapped_view
