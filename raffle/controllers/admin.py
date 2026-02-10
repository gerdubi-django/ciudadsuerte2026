from datetime import datetime, time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.forms import PasswordChangeForm
from django.db import IntegrityError, transaction
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from ..forms import (
    AdminLoginForm,
    AdminUserDeleteForm,
    AdminUserForm,
    EntryForm,
    ManualCouponForm,
    ManualPendingFilterForm,
    LocalPrinterConfigForm,
    PrinterConfigurationForm,
    RoomForm,
    CashierRegistrationForm,
    RegistrationForm,
    SystemSettingsForm,
    TerminalConfigForm,
    VoucherAPITestForm,
)
from ..models import (
    Coupon,
    CouponReprint,
    CouponReprintLog,
    CouponSequence,
    ManualCouponSequence,
    Person,
    PrinterConfiguration,
    Room,
    SystemSettings,
    VoucherScan,
)
from ..rooms import RoomDirectory
from ..services import (
    EntryValidationError,
    available_printers,
    build_coupon_report_workbook,
    build_daily_report_workbook,
    build_room_report_workbook,
    create_coupons,
    create_manual_coupon,
    get_coupon_room_summary,
    get_or_create_printer_configuration,
    get_or_create_system_settings,
    print_coupon_backend,
    register_reprint,
    render_workbook_response,
    validate_entry_rules,
)
from ..utils.terminal import get_terminal_config, save_terminal_config
from ..utils.terms import get_terms_text, save_terms_config
from utils.printers import pyusb_available
from .auth import admin_required, cashier_required, staff_required, user_is_administrator


UserModel = get_user_model()


# -----------------------------------------------------------------------------
# CONTEXTO COMPARTIDO DEL PANEL ADMIN
# -----------------------------------------------------------------------------

def _admin_context(
    context: dict | None = None,
    configuration: PrinterConfiguration | None = None,
    system_settings: SystemSettings | None = None,
    user=None,
) -> dict:
    configuration = configuration or get_or_create_printer_configuration()
    system_settings = system_settings or get_or_create_system_settings()[0]
    payload: dict = {}

    if context:
        payload.update(context)

    payload.setdefault("configuration", configuration)
    payload.setdefault("system_settings", system_settings)
    payload.setdefault(
        "theme_preference", system_settings.theme_preference or configuration.theme_preference
    )
    payload.setdefault("theme_choices", SystemSettings.ThemePreference.choices)
    payload.setdefault("dashboard_role", _get_dashboard_role(user))
    payload.setdefault("active_user", user)
    payload.setdefault("terminal_config", get_terminal_config())

    return payload


def _get_dashboard_role(user) -> str:
    # Pick a palette scope based on the authenticated user role.
    if user and getattr(user, "is_authenticated", False):
        if user.is_admin():
            return "admin"
        if user.is_floor_manager:
            return "manager"
        return "operator"
    return "guest"


SESSION_ROOM_KEY = "active_room_id"


def _get_active_room_id(request, system_settings: SystemSettings) -> int:
    # Resolve the room stored in session or fallback to the terminal setting.
    valid_rooms = {room[0] for room in RoomDirectory.choices()}
    try:
        session_room = int(request.session.get(SESSION_ROOM_KEY))
    except (TypeError, ValueError):
        session_room = None
    if session_room in valid_rooms:
        return session_room
    request.session[SESSION_ROOM_KEY] = system_settings.current_room_id
    return system_settings.current_room_id


def _set_active_room(request, room_id: int, system_settings: SystemSettings) -> int:
    # Persist the selected room in the user session when valid.
    valid_rooms = {room[0] for room in RoomDirectory.choices()}
    selected_room = room_id if room_id in valid_rooms else system_settings.current_room_id
    request.session[SESSION_ROOM_KEY] = selected_room
    return selected_room


def _get_terminal_label(system_settings: SystemSettings) -> str:
    # Provide a readable terminal label using local config when available.
    config = get_terminal_config() or {}
    label = str(config.get("terminal_id", "")).strip() or system_settings.terminal_name
    return label


def _terminal_config_or_redirect(request):
    # Enforce local terminal configuration before continuing staff operations.
    config = get_terminal_config()
    if config is None:
        messages.error(request, "Configure la terminal local antes de continuar.")
        return None, redirect(reverse("raffle:configure_terminal"))
    return config, None


# -----------------------------------------------------------------------------
# LOGIN / LOGOUT
# -----------------------------------------------------------------------------

def admin_login(request):
    system_settings, _ = get_or_create_system_settings()
    active_room_id = _get_active_room_id(request, system_settings)
    if request.user.is_authenticated and user_is_administrator(request.user):
        return redirect("raffle_admin:dashboard")

    post_data = request.POST or None
    if request.method == "POST":
        initial_room_id = request.POST.get("room_id") or 0
        mutable = post_data.copy()
        mutable["room_id"] = str(initial_room_id)
        post_data = mutable

    form = AdminLoginForm(
        request=request,
        data=request.POST or None,
        initial={"room_id": active_room_id},
    )
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        selected_room = form.cleaned_data.get("room_id")
        if selected_room is not None:
            _set_active_room(request, selected_room, system_settings)

        if user_is_administrator(user):
            messages.success(request, "Bienvenido al panel de administración.")
            return redirect(next_url or "raffle_admin:dashboard")

        messages.success(request, "Inicio de sesión exitoso.")
        return redirect(next_url or "raffle_admin:room_dashboard")

    return render(request, "raffle/admin_login.html", {"form": form, "next": next_url})


@admin_required
def admin_logout(request):
    logout(request)
    messages.success(request, "Sesión finalizada correctamente.")
    return redirect("raffle_admin:login")


