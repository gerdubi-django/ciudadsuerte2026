"""Local terms and conditions storage helpers."""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings

TERMS_CONFIG_FILENAME = "terms_config.json"
TERMS_CONFIG_PATH = Path(settings.BASE_DIR) / TERMS_CONFIG_FILENAME
DEFAULT_TERMS_TEXT = """“EL JUEGO COMPULSIVO ES PERJUDICIAL PARA LA SALUD Y PRODUCE ADICCIÓN. LEY 1647-C”
BASES Y CONDICIONES PROMOCIÓN
La ciudad de la suerte
PRIMERA: La participación en el concurso denominado “LA CIUDAD DE LA SUERTE” organizado
por Gala S.A., en adelante el organizador, implica el total conocimiento y aceptación de las siguientes
bases y condiciones por parte de los participantes, como así también los sistemas o procedimientos
establecidos por el organizador.
SEGUNDA: Esta promoción es válida desde el jueves 20 de noviembre de 2025 hasta el jueves 5
de marzo de 2026, exclusivamente para las siete (7) salas de Gala S.A., ubicadas en la Provincia del
Chaco. Participan las siguientes salas: Sala Güemes, sita en Güemes 250, Ciudad de Resistencia;
Sala Tropicana Castelli, ubicada en Av. Castelli 2727, Ciudad de Resistencia; Sala Ruta 11, en Ruta
Nacional N° 11, Kilómetro 1.003, Ciudad de Resistencia; Sala Sáenz Peña, en Roque Sáenz Peña
126, Ciudad de Resistencia; Sala Central, en Juan D. Perón 330, Ciudad de Resistencia; Sala
Tropicana Barranqueras, en Avenida Diagonal Eva Perón 560, Ciudad de Barranqueras; y Sala
Fontana, en Pasaje Augusto Rey S/N, Ciudad de Fontana.
TERCERA: 16.500.000 (dieciséis millones quinientos mil pesos) distribuidos en distintas salas de
Casinos Gala.
Los sorteos se realizarán a partir de las 21 horas, conforme al siguiente cronograma de fechas y
lugares:
1. 09/12/2025 Sala Fontana. Pasaje Augusto Rey S/N. Sorteo Primer Premio $150.000 (ciento
cincuenta mil pesos). Segundo y Tercer premio $50.000 (cincuenta mil pesos).
2. 11/12/2025 Sala Tropicana Barranqueras. Avenida Diagonal Eva Perón 560. Sorteo Primer
Premio $400.000 (cuatrocientos mil pesos). Segundo y Tercer premio $100.000 (cien mil
pesos).
3. 16/12/2025 Sala Sáenz Peña. Roque Sáenz Peña 126. Sorteo Primer Premio $450.000
(cuatrocientos cincuenta mil). Segundo y Tercer premio $150.000 (ciento cincuenta mil
pesos).
4. 18/12/2025 Sala Güemes. Güemes 250. Sorteo Primer Premio $450.000 (cuatrocientos
cincuenta mil). Segundo y Tercer premio $150.000 (ciento cincuenta mil pesos).
5. 23/12/2025 Sala Tropicana Castelli. Av. Castelli 2727. Sorteo Primer Premio $200.000
(doscientos mil pesos). Segundo y Tercer premio $75.000 (setenta y cinco mil pesos).
6. 25/12/2025 Sala Ruta 11. Ruta 11 Km 1.003. Sorteo Primer Premio $200.000 (doscientos mil
pesos). Segundo y Tercer premio $50.000 (cincuenta mil pesos).
7. 30/12/2025 Sala Central. Juan D. Perón 330. Sorteo Primer Premio $1.500.000 (un millón y
quinientos mil pesos). Segundo y Tercer premio $250.000 (doscientos cincuenta mil pesos).
“EL JUEGO COMPULSIVO ES PERJUDICIAL PARA LA SALUD Y PRODUCE ADICCIÓN. LEY 1647-C”
8. 06/01/2026 Sala Tropicana Barranqueras. Avenida Diagonal Eva Perón 560. Sorteo Primer
Premio $400.000 (cuatrocientos mil pesos). Segundo y Tercer premio $100.000 (cien mil
pesos).
9. 08/01/2026 Sala Fontana. Pasaje Augusto Rey S/N. Sorteo Primer Premio $150.000 (ciento
cincuenta mil pesos). Segundo y Tercer premio $50.000 (cincuenta mil pesos).
10.13/01/2026 Sala Ruta 11. Ruta 11 Km 1.003. Sorteo Primer Premio $200.000 (doscientos mil
pesos). Segundo y Tercer premio $50.000 (cincuenta mil pesos).
11.15/01/2026 Sala Tropicana Castelli. Av. Castelli 2727. Sorteo Primer Premio $200.000
(doscientos mil pesos). Segundo y Tercer premio $75.000 (setenta y cinco mil pesos).
12.20/01/2026 Sala Sáenz Peña. Roque Sáenz Peña 126. Sorteo Primer Premio $450.000
(cuatrocientos cincuenta mil). Segundo y Tercer premio $150.000 (ciento cincuenta mil
pesos).
13.22/01/2026 Sala Güemes. Güemes 250. Sorteo Primer Premio $450.000 (cuatrocientos
cincuenta mil). Segundo y Tercer premio $150.000 (ciento cincuenta mil pesos).
14.28/01/2026 Sala Central. Juan D. Perón 330. Sorteo Primer Premio $1.500.000 (un millón y
quinientos mil pesos). Segundo y Tercer premio $250.000 (doscientos cincuenta mil pesos).
15.10/02/2026 Sala Tropicana Barranqueras. Avenida Diagonal Eva Perón 560. Sorteo Primer
Premio $400.000 (cuatrocientos mil pesos). Segundo y Tercer premio $100.000 (cien mil
pesos).
16.12/02/2026 Sala Fontana. Pasaje Augusto Rey S/N. Sorteo Primer Premio $150.000 (ciento
cincuenta mil pesos). Segundo y Tercer premio $50.000 (cincuenta mil pesos).
17.17/02/2026 Sala Ruta 11. Ruta 11 Km 1.003. Sorteo Primer Premio $200.000 (doscientos mil
pesos). Segundo y Tercer premio $50.000 (cincuenta mil pesos).
18.19/02/2026 Sala Tropicana Castelli. Av. Castelli 2727. Sorteo Primer Premio $200.000
(doscientos mil pesos). Segundo y Tercer premio $75.000 (setenta y cinco mil pesos).
19.24/02/2026 Sala Sáenz Peña. Roque Sáenz Peña 126. Sorteo Primer Premio $450.000
(cuatrocientos cincuenta mil). Segundo y Tercer premio $150.000 (ciento cincuenta mil
pesos).
20.26/02/2026 Sala Güemes. Güemes 250. Sorteo Primer Premio $450.000 (cuatrocientos
cincuenta mil). Segundo y Tercer premio $150.000 (ciento cincuenta mil pesos).
21.05/03/2026 Sala Central. Juan D. Perón 330. Gran Sorteo Final. Primer Premio $2.000.000
(dos millones pesos). Segundo y Tercer premio $750.000 (setecientos cincuenta mil pesos).
CUARTA: Podrán participar del sorteo todas aquellas personas físicas, mayores de 18 años, que no
mantengan relación laboral, contractual o de parentesco hasta segundo grado con empleados
de Gala S.A. o de Hotel Gala S.A.
El organizador se reserva el derecho de determinar si algún participante o eventual ganador se
encuentra comprendido en alguna de las incompatibilidades establecidas en el párrafo anterior. Dicha
resolución tendrá carácter definitivo e inapelable.
“EL JUEGO COMPULSIVO ES PERJUDICIAL PARA LA SALUD Y PRODUCE ADICCIÓN. LEY 1647-C”
QUINTA: PARTICIPACIÓN EN EL SORTEO
De lunes a domingo se entregarán, en todas las salas de Casinos Gala y Salas de Juego Tropicana
mencionadas anteriormente, los cupones habilitados para participar del sorteo correspondiente a cada
fecha y sala.
El personal habilitado por el organizador (cajeros, asistentes técnicos y jefes de sala) asistirá en el
proceso de registro y validación de los participantes a través de una aplicación interna creada
especialmente para el concurso. Cada participante deberá registrarse una única vez en dicha
plataforma, completando sus datos personales requeridos.
Al realizar el registro, la aplicación generará automáticamente cinco (5) cupones con los datos del
participante, los cuales serán impresos y podrán ser depositados en las urnas habilitadas en cada una
de las salas de juego participantes.
Durante el desarrollo de la campaña, los participantes podrán obtener cupones adicionales
escaneando los tickets de las máquinas tragamonedas en cualquiera de las salas de Casinos Gala y
Casinos Tropicana. Asimismo, quienes adquieran créditos mediante los canales digitales habilitados
también serán acreedores de cupones adicionales.
La aplicación validará la identidad de los participantes mediante el número de Documento Nacional
de Identidad (DNI) o documento equivalente, impidiendo múltiples registros por persona.
No existe límite de participación, pudiendo cada persona depositar todos los cupones que haya
obtenido. Un mismo participante podrá concursar en todas las fechas programadas del sorteo, incluso
si resultara ganador en alguna de ellas; sin embargo, no podrá ser beneficiario de más de un premio
por fecha de sorteo.
Todos los cupones participantes en los distintos sorteos serán posteriormente recogidos y depositados
en la urna ubicada en la sala de Juan D. Perón 330, Ciudad de Resistencia, para la realización del
sorteo final el día 05/03/2026.
SEXTA: Los sorteos serán fiscalizados por un escribano público designado por el organizador, quien
labrará el acta correspondiente consignando los datos de los ganadores y toda otra circunstancia que
considere pertinente.
El sorteo se llevará a cabo en las fechas y lugares establecidos en la Cláusula Tercera del presente
documento. En cada jornada de sorteo se procederá a la extracción de tres (3) cupones, cuyos
titulares serán los ganadores de los premios asignados para esa fecha.
En todos los casos, si alguno de los cupones seleccionados presentara irregularidades o incumpliera
con los requisitos establecidos, conforme la revisión del escribano presente, se procederá a extraer
un nuevo cupón hasta obtener un beneficiario válido, según lo determine la autoridad de constatación.
Para ser considerado ganador del premio, será condición obligatoria estar presente al momento del
sorteo. Se considerará “presente” al participante que se encuentre físicamente dentro de la sala de
juego al momento de la extracción. Si el titular del cupón no se encontrara presente, se esperará un
lapso máximo de cinco (5) minutos, tras lo cual se procederá a extraer un nuevo cupón, repitiéndose
este procedimiento hasta obtener un ganador presente en la sala.
“EL JUEGO COMPULSIVO ES PERJUDICIAL PARA LA SALUD Y PRODUCE ADICCIÓN. LEY 1647-C”
SEPTIMA: El organizador se reserva el derecho de modificar las presentes bases y condiciones
cuando lo considere necesario para asegurar la correcta ejecución del concurso. Dichas
modificaciones serán informadas a los participantes mediante su exhibición en lugares visibles de las
salas o a través de los medios que el organizador estime pertinentes.
Las modificaciones serán de aplicación inmediata; sin embargo, no podrán alterar la igualdad de
condiciones entre los participantes ni afectar los derechos adquiridos por éstos.
OCTAVA: El solo hecho de participar en los sorteos implica el pleno conocimiento y aceptación de las
presentes bases y condiciones, así como la expresa sujeción a las disposiciones contenidas en ellas.
Los participantes autorizan expresamente al organizador a difundir su nombre, datos personales,
voz e imagen, por los medios y en la forma que éste considere apropiada, con fines publicitarios y/o
promocionales vinculados al concurso, sin derecho a compensación alguna.
El tratamiento de los datos personales recabados se realizará conforme a lo establecido en la Ley
N° 25.326 de Protección de Datos Personales y sus modificatorias, garantizando su confidencialidad
y el ejercicio de los derechos de acceso, rectificación y supresión previstos en dicha norma.
NOVENA: Las eventuales acciones judiciales que pudieran corresponder a los participantes por circunstancias
acaecidas fuera de las establecidas en este reglamento y dentro de las salas, por daños y perjuicios ocasionados
por terceros sobre bienes o sobre las personas de los mismos, no generarán responsabilidad alguna para el
organizador.
Los participantes renuncian expresamente a toda acción o reclamo contra el organizador por tales causas, sin
perjuicio de las que pudieran ejercer contra los terceros responsables.
Ante cualquier divergencia que pudiera surgir con relación a esta promoción y a todos sus efectos, los
participantes y el organizador se someten a la jurisdicción y competencia de los tribunales ordinarios de la
Ciudad de Resistencia, renunciando a cualquier otro fuero que pudiera corresponderles, incluso el federal."""


