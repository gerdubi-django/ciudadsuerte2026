from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from ..forms import EntryForm, RegistrationForm
from ..models import Coupon, Person, VoucherScan
from ..services import (
    EntryValidationError,
    create_coupons,
    get_or_create_system_settings,
    print_coupon_backend,
    validate_entry_rules,
    validate_voucher_code,
)
from ..utils.terminal import get_terminal_config
from ..utils.terms import get_terms_text


def home(request):
    return render(request, "raffle/home.html")


def register(request):
    terminal_config = get_terminal_config()
    if terminal_config is None:
        return redirect("raffle:configure_terminal")

    system_settings, _ = get_or_create_system_settings()
    room_id = terminal_config["room_id"]
    terminal_name = terminal_config.get("terminal_id") or system_settings.terminal_name
    form = RegistrationForm(request.POST or None, initial={"room_id": room_id})
    coupons = []
    person = None
    if request.method == "POST" and form.is_valid():
        person_data = form.cleaned_data.copy()
        person_data.pop("room_id", None)
        try:
            with transaction.atomic():
                person = Person.objects.create(**person_data)
                coupons = create_coupons(
                    person=person,
                    quantity=5,
                    source=Coupon.REGISTER,
                    room_id=room_id,
                    terminal_name=terminal_name,
                    system_settings=system_settings,
                )
        except IntegrityError:
            if Person.objects.filter(id_number=person_data["id_number"]).exists():
                form.add_error("id_number", "Ya existe un participante con ese DNI.")
            else:
                form.add_error(None, "No se pudo completar el registro.")
        else:
            for coupon in coupons:
                print_coupon_backend(coupon)
            if coupons:
                return redirect("raffle:home")
    return render(
        request,
        "raffle/register.html",
        {"form": form, "person": person, "system_settings": system_settings, "terms_text": get_terms_text(system_settings.terms_text)},
    )


def entry(request):
    terminal_config = get_terminal_config()
    if terminal_config is None:
        return redirect("raffle:configure_terminal")

    system_settings, _ = get_or_create_system_settings()
    form = EntryForm(request.POST or None, initial={"room_id": terminal_config["room_id"]})
    coupons = []
    person = None
    status_message = ""

    room_id = terminal_config["room_id"]
    terminal_name = terminal_config.get("terminal_id") or system_settings.terminal_name

    if request.method == "POST" and form.is_valid():
        id_number = form.cleaned_data["id_number"]
        voucher_code = form.cleaned_data.get("voucher_code", "")

        # Buscar persona por DNI
        try:
            person = Person.objects.get(id_number=id_number)
        except Person.DoesNotExist:
            form.add_error("id_number", "No existe un participante con ese DNI.")
        else:
            validation = validate_voucher_code(
                voucher_code, room_id, terminal_config.get("room_ip")
            )
            if not validation.is_valid:
                status_message = validation.message
                form.add_error(None, validation.message)
            elif VoucherScan.objects.filter(code=voucher_code).exists():
                form.add_error(None, "El voucher ya fue utilizado.")
            else:
                rule_check = validate_entry_rules(person, system_settings)
                if not rule_check.is_valid:
                    form.add_error(None, rule_check.message)
                    status_message = rule_check.message
                else:
                    try:
                        with transaction.atomic():
                            locked_rules = validate_entry_rules(
                                person, system_settings, lock_rows=True
                            )
                            if not locked_rules.is_valid:
                                raise EntryValidationError(locked_rules.message)

                            # Registrar el voucher validado
                            VoucherScan.objects.create(
                                code=voucher_code,
                                person=person,
                                room_id=room_id,
                                terminal_name=terminal_name,
                                source=Coupon.ENTRY,
                            )

                            # Crear cupón
                            coupons = create_coupons(
                                person=person,
                                quantity=1,
                                source=Coupon.ENTRY,
                                room_id=room_id,
                                terminal_name=terminal_name,
                                system_settings=system_settings,
                                created_by_user=False,
                            )

                    except EntryValidationError as error:
                        form.add_error(None, str(error))
                        status_message = str(error)
                    except IntegrityError:
                        form.add_error(None, "El voucher ya fue utilizado.")
                    else:
                        # Imprimir cupones
                        for coupon in coupons:
                            print_coupon_backend(coupon)

                        if coupons:
                            return redirect("raffle:home")

    return render(
        request,
        "raffle/entry.html",
        {
            "form": form,
            "person": person,
            "scan_status_message": status_message,
        },
    )


@require_POST
def validate_entry_voucher(request):
    terminal_config = get_terminal_config()
    if terminal_config is None:
        return redirect("raffle:configure_terminal")

    code = request.POST.get("voucher_code", "").strip()
    if not code:
        return JsonResponse({"valid": False, "message": "Voucher requerido."}, status=400)

    validation = validate_voucher_code(
        code.upper(), terminal_config["room_id"], terminal_config.get("room_ip")
    )
    status_code = 200 if validation.is_valid else 400
    return JsonResponse(
        {"valid": validation.is_valid, "message": validation.message}, status=status_code
    )



def person_lookup(request):
    id_number = request.GET.get("id_number", "").strip()
    if not id_number:
        return JsonResponse({"error": "Missing id_number."}, status=400)

    try:
        person = Person.objects.get(id_number=id_number)
    except Person.DoesNotExist:
        return JsonResponse({"error": "Person not found."}, status=404)

    full_name = f"{person.first_name} {person.last_name}".strip()
    return JsonResponse(
        {
            "firstName": person.first_name,
            "lastName": person.last_name,
            "fullName": full_name,
            "idNumber": person.id_number,
        }
    )