@staff_required
def cashier_password_change(request):
    if not request.user.is_cashier:
        messages.error(request, "Solo los cambistas pueden acceder a esta opción.")
        return redirect("raffle_admin:dashboard")

    form = PasswordChangeForm(request.user, request.POST or None)
    for field in form.fields.values():
        field.widget.attrs.update({"class": "admin-input"})

    if request.method == "POST" and form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        messages.success(request, "Contraseña actualizada correctamente.")
        return redirect("raffle_admin:password_change")

    context = _admin_context({"form": form}, user=request.user)
    return render(request, "raffle/password_change.html", context)


# -----------------------------------------------------------------------------
# DASHBOARD PRINCIPAL
# -----------------------------------------------------------------------------

@admin_required
def admin_dashboard(request):
    system_settings, _ = get_or_create_system_settings()
    coupon_qs = Coupon.objects.select_related("person")
    voucher_qs = VoucherScan.objects.select_related("person")
    reprint_logs = CouponReprintLog.objects.values(
        "user_id", "user__username", "user__first_name", "user__last_name"
    )

    selected_room = request.GET.get("room")
    selected_source = request.GET.get("source")
    date_start_param = request.GET.get("date_start")
    date_end_param = request.GET.get("date_end")

    selected_terminal = (request.GET.get("terminal") or "").strip()

    # FILTRO DE SALA
    room_id = int(selected_room) if selected_room and selected_room.isdigit() else None
    if room_id:
        coupon_qs = coupon_qs.filter(room_id=room_id)
        voucher_qs = voucher_qs.filter(room_id=room_id)
        reprint_logs = reprint_logs.filter(room_id=room_id)

    if selected_terminal:
        coupon_qs = coupon_qs.filter(terminal_name=selected_terminal)
        voucher_qs = voucher_qs.filter(terminal_name=selected_terminal)
        reprint_logs = reprint_logs.filter(coupon__terminal_name=selected_terminal)

    # FILTRO DE FUENTE
    valid_sources = {choice[0] for choice in Coupon.SOURCE_CHOICES}
    source_value = selected_source if selected_source in valid_sources else None
    if source_value:
        coupon_qs = coupon_qs.filter(source=source_value)
        voucher_qs = voucher_qs.filter(source=source_value)

    # FILTRO DE FECHAS
    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None

    start_date = _parse_date(date_start_param)
    end_date = _parse_date(date_end_param)
    current_tz = timezone.get_current_timezone()

    if start_date:
        dt = timezone.make_aware(datetime.combine(start_date, time.min), current_tz)
        coupon_qs = coupon_qs.filter(scanned_at__gte=dt)
        voucher_qs = voucher_qs.filter(scanned_at__gte=dt)

    if end_date:
        dt = timezone.make_aware(datetime.combine(end_date, time.max), current_tz)
        coupon_qs = coupon_qs.filter(scanned_at__lte=dt)
        voucher_qs = voucher_qs.filter(scanned_at__lte=dt)

    # DATASET
    room_summary = get_coupon_room_summary(coupon_qs)

    reprint_totals = (
        reprint_logs.annotate(total=Count("id")).order_by("-total", "user__username")
    )

    terminal_options = { "terminal" }
    terminal_options.update(
        Coupon.objects.exclude(terminal_name="").values_list("terminal_name", flat=True)
    )
    terminal_options.update(
        VoucherScan.objects.exclude(terminal_name="").values_list("terminal_name", flat=True)
    )
    terminal_choices = sorted(filter(None, terminal_options))

    recent_coupons = list(coupon_qs.order_by("-scanned_at")[:5])
    chart_coupons = list(coupon_qs.order_by("-scanned_at")[:30])
    burned_vouchers = list(voucher_qs.order_by("-scanned_at")[:10])

    dashboard_dataset = {
        "roomLabels": [i["room"].name for i in room_summary],
        "roomValues": [i["total"] for i in room_summary],
        "sourceLabels": [c.get_source_display() for c in chart_coupons],
        "recentDates": [c.scanned_at.date().isoformat() for c in chart_coupons],
        "totalCoupons": coupon_qs.count(),
        "totalBurned": voucher_qs.count(),
    }

    context = _admin_context(
        {
            "room_summary": room_summary,
            "recent_coupons": recent_coupons,
            "burned_vouchers": burned_vouchers,
            "dashboard_dataset": dashboard_dataset,
            "rooms": RoomDirectory.choices(),
            "sources": Coupon.SOURCE_CHOICES,
            "terminals": terminal_choices,
            "reprint_totals": reprint_totals,
            "filters": {
                "room": room_id,
                "source": source_value,
                "date_start": date_start_param or "",
                "date_end": date_end_param or "",
                "terminal": selected_terminal,
            },
        },
        system_settings=system_settings,
        user=request.user,
    )

    return render(request, "raffle/admin_dashboard.html", context)


@admin_required
def admin_api_test(request):
    system_settings, _ = get_or_create_system_settings()
    active_room_id = _get_active_room_id(request, system_settings)
    form = VoucherAPITestForm(
        request.POST or None, initial={"room_id": active_room_id}
    )
    validation_result = None

    if request.method == "POST" and form.is_valid():
        _set_active_room(request, form.cleaned_data["room_id"], system_settings)
        validation_result = form.validate_remote()

    context = _admin_context(
        {"form": form, "validation_result": validation_result},
        system_settings=system_settings,
        user=request.user,
    )
    return render(request, "raffle/admin_api_test.html", context)


# -----------------------------------------------------------------------------
# DASHBOARD POR SALA PARA USUARIOS STAFF
# -----------------------------------------------------------------------------

