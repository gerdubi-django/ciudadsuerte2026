from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_operator_users(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    # Define the operator and floor manager records to be inserted.
    operator_accounts = [
        {"first_name": "Cristian", "last_name": "Alarcon", "username": "Cristian.Alarcon", "password": "A9K2D7QF", "role": "cambista"},
        {"first_name": "Liliana", "last_name": "Alfonzo", "username": "Liliana.Alfonzo", "password": "M4Z8Q2TN", "role": "cambista"},
        {"first_name": "Alicia", "last_name": "Benitez", "username": "Alicia.Benitez", "password": "H7P3W9CA", "role": "cambista"},
        {"first_name": "Cristian", "last_name": "Bernal", "username": "Cristian.Bernal", "password": "Q6R2L8MX", "role": "cambista"},
        {"first_name": "Mauricio", "last_name": "Castillo", "username": "Mauricio.Castillo", "password": "T8F9A3KD", "role": "cambista"},
        {"first_name": "Patricia", "last_name": "Castro", "username": "Patricia.Castro", "password": "W5E7B2JG", "role": "cambista"},
        {"first_name": "Rita", "last_name": "Cespedes", "username": "Rita.Cespedes", "password": "Z1N6Q8VP", "role": "cambista"},
        {"first_name": "Federico", "last_name": "Fleitas", "username": "Federico.Fleitas", "password": "C9T4M2LX", "role": "cambista"},
        {"first_name": "Nelson", "last_name": "Foschiatti", "username": "Nelson.Foschiatti", "password": "D3G7P5RW", "role": "cambista"},
        {"first_name": "Noelia", "last_name": "Gonzalez", "username": "Noelia.Gonzalez", "password": "L8S2Q9FT", "role": "cambista"},
        {"first_name": "Alejandra", "last_name": "Hernandez", "username": "Alejandra.Hernandez", "password": "R4B6P7KM", "role": "cambista"},
        {"first_name": "Analia", "last_name": "Hernandez", "username": "Analia.Hernandez", "password": "G2J9V8TS", "role": "cambista"},
        {"first_name": "Ulises", "last_name": "Leiva", "username": "Ulises.Leiva", "password": "P7A3H4DQ", "role": "cambista"},
        {"first_name": "Gerardo", "last_name": "Lovato", "username": "Gerardo.Lovato", "password": "V6K9S1ME", "role": "cambista"},
        {"first_name": "Diego", "last_name": "Luque", "username": "Diego.Luque", "password": "B5P8L3QH", "role": "cambista"},
        {"first_name": "Adrian", "last_name": "Medina", "username": "Adrian.Medina", "password": "E9M1T7CZ", "role": "cambista"},
        {"first_name": "Cecilia", "last_name": "Mercado", "username": "Cecilia.Mercado", "password": "N3Q6J4VR", "role": "cambista"},
        {"first_name": "Rodolfo", "last_name": "Oviedo", "username": "Rodolfo.Oviedo", "password": "K4S9W2FP", "role": "cambista"},
        {"first_name": "Ezequiel", "last_name": "Quintero", "username": "Ezequiel.Quintero", "password": "S8L1H7DX", "role": "cambista"},
        {"first_name": "Viviana", "last_name": "Raigemborn", "username": "Viviana.Raigemborn", "password": "U2C5K9MA", "role": "cambista"},
        {"first_name": "Diego", "last_name": "Ramirez", "username": "Diego.Ramirez", "password": "J7D4T6QP", "role": "cambista"},
        {"first_name": "Mario", "last_name": "Romero Cremades", "username": "Mario.Romero", "password": "X3F9L2HB", "role": "cambista"},
        {"first_name": "Gabriela", "last_name": "Romero", "username": "Gabriela.Romero", "password": "F1M6Q8ZR", "role": "cambista"},
        {"first_name": "Hector", "last_name": "Sampayo", "username": "Hector.Sampayo", "password": "Y9A2T4GK", "role": "cambista"},
        {"first_name": "Lorena", "last_name": "Sanchez", "username": "Lorena.Sanchez", "password": "H6W3D7PN", "role": "cambista"},
        {"first_name": "Telma", "last_name": "Toledo", "username": "Telma.Toledo", "password": "C2V8S9JL", "role": "cambista"},
        {"first_name": "Sergio", "last_name": "Vera", "username": "Sergio.Vera", "password": "P9Q5K1TR", "role": "cambista"},
        {"first_name": "Ariel", "last_name": "Zarate", "username": "Ariel.Zarate", "password": "M3N7F6YD", "role": "jefesala"},
        {"first_name": "Norma", "last_name": "Le Vraux", "username": "Norma.Levraux", "password": "A8J4Q2SM", "role": "jefesala"},
        {"first_name": "Telmo", "last_name": "Romero", "username": "Telmo.Romero", "password": "K5T9X1DV", "role": "jefesala"},
        {"first_name": "Walter", "last_name": "Michan Coiz", "username": "Walter.Levraux", "password": "Z7L3B6PA", "role": "jefesala"},
        {"first_name": "Benjamin", "last_name": "Costa", "username": "Benjamin.Costa", "password": "R2F8V9QH", "role": "jefesala"},
        {"first_name": "Enzo", "last_name": "Lirussi", "username": "Enzo.Lirussi", "password": "G9M4T1SW", "role": "jefesala"},
    ]

    # Create or update each operator account with the provided attributes.
    for entry in operator_accounts:
        user, _ = User.objects.get_or_create(username=entry["username"])
        user.first_name = entry["first_name"]
        user.last_name = entry["last_name"]
        user.role = entry["role"]
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.password = make_password(entry["password"])
        user.save()


def remove_operator_users(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    usernames = [
        "Cristian.Alarcon",
        "Liliana.Alfonzo",
        "Alicia.Benitez",
        "Cristian.Bernal",
        "Mauricio.Castillo",
        "Patricia.Castro",
        "Rita.Cespedes",
        "Federico.Fleitas",
        "Nelson.Foschiatti",
        "Noelia.Gonzalez",
        "Alejandra.Hernandez",
        "Analia.Hernandez",
        "Ulises.Leiva",
        "Gerardo.Lovato",
        "Diego.Luque",
        "Adrian.Medina",
        "Cecilia.Mercado",
        "Rodolfo.Oviedo",
        "Ezequiel.Quintero",
        "Viviana.Raigemborn",
        "Diego.Ramirez",
        "Mario.Romero",
        "Gabriela.Romero",
        "Hector.Sampayo",
        "Lorena.Sanchez",
        "Telma.Toledo",
        "Sergio.Vera",
        "Ariel.Zarate",
        "Norma.Levraux",
        "Telmo.Romero",
        "Walter.Levraux",
        "Benjamin.Costa",
        "Enzo.Lirussi",
    ]
    User.objects.filter(username__in=usernames).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_alter_user_role"),
    ]

    operations = [
        migrations.RunPython(create_operator_users, remove_operator_users),
    ]
