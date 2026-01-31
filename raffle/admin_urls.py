from django.urls import path

from .controllers import admin as views


app_name = "raffle_admin"

urlpatterns = [
    path("", views.admin_dashboard, name="dashboard"),
    path("login/", views.admin_login, name="login"),
    path("logout/", views.admin_logout, name="logout"),
    path("password/change/", views.cashier_password_change, name="password_change"),
    path("sala/", views.room_dashboard, name="room_dashboard"),
    path("ingreso/", views.staff_entry, name="staff_entry"),
    path("registrar/", views.staff_register, name="staff_register"),
    path("ingreso-manual/", views.manual_entry, name="manual_entry"),
    path("ingreso-manual/listado/", views.manual_list, name="manual_list"),
    path("coupons/", views.admin_coupons, name="coupons"),
    path("coupons/export/", views.admin_coupons_export, name="coupons_export"),
    path("coupons/<int:coupon_id>/print/", views.admin_print_coupon, name="print_coupon"),
    path(
        "coupons/<int:coupon_id>/reprint/",
        views.room_reprint_coupon,
        name="room_reprint_coupon",
    ),
    path("reprints/", views.admin_reprints, name="reprints"),
    path("configuration/", views.admin_configuration, name="configuration"),
    path(
        "configuration/printers/",
        views.admin_configuration_printers,
        name="configuration_printers",
    ),
    path(
        "configuration/normalize-participants/",
        views.admin_normalize_participants,
        name="normalize_participants",
    ),
    path("api-test/", views.admin_api_test, name="api_test"),
    path("clear-database/", views.admin_clear_database, name="clear_database"),
]