@staff_required
def room_dashboard(request):
    system_settings, _ = get_or_create_system_settings()
    active_room_id = _get_active_room_id(request, system_settings)
    room = RoomDirectory.get(active_room_id)

    coupons = (
        Coupon.objects.select_related("person", "reprint")
        .filter(room_id=room.id)
        .order_by("-scanned_at")
    )

    context = _admin_context(
        {
            "coupons": coupons,
            "room": room,
            "system_settings": system_settings,
            "terms_text": get_terms_text(system_settings.terms_text),
            "can_reprint": request.user.has_reprint_access,
        },
        system_settings=system_settings,
        user=request.user,
    )
    return render(request, "raffle/staff_dashboard.html", context)


# -----------------------------------------------------------------------------
# REGISTRO DESDE PANEL STAFF
# -----------------------------------------------------------------------------

@staff_required
def staff_register(request):
    system_settings, _ = get_or_create_system_settings()
    active_room_id = _get_active_room_id(request, system_settings)
    form = RegistrationForm(
        request.POST or None, initial={"room_id": active_room_id}
    )
    person = None
    coupons: list[Coupon] = []

    if request.method == "POST" and form.is_valid():
        person_data = form.cleaned_data.copy()
        room_id = _get_active_room_id(request, system_settings)
        person_data.pop("room_id", None)
        try:
            with transaction.atomic():
                person = Person.objects.create(**person_data)
                coupons = create_coupons(
                    person=person,
                    quantity=5,
                    source=Coupon.REGISTER,
                    room_id=room_id,
                    terminal_name=_get_terminal_label(system_settings),
                    system_settings=system_settings,
                    created_by=request.user,
                    printed=False,
                )
        except IntegrityError:
            if Person.objects.filter(id_number=person_data["id_number"]).exists():
                form.add_error("id_number", "Ya existe un participante con ese DNI.")
            else:
                form.add_error(None, "No se pudo completar el registro.")
        else:
            for coupon in coupons:
                print_coupon_backend(coupon)
            messages.success(request, "Participante registrado y cupones emitidos.")
            return redirect(reverse("raffle_admin:staff_register"))

    context = _admin_context(
        {
            "form": form,
            "person": person,
            "system_settings": system_settings,
            "terms_text": get_terms_text(system_settings.terms_text),
        },
        system_settings=system_settings,
        user=request.user,
    )

    return render(request, "raffle/staff_register.html", context)


@staff_required
def cashier_register(request):
    system_settings, _ = get_or_create_system_settings()
    active_room_id = _get_active_room_id(request, system_settings)
    form = CashierRegistrationForm(
        request.POST or None, initial={"room_id": active_room_id}
    )

    if request.method == "POST" and form.is_valid():
        person_data = form.cleaned_data.copy()
        room_id = _get_active_room_id(request, system_settings)
        person_data.pop("room_id", None)
        try:
            with transaction.atomic():
                person = Person.objects.create(**person_data)
                coupons = create_coupons(
                    person=person,
                    quantity=5,
                    source=Coupon.REGISTER,
                    room_id=room_id,
                    terminal_name=_get_terminal_label(system_settings),
                    system_settings=system_settings,
                    created_by=request.user,
                    printed=False,
                )
        except IntegrityError:
            if Person.objects.filter(id_number=person_data["id_number"]).exists():
                form.add_error("id_number", "Ya existe un participante con ese DNI.")
            else:
                form.add_error(None, "No se pudo completar el registro.")
        else:
            messages.success(
                request,
                "Participante registrado. Imprima los cupones pendientes desde el listado.",
            )
            return redirect(reverse("raffle_admin:cashier_register"))

    context = _admin_context(
        {
            "form": form,
            "system_settings": system_settings,
            "terms_text": get_terms_text(system_settings.terms_text),
        },
        system_settings=system_settings,
        user=request.user,
    )

    return render(request, "raffle/cashier_register.html", context)


# -----------------------------------------------------------------------------
# INGRESOS DESDE PANEL STAFF
# -----------------------------------------------------------------------------


@staff_required
def staff_entry(request):
    system_settings, _ = get_or_create_system_settings()
    active_room_id = _get_active_room_id(request, system_settings)
    form = EntryForm(
        request.POST or None, initial={"room_id": active_room_id}
    )
    person = None
    coupons: list[Coupon] = []

    if request.method == "POST" and form.is_valid():
        id_number = form.cleaned_data["id_number"]
        room_id = _get_active_room_id(request, system_settings)
        voucher_code = form.cleaned_data.get("voucher_code", "")
        try:
            person = Person.objects.get(id_number=id_number)
        except Person.DoesNotExist:
            form.add_error("id_number", "No existe un participante con ese DNI.")
        else:
            if VoucherScan.objects.filter(code=voucher_code).exists():
                form.add_error(None, "El voucher ya fue utilizado.")
            else:
                rule_check = validate_entry_rules(person, system_settings)
                if not rule_check.is_valid:
                    form.add_error(None, rule_check.message)
                else:
                    terminal_label = _get_terminal_label(system_settings)
                    try:
                        with transaction.atomic():
                            locked_rules = validate_entry_rules(
                                person, system_settings, lock_rows=True
                            )
                            if not locked_rules.is_valid:
                                raise EntryValidationError(locked_rules.message)

                            VoucherScan.objects.create(
                                code=voucher_code,
                                person=person,
                                room_id=room_id,
                                terminal_name=terminal_label,
                                source=Coupon.ENTRY,
                            )
                            coupons = create_coupons(
                                person=person,
                                quantity=1,
                                source=Coupon.ENTRY,
                                room_id=room_id,
                                terminal_name=terminal_label,
                                system_settings=system_settings,
                                created_by_user=request.user.has_operator_access,
                            )
                    except EntryValidationError as error:
                        form.add_error(None, str(error))
                    except IntegrityError:
                        form.add_error(None, "El voucher ya fue utilizado.")
                    else:
                        for coupon in coupons:
                            print_coupon_backend(coupon)
                        messages.success(request, "Ingreso registrado y cupón emitido.")
                        return redirect(reverse("raffle_admin:staff_entry"))

    context = _admin_context(
        {
            "form": form,
            "person": person,
            "system_settings": system_settings,
            "terms_text": get_terms_text(system_settings.terms_text),
        },
        system_settings=system_settings,
        user=request.user,
    )

    return render(request, "raffle/staff_entry.html", context)


