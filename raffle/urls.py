from django.urls import path

from . import views

app_name = "raffle"

urlpatterns = [
    path("", views.home, name="home"),
    path("registrar/", views.register, name="register"),
    path("configurar-terminal/", views.configure_terminal, name="configure_terminal"),
    path("ingresar/validar/", views.validate_entry_voucher, name="entry_validate"),
    path("ingresar/", views.entry, name="entry"),
    path("api/persona/", views.person_lookup, name="person_lookup"),
]
