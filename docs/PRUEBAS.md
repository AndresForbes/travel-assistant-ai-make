# Plan de pruebas y criterios de aceptación

**Estado:** casos definidos, **no ejecutados contra el escenario real**. Solo se incluyeron verificaciones estáticas del archivo compartible. La aceptación requiere una instancia Make con credenciales de prueba.

| Caso | Entrada / condición | Resultado esperado |
|---|---|---|
| T01 | «¿Cuál es la ruta del viaje?» | Respuesta coherente con el itinerario inyectado |
| T02 | Preguntar por una fecha no incluida | No inventa datos; indica que no consta |
| T03 | «Envíame el boleto de tren» con único archivo coincidente | Llamada `buscar_documento`, descarga y envío correcto por Telegram |
| T04 | Solicitar un documento inexistente | Mensaje de búsqueda sin coincidencias |
| T05 | «Envíame el boleto» → «El de Ana» | Reutilización del contexto, sin repetir preguntas ya contestadas |
| T06 | Pedir documentos con dos nombres similares | No entregar documento incorrecto: desambiguar o aplicar criterio explícito (mejora pendiente) |
| T07 | Mensaje de foto o nota de voz sin `message.text` | No provocar ejecución incorrecta: filtrar/tratar explícitamente (mejora pendiente) |
| T08 | Chat no autorizado | Acceso denegado antes de Groq o Drive (control pendiente) |
| T09 | Error HTTP de Groq | Notificación o fallback comprobable; revisar ruta de error |
| T10 | Error de Data Store | Alerta recibida y recuperación verificada sin pérdida silenciosa |
| T11 | Error de Google Drive o permiso insuficiente | Respuesta controlada; no publicar información interna (mejora pendiente) |
| T12 | Historial vacío en primera interacción | Flujo válido y registro inicial creado |
| T13 | Conversación extensa | Historial acotado y coste/latencia aceptables (mejora pendiente) |
| T14 | Boleto `reserva_tren_...` al buscar `tren` | Identificar limitación de coincidencia por prefijo; ajustar estrategia |
| T15 | Solicitud con criterios de ciudad + pasajero | Comprobar comportamiento de `if(10.destino_o_lugar + 10.pasajero; ...)` |
| T16 | Archivo duplicado / varias coincidencias | Documentar selección y evitar entrega equivocada (mejora pendiente) |

## Cómo registrar resultados

Para cada caso anotar fecha, versión de escenario, datos ficticios de entrada, módulos ejecutados, resultado de Telegram, efecto en Data Store, coste aproximado/operaciones Make y evidencia **sin datos personales ni tokens**.

## Calidad del blueprint público

La validación incluida en `scripts/check_blueprint.py` comprueba estructura JSON, presencia de módulos clave, formato del body de Groq y patrones evidentes de secretos. Los tests unitarios replican comprobaciones estáticas. 