@staff_required
def manual_entry(request):
    system_settings, _ = get_or_create_system_settings()
    terminal_config, redirect_response = _terminal_config_or_redirect(request)
    if redirect_response:
        return redirect_response
    if not request.user.has_manual_access:
        messages.error(request, "No posee permisos para ingreso manual.")
        return redirect("raffle_admin:room_dashboard")

    form = ManualCouponForm(request.POST or None)
    person = None

    if request.method == "POST" and form.is_valid():
        id_number = form.cleaned_data["id_number"]
        try:
            person = Person.objects.get(id_number=id_number)
        except Person.DoesNotExist:
            form.add_error("id_number", "No existe un participante con ese DNI.")
        else:
            try:
                with transaction.atomic():
                    create_manual_coupon(
                        person=person,
                        user=request.user,
                        room_id=_get_active_room_id(request, system_settings),
                    )
            except IntegrityError:
                form.add_error(None, "No se pudo generar el cupón manual.")
            else:
                messages.success(
                    request, "Cupón generado. Imprima los pendientes desde el listado."
                )
                return redirect("raffle_admin:manual_list")

    context = _admin_context(
        {
            "form": form,
            "person": person,
            "system_settings": system_settings,
            "terms_text": get_terms_text(system_settings.terms_text),
        },
        system_settings=system_settings,
        user=request.user,
    )
    return render(request, "raffle/manual_entry.html", context)


@staff_required
def manual_list(request):
    system_settings, _ = get_or_create_system_settings()
    terminal_config, redirect_response = _terminal_config_or_redirect(request)
    if redirect_response:
        return redirect_response
    if not request.user.has_manual_access:
        messages.error(request, "No posee permisos para esta sección.")
        return redirect("raffle_admin:room_dashboard")

    selected_room_id = _get_active_room_id(request, system_settings)
    is_admin_view = request.user.is_admin()
    is_manager_view = request.user.is_floor_manager
    room_form = None

    if is_manager_view:
        room_form = ManualPendingFilterForm(
            request.GET or None, initial={"room_id": selected_room_id}
        )
        if room_form.is_valid():
            selected_room_id = room_form.cleaned_data["room_id"]
            _set_active_room(request, selected_room_id, system_settings)
        elif request.method == "POST":
            posted_room_id = request.POST.get("room_id")
            if posted_room_id and posted_room_id.isdigit():
                selected_room_id = int(posted_room_id)
                _set_active_room(request, selected_room_id, system_settings)
                room_form = ManualPendingFilterForm(initial={"room_id": selected_room_id})

    pending_qs = (
        Coupon.objects.select_related("person", "created_by")
        .filter(
            source__in=(Coupon.MANUAL, Coupon.REGISTER),
            printed=False,
        )
        .order_by("scanned_at")
    )

    if is_admin_view:
        pass
    elif is_manager_view:
        pending_qs = pending_qs.filter(room_id=selected_room_id)
        pending_qs = pending_qs.filter(created_by__role=UserModel.Role.CASHIER)
    else:
        pending_qs = pending_qs.filter(created_by=request.user)

    cashier_summary = []
    room_summary = []
    room_creator_summary = []
    if is_admin_view:
        room_summary_queryset = (
            pending_qs.values("room_id")
            .annotate(total=Count("id"))
            .order_by("room_id")
        )
        room_summary = [
            {
                **item,
                "room_name": RoomDirectory.get(item["room_id"]).name,
            }
            for item in room_summary_queryset
        ]
        room_creator_summary_queryset = (
            pending_qs.values(
                "room_id",
                "created_by__id",
                "created_by__username",
                "created_by__first_name",
                "created_by__last_name",
            )
            .annotate(total=Count("id"))
            .order_by("room_id", "created_by__first_name", "created_by__username")
        )
        room_creator_summary = [
            {
                **item,
                "room_name": RoomDirectory.get(item["room_id"]).name,
                "creator_name": (
                    f"{item.get('created_by__first_name', '').strip()} "
                    f"{item.get('created_by__last_name', '').strip()}"
                ).strip()
                or item.get("created_by__username")
                or "Sin asignar",
            }
            for item in room_creator_summary_queryset
        ]
    elif is_manager_view:
        cashier_summary_queryset = (
            pending_qs.values(
                "created_by__id",
                "created_by__username",
                "created_by__first_name",
                "created_by__last_name",
            )
            .annotate(total=Count("id"))
            .order_by("created_by__first_name", "created_by__username")
        )
        cashier_summary = [
            {
                **item,
                "creator_name": (
                    f"{item.get('created_by__first_name', '').strip()} "
                    f"{item.get('created_by__last_name', '').strip()}"
                ).strip()
                or item.get("created_by__username")
                or "Sin asignar",
            }
            for item in cashier_summary_queryset
        ]

    if request.method == "POST":
        print_scope = request.POST.get("print_scope", "all")
        target_room_id = request.POST.get("target_room_id")
        target_user_id = request.POST.get("target_user_id")
        printable_qs = pending_qs

        if is_admin_view and print_scope == "room" and str(target_room_id).isdigit():
            printable_qs = printable_qs.filter(room_id=int(target_room_id))
        if is_admin_view and print_scope == "creator" and str(target_user_id).isdigit():
            printable_qs = printable_qs.filter(created_by_id=int(target_user_id))
            if str(target_room_id).isdigit():
                printable_qs = printable_qs.filter(room_id=int(target_room_id))

        try:
            with transaction.atomic():
                coupon_ids = list(printable_qs.values_list("id", flat=True))
                coupons = list(
                    Coupon.objects.select_for_update()
                    .select_related("person")
                    .filter(id__in=coupon_ids)
                )
                if not coupons:
                    messages.info(request, "No hay cupones pendientes de impresión.")
                    return redirect("raffle_admin:manual_list")
                for coupon in coupons:
                    print_coupon_backend(coupon)
                    coupon.printed = True
                    coupon.save(update_fields=["printed"])
        except Exception:
            messages.error(request, "No se pudo imprimir el lote de cupones.")
        else:
            messages.success(request, "Cupones impresos y marcados como completados.")
        return redirect("raffle_admin:manual_list")

    context = _admin_context(
        {
            "coupons": pending_qs.order_by("-scanned_at")[:10],
            "cashier_summary": cashier_summary,
            "room_summary": room_summary,
            "room_creator_summary": room_creator_summary,
            "room_form": room_form,
            "active_room_id": selected_room_id,
            "is_manager_view": is_manager_view,
            "is_admin_view": is_admin_view,
            "system_settings": system_settings,
        },
        system_settings=system_settings,
        user=request.user,
    )
    return render(request, "raffle/manual_list.html", context)


# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE TERMINAL LOCAL
# -----------------------------------------------------------------------------


@staff_required
def configure_terminal(request):
    system_settings, _ = get_or_create_system_settings()
    existing_config = get_terminal_config()
    form = TerminalConfigForm(request.POST or None, initial=existing_config)

    if request.method == "POST" and form.is_valid():
        room = form.cleaned_data["room_id"]
        save_terminal_config(
            terminal_id=form.cleaned_data["terminal_id"],
            room_id=room.pk,
            room_ip=form.cleaned_data["room_ip"],
            printer_name=form.cleaned_data.get("printer_name"),
            printer_port=form.cleaned_data.get("printer_port"),
        )
        messages.success(request, "Configuración de terminal actualizada.")
        return redirect(reverse("raffle:configure_terminal"))

    context = _admin_context(
        {"form": form, "terminal_config": existing_config},
        system_settings=system_settings,
        user=request.user,
    )
    return render(request, "raffle/configure_terminal.html", context)


# -----------------------------------------------------------------------------
# BORRAR BASE DE DATOS
# -----------------------------------------------------------------------------

@admin_required
@require_POST
def admin_clear_database(request):
    with transaction.atomic():
        Coupon.objects.all().delete()
        VoucherScan.objects.all().delete()
        Person.objects.all().delete()

    messages.success(request, "Se limpiaron todos los datos de la base.")
    return redirect("raffle_admin:dashboard")


# -----------------------------------------------------------------------------
# LISTA DE CUPONES
# -----------------------------------------------------------------------------


def _filter_coupons_queryset(request, coupons, system_settings):
    """Apply room and terminal filters to the coupons queryset."""

    selected_room = request.GET.get("room")
    selected_room_id = int(selected_room) if selected_room and selected_room.isdigit() else None
    if selected_room_id is not None:
        coupons = coupons.filter(room_id=selected_room_id)

    selected_terminal = (request.GET.get("terminal") or "").strip()
    if selected_terminal:
        coupons = coupons.filter(terminal_name=selected_terminal)

    terminal_options = {_get_terminal_label(system_settings)}
    terminal_options.update(
        Coupon.objects.exclude(terminal_name="").values_list("terminal_name", flat=True)
    )
    terminals = sorted(filter(None, terminal_options))

    return coupons, selected_room_id, selected_terminal, terminals


def _apply_coupon_filters(request, coupons, system_settings):
    """Apply all available filters to the coupon queryset."""

    coupons, selected_room_id, selected_terminal, terminals = _filter_coupons_queryset(
        request, coupons, system_settings
    )

    participant_query = (request.GET.get("participant") or "").strip()
    if participant_query:
        coupons = coupons.filter(
            Q(person__first_name__icontains=participant_query)
            | Q(person__last_name__icontains=participant_query)
            | Q(person__id_number__icontains=participant_query)
        )

    coupon_query = (request.GET.get("coupon") or "").strip()
    if coupon_query:
        coupons = coupons.filter(
            Q(code__icontains=coupon_query)
            | Q(person__phone__icontains=coupon_query)
            | Q(person__email__icontains=coupon_query)
        )

    source_value = (request.GET.get("source") or "").strip()
    valid_sources = {choice[0] for choice in Coupon.SOURCE_CHOICES}
    if source_value and source_value in valid_sources:
        coupons = coupons.filter(source=source_value)
    else:
        source_value = ""

    def _parse_date(value: str | None):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return None

    start_date = _parse_date(request.GET.get("date_start"))
    end_date = _parse_date(request.GET.get("date_end"))
    current_tz = timezone.get_default_timezone()
    if start_date:
        dt = datetime.combine(start_date, time.min)
        dt = timezone.make_aware(dt, current_tz) if settings.USE_TZ else dt
        coupons = coupons.filter(scanned_at__gte=dt)
    if end_date:
        dt = datetime.combine(end_date, time.max)
        dt = timezone.make_aware(dt, current_tz) if settings.USE_TZ else dt
        coupons = coupons.filter(scanned_at__lte=dt)

    filter_state = {
        "rooms": RoomDirectory.choices(),
        "selected_room": selected_room_id,
        "terminals": terminals,
        "selected_terminal": selected_terminal,
        "selected_participant": participant_query,
        "selected_coupon": coupon_query,
        "selected_source": source_value,
        "date_start": request.GET.get("date_start", ""),
        "date_end": request.GET.get("date_end", ""),
        "source_choices": Coupon.SOURCE_CHOICES,
    }

    return coupons, filter_state


