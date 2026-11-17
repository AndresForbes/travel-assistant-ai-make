# Plan de pruebas

La validación del proyecto contempla dos niveles: **pruebas estáticas del blueprint público** y **pruebas funcionales del escenario configurado en Make**.

## Validaciones automáticas

El repositorio incluye verificaciones offline para confirmar la estructura del archivo JSON, los módulos esperados, la definición de `buscar_documento` y patrones habituales de credenciales. Estas comprobaciones se ejecutan en GitHub Actions.

```bash
python3 scripts/check_blueprint.py
python3 -m unittest discover -s tests -v
```

Estas pruebas comprueban el archivo exportado. Las pruebas funcionales requieren ejecutar el escenario de Make con conexiones y datos de demostración.

## Casos funcionales

| Caso | Consulta o situación | Resultado esperado |
|---|---|---|
| T01 | Pregunta sobre el itinerario configurado | Respuesta basada en la información proporcionada |
| T02 | Solicitud de información que no consta en el itinerario | Respuesta que indique la ausencia de ese dato |
| T03 | Solicitud de un documento con coincidencia única | Interpretación de la solicitud y envío por Telegram |
| T04 | Solicitud de documento sin coincidencias | Mensaje de búsqueda sin resultados |
| T05 | Solicitud inicial seguida de una aclaración, como «El de Ana» | Interpretación de la referencia usando historial |
| T06 | Reinicio o primera conversación de un chat | Recuperación o inicialización coherente del historial |
| T07 | Error de comunicación con Groq | Activación de la ruta de alerta correspondiente |
| T08 | Error al guardar el historial | Activación de la notificación configurada |

## Pruebas de ampliación

Como parte de futuras iteraciones, se pueden incorporar casos adicionales: solicitudes con múltiples archivos coincidentes, mensajes que no sean de texto, control de chats autorizados, conversaciones largas y búsqueda avanzada con varios criterios.

## Registro de evidencias

Para documentar una ejecución se pueden registrar la fecha, la versión del escenario, los datos ficticios de entrada, los módulos ejecutados y el resultado observado en Telegram y Data Store.

**Estado de las pruebas:** la validación automatizada del blueprint forma parte del repositorio. La matriz funcional se proporciona como plan reproducible; no se presenta como un conjunto de resultados ya ejecutados en esta publicación.
