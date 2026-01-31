from django.contrib import admin

from .models import Coupon, Person, VoucherScan


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "id_number", "phone", "birth_date")
    search_fields = ("first_name", "last_name", "id_number")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "person", "source", "scanned_at")
    list_filter = ("source", "scanned_at")
    search_fields = ("code", "person__first_name", "person__last_name", "person__id_number")


@admin.register(VoucherScan)
class VoucherScanAdmin(admin.ModelAdmin):
    list_display = ("code", "person", "source", "room_id", "scanned_at")
    list_filter = ("source", "room_id", "scanned_at")
    search_fields = (
        "code",
        "person__first_name",
        "person__last_name",
        "person__id_number",
    )