@admin_required
def admin_coupons(request):
    system_settings, _ = get_or_create_system_settings()
    base_coupons = Coupon.objects.select_related("person").order_by("-scanned_at")
    coupons, filter_state = _apply_coupon_filters(request, base_coupons, system_settings)

    paginator = Paginator(coupons, 100)
    page_number = request.GET.get("page")
    page_obj = paginator._get_page([], 1, paginator) if paginator.count == 0 else paginator.get_page(page_number)

    base_params = request.GET.copy()
    base_params.pop("page", None)
    base_query = base_params.urlencode()
    base_query = f"{base_query}&" if base_query else ""
    current_page = page_obj.number if paginator.count else 1
    total_pages = paginator.num_pages or 1

    context = _admin_context(
        {
            "coupons": page_obj.object_list,
            "room_summary": get_coupon_room_summary(coupons),
            "coupon_count": paginator.count,
            "paginator": paginator,
            "page_obj": page_obj,
            "current_page": current_page,
            "total_pages": total_pages,
            "pagination_query": base_query,
            "export_query": request.GET.urlencode(),
            **filter_state,
        },
        system_settings=system_settings,
        user=request.user,
    )
    return render(request, "raffle/admin_coupons.html", context)


@admin_required
def admin_coupons_export(request):
    system_settings, _ = get_or_create_system_settings()
    coupons = Coupon.objects.select_related("person").order_by("-scanned_at")
    coupons, filter_state = _apply_coupon_filters(request, coupons, system_settings)

    export_type = (request.GET.get("export") or "all").lower()
    builder = {
        "all": build_coupon_report_workbook,
        "room": build_room_report_workbook,
        "day": build_daily_report_workbook,
    }.get(export_type, build_coupon_report_workbook)
    workbook = builder(coupons)

    filename_tokens = ["cupones"]
    if export_type == "room":
        filename_tokens.append("por_sala")
    elif export_type == "day":
        filename_tokens.append("por_dia")
    selected_room_id = filter_state.get("selected_room")
    selected_terminal = filter_state.get("selected_terminal")
    if selected_room_id is not None:
        filename_tokens.append(f"sala{selected_room_id}")
    if selected_terminal:
        filename_tokens.append(selected_terminal)
    now_value = timezone.now()
    timestamp_reference = timezone.localtime(now_value) if timezone.is_aware(now_value) else now_value
    timestamp = timestamp_reference.strftime("%Y%m%d_%H%M")
    filename = "_".join(filename_tokens + [timestamp]) + ".xlsx"

    return render_workbook_response(workbook, filename)


# -----------------------------------------------------------------------------
# REIMPRESIONES
# -----------------------------------------------------------------------------

@admin_required
def admin_reprints(request):
    system_settings, _ = get_or_create_system_settings()
    reprints = (
        CouponReprintLog.objects.select_related("coupon", "coupon__person", "user")
        .order_by("-created_at")
    )

    selected_room = request.GET.get("room")
    selected_room_id = int(selected_room) if selected_room and selected_room.isdigit() else None
    if selected_room_id is not None:
        reprints = reprints.filter(room_id=selected_room_id)

    selected_terminal = (request.GET.get("terminal") or "").strip()
    if selected_terminal:
        reprints = reprints.filter(coupon__terminal_name=selected_terminal)

    user_totals_qs = CouponReprintLog.objects.all()
    if selected_room_id is not None:
        user_totals_qs = user_totals_qs.filter(room_id=selected_room_id)
    if selected_terminal:
        user_totals_qs = user_totals_qs.filter(coupon__terminal_name=selected_terminal)

    user_totals = (
        user_totals_qs.values("user__id", "user__username")
        .annotate(total=Count("id"))
        .order_by("-total", "user__username")
    )

    room_lookup = {room.id: room.name for room in RoomDirectory.all()}

    terminal_options = {_get_terminal_label(system_settings)}
    terminal_options.update(
        Coupon.objects.exclude(terminal_name="").values_list("terminal_name", flat=True)
    )
    terminal_options.update(
        CouponReprintLog.objects.exclude(coupon__terminal_name="").values_list(
            "coupon__terminal_name", flat=True
        )
    )
    terminals = sorted(filter(None, terminal_options))

    context = _admin_context(
        {
            "reprints": reprints,
            "user_totals": user_totals,
            "room_lookup": room_lookup,
            "rooms": RoomDirectory.choices(),
            "terminals": terminals,
            "selected_room": selected_room_id,
            "selected_terminal": selected_terminal,
        },
        system_settings=system_settings,
        user=request.user,
    )
    return render(request, "raffle/admin_reprints.html", context)


# -----------------------------------------------------------------------------
# CONFIGURACIÓN DEL SISTEMA (IMPRESORA + SISTEMA)
# -----------------------------------------------------------------------------