def get_terms_config_path() -> Path:
    """Return the absolute path to the local terms configuration file."""

    return TERMS_CONFIG_PATH


def get_terms_config() -> dict[str, str]:
    """Load terms from disk and create the file with defaults when needed."""

    path = get_terms_config_path()
    if not path.exists():
        payload = {"terms_text": DEFAULT_TERMS_TEXT}
        path.write_text(json.dumps(payload, indent=4, ensure_ascii=False), encoding="utf-8")
        return payload

    try:
        raw_data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        raw_data = {}

    terms_text = str(raw_data.get("terms_text") or "").strip() or DEFAULT_TERMS_TEXT
    payload = {"terms_text": terms_text}
    path.write_text(json.dumps(payload, indent=4, ensure_ascii=False), encoding="utf-8")
    return payload


def get_terms_text(fallback: str = "") -> str:
    """Return the local terms body with an optional fallback."""

    local_terms = get_terms_config().get("terms_text", "").strip()
    if local_terms:
        return local_terms
    return fallback.strip() or DEFAULT_TERMS_TEXT


def save_terms_config(terms_text: str) -> dict[str, str]:
    """Persist edited terms and conditions in the local configuration file."""

    payload = {"terms_text": str(terms_text or "").strip() or DEFAULT_TERMS_TEXT}
    path = get_terms_config_path()
    path.write_text(json.dumps(payload, indent=4, ensure_ascii=False), encoding="utf-8")
    return payload
