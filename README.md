# Ciudad de la Suerte

## Flujo de configuración por terminal
- En el primer arranque el sistema calcula un identificador local usando el hostname y un UUID, lo guarda en `.terminal_identifier` y crea un registro de `SystemSettings` con `terminal_identifier`, `terminal_name` y `current_room_id` por defecto.
- En ejecuciones siguientes se reutiliza el mismo identificador almacenado en disco para recuperar el registro existente sin solicitar confirmaciones.
- Los administradores pueden renombrar el terminal o cambiar la sala desde Ajustes del sistema, pero siempre se conserva el `terminal_identifier` asignado a la máquina.

## Uso automático en registros y vouchers
- Los formularios de registro y de ingreso toman sala y terminal directamente desde `SystemSettings`, adjuntándolos a cupones y vouchers sin intervención del operador.
- La secuencia de cupones (`CouponSequence`) continúa siendo única por combinación de `room_id` y `terminal_name`, asegurando numeración separada por equipo y sala.
- Los códigos generados incluyen la sala y el terminal sanitizados; los vouchers quemados también almacenan estos datos para trazabilidad.

## Panel administrativo
- Dashboard, listados de cupones y reimpresiones ahora permiten filtrar tanto por sala como por terminal.
- El menú de configuración y la vista de ajustes permanecen visibles solo para usuarios administradores.
- Las tablas muestran sala y terminal donde corresponde para facilitar el control operativo.