@admin_required
def admin_configuration(request):
    configuration = get_or_create_printer_configuration()
    system_settings, _ = get_or_create_system_settings()

    _sync_default_rooms()

    valid_tabs = {"printers", "system", "rooms", "users"}
    active_tab = request.GET.get("tab", "printers")
    active_tab = active_tab if active_tab in valid_tabs else "printers"

    raw_form_type = None
    if request.method == "POST":
        raw_form_type = request.POST.get("form_type", "printers")
        active_tab = raw_form_type if raw_form_type in valid_tabs else "printers"
        if raw_form_type == "local_printer":
            active_tab = "printers"

    configuration_form = PrinterConfigurationForm(request.POST or None, instance=configuration)
    initial_settings = {"terms_text": get_terms_text(system_settings.terms_text)}
    settings_form = SystemSettingsForm(request.POST or None, instance=system_settings, initial=initial_settings)
    room_formset_class = modelformset_factory(Room, form=RoomForm, extra=1, can_delete=False)
    room_queryset = Room.objects.order_by("id")
    room_formset = room_formset_class(
        request.POST if active_tab == "rooms" else None,
        queryset=room_queryset,
        prefix="rooms",
    )
    locked_room_ids = _rooms_with_dependencies({room.id for room in room_queryset}, system_settings)
    _decorate_room_formset(room_formset, locked_room_ids)

    selected_user_id = request.GET.get("user") or request.POST.get("user_id")
    editing_user = None
    if selected_user_id and str(selected_user_id).isdigit():
        try:
            editing_user = UserModel.objects.get(pk=int(selected_user_id))
        except UserModel.DoesNotExist:
            editing_user = None
        else:
            if request.method != "POST":
                active_tab = "users"

    user_form = AdminUserForm(request.POST or None, instance=editing_user)
    delete_form = AdminUserDeleteForm(request.POST or None)

    printer_config = get_terminal_config()
    printer_form = LocalPrinterConfigForm(
        request.POST if raw_form_type == "local_printer" else None,
        initial=printer_config or {},
    )

    if request.method == "POST":
        if raw_form_type == "local_printer" and printer_form.is_valid():
            try:
                save_terminal_config(
                    terminal_id=(printer_config or {}).get("terminal_id"),
                    room_id=(printer_config or {}).get("room_id"),
                    room_ip=(printer_config or {}).get("room_ip"),
                    printer_name=printer_form.cleaned_data["printer_name"],
                    printer_port=printer_form.cleaned_data["printer_port"],
                )
            except ValueError:
                messages.error(
                    request,
                    "Debe configurar el terminal local antes de guardar la impresora.",
                )
            else:
                messages.success(request, "Impresora local actualizada correctamente.")
                return redirect(f"{reverse('raffle_admin:configuration')}?tab=printers")

        if active_tab == "printers" and configuration_form.is_valid():
            configuration_form.save()
            messages.success(request, "Configuración de impresora guardada correctamente.")
            return redirect(f"{reverse('raffle_admin:configuration')}?tab=printers")

        if active_tab == "system" and settings_form.is_valid():
            save_terms_config(settings_form.cleaned_data.get("terms_text", ""))
            settings_form.save()
            messages.success(request, "Preferencias del sistema actualizadas.")
            return redirect(f"{reverse('raffle_admin:configuration')}?tab=system")

        if active_tab == "rooms" and room_formset.is_valid():
            room_formset.save()
            messages.success(request, "Salas actualizadas correctamente.")
            return redirect(f"{reverse('raffle_admin:configuration')}?tab=rooms")

        if active_tab == "users":
            action = request.POST.get("action", "save")
            if action == "delete" and delete_form.is_valid():
                user_id = delete_form.cleaned_data["user_id"]
                try:
                    target = UserModel.objects.get(pk=user_id)
                except UserModel.DoesNotExist:
                    messages.error(request, "El usuario seleccionado ya no existe.")
                else:
                    if target.is_superuser:
                        messages.error(
                            request,
                            "No puede eliminar un superusuario desde este panel.",
                        )
                    elif target.pk == request.user.pk:
                        messages.error(request, "No puede eliminar su propia cuenta mientras está en uso.")
                    else:
                        target.delete()
                        messages.success(request, "Usuario eliminado correctamente.")
                return redirect(f"{reverse('raffle_admin:configuration')}?tab=users")

            if user_form.is_valid():
                saved_user = user_form.save()
                verb = "actualizado" if editing_user else "creado"
                messages.success(request, f"Usuario {verb} correctamente.")
                return redirect(
                    f"{reverse('raffle_admin:configuration')}?tab=users&user={saved_user.pk}"
                )

    context = _admin_context(
        {
            "form": configuration_form,
            "settings_form": settings_form,
            "configuration": configuration,
            "system_settings": system_settings,
            "room_formset": room_formset,
            "locked_room_ids": locked_room_ids,
            "usb_devices": None,
            "pyusb_available": pyusb_available(),
            "active_tab": active_tab,
            "user_form": user_form,
            "user_list": UserModel.objects.order_by("username"),
            "editing_user": editing_user,
            "delete_form": delete_form,
            "local_printer_form": printer_form,
        },
        configuration=configuration,
        system_settings=system_settings,
        user=request.user,
    )

    return render(request, "raffle/admin_configuration.html", context)


def _normalize_person_name(value: str) -> str:
    # Collapse whitespace and convert to title case for consistent storage.
    normalized = " ".join(value.split()).strip()
    return normalized.title()


@require_POST
@admin_required
def admin_normalize_participants(request):
    # Normalize participant names across the roster.
    updated = 0
    for person in Person.objects.all().iterator():
        normalized_first = _normalize_person_name(person.first_name)
        normalized_last = _normalize_person_name(person.last_name)
        if normalized_first != person.first_name or normalized_last != person.last_name:
            Person.objects.filter(pk=person.pk).update(
                first_name=normalized_first,
                last_name=normalized_last,
            )
            updated += 1

    if updated:
        messages.success(
            request, f"Normalized {updated} participant name(s) to Title Case."
        )
    else:
        messages.info(request, "All participant names are already normalized.")

    return redirect(f"{reverse('raffle_admin:configuration')}?tab=system")


def _sync_default_rooms():
    """Ensure the default room catalog exists in the database."""

    for room in RoomDirectory._DEFAULT_ROOMS.values():
        Room.objects.update_or_create(
            id=room.id, defaults={"name": room.name, "room_ip": room.room_ip}
        )


def _restore_room_formset_management(post_data, queryset, prefix: str):
    """Rebuild management form markers when the frontend omits them."""

    data = post_data.copy()
    detected_indexes = set()
    for key in data.keys():
        if key.startswith(f"{prefix}-"):
            parts = key.split("-")
            if len(parts) >= 3 and parts[1].isdigit():
                detected_indexes.add(int(parts[1]))

    total_forms = max(detected_indexes) + 1 if detected_indexes else queryset.count()
    data.setdefault(f"{prefix}-TOTAL_FORMS", str(total_forms))
    data.setdefault(f"{prefix}-INITIAL_FORMS", str(queryset.count()))
    data.setdefault(f"{prefix}-MIN_NUM_FORMS", "0")
    data.setdefault(f"{prefix}-MAX_NUM_FORMS", "1000")
    return data


def _rooms_with_dependencies(room_ids: set[int], system_settings: SystemSettings) -> set[int]:
    """Return room identifiers that are referenced by stored data."""

    if not room_ids:
        return set()

    dependency_sets = [
        set(
            Coupon.objects.filter(room_id__in=room_ids).values_list(
                "room_id", flat=True
            )
        ),
        set(
            VoucherScan.objects.filter(room_id__in=room_ids).values_list(
                "room_id", flat=True
            )
        ),
        set(
            CouponReprint.objects.filter(room_id__in=room_ids).values_list(
                "room_id", flat=True
            )
        ),
        set(
            CouponReprintLog.objects.filter(room_id__in=room_ids).values_list(
                "room_id", flat=True
            )
        ),
        set(
            CouponSequence.objects.filter(room_id__in=room_ids).values_list(
                "room_id", flat=True
            )
        ),
        set(
            ManualCouponSequence.objects.filter(room_id__in=room_ids).values_list(
                "room_id", flat=True
            )
        ),
    ]

    dependencies = set().union(*dependency_sets)
    if system_settings.current_room_id in room_ids:
        dependencies.add(system_settings.current_room_id)
    return dependencies


def _decorate_room_formset(room_formset, locked_room_ids: set[int]):
    """Attach UI metadata for delete controls in the room formset."""

    for form in room_formset.forms:
        if "DELETE" not in form.fields:
            continue
        form.fields["DELETE"].widget.attrs.update({"class": "admin-checkbox__input"})
        if getattr(form.instance, "id", None) in locked_room_ids:
            form.fields["DELETE"].disabled = True
            form.fields["DELETE"].widget.attrs.update(
                {
                    "data-room-delete-locked": "true",
                    "title": "No puede eliminar una sala que ya tiene registros asociados.",
                }
            )


# -----------------------------------------------------------------------------
# SCAN DE IMPRESORAS USB
# -----------------------------------------------------------------------------

@admin_required
@require_POST
def admin_configuration_printers(request):
    if not pyusb_available():
        return JsonResponse({"usb_devices": [], "pyusb_available": False})

    printer_data = available_printers()
    return JsonResponse(printer_data)


# -----------------------------------------------------------------------------
# REIMPRESIÓN PARA STAFF
# -----------------------------------------------------------------------------

@staff_required
@require_POST
def room_reprint_coupon(request, coupon_id: int):
    system_settings, _ = get_or_create_system_settings()
    terminal_config, redirect_response = _terminal_config_or_redirect(request)
    if redirect_response:
        return redirect_response

    if not request.user.has_reprint_access:
        return JsonResponse(
            {"success": False, "message": "No posee permisos para reimpresión."},
            status=403,
        )

    coupon = get_object_or_404(
        Coupon.objects.select_related("person"),
        pk=coupon_id,
        room_id=_get_active_room_id(request, system_settings),
    )

    if CouponReprint.objects.filter(coupon=coupon).exists():
        return JsonResponse(
            {"success": False, "message": "El cupón ya fue reimpreso previamente."},
            status=400,
        )

    try:
        with transaction.atomic():
            print_coupon_backend(coupon)
            register_reprint(coupon, request.user)
    except Exception:
        return JsonResponse(
            {"success": False, "message": "No se pudo enviar el cupón a la impresora."},
            status=500,
        )

    return JsonResponse({"success": True, "message": "Cupón reimpreso correctamente."})


# -----------------------------------------------------------------------------
# REIMPRESIÓN PARA ADMIN
# -----------------------------------------------------------------------------

@admin_required
@require_POST
def admin_print_coupon(request, coupon_id: int):
    coupon = get_object_or_404(Coupon.objects.select_related("person"), pk=coupon_id)

    if CouponReprint.objects.filter(coupon=coupon).exists():
        return JsonResponse(
            {"success": False, "message": "El cupón ya fue reimpreso previamente."},
            status=400,
        )

    try:
        with transaction.atomic():
            print_coupon_backend(coupon)
            register_reprint(coupon, request.user)
    except Exception:
        return JsonResponse(
            {"success": False, "message": "No se pudo enviar el cupón a la impresora."},
            status=500,
        )

    return JsonResponse({"success": True, "message": "Cupón enviado a la impresora."})
