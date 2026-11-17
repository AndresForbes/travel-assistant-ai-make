# Arquitectura técnica del escenario

## Fuente y criterio de documentación

Esta documentación se basa en el blueprint JSON exportado del escenario «Asistente de viaje». Se distingue **configuración observada en el archivo** de **funcionamiento verificado**: no hay logs, pruebas en vivo ni accesos a las cuentas que permitan confirmar el resultado de cada ejecución. El blueprint público conserva la topología original, pero elimina identificadores y datos personales.

## Flujo principal

1. **Recepción**: módulo `2` `telegram:WatchUpdates`. Recibe actualizaciones del bot. El escenario utiliza `message.chat.id`, `message.chat.first_name` y `message.text`; el diseño presupone mensajes de texto.
2. **Contexto**: módulo `20` `datastore:GetRecord`. Obtiene el campo `Historial` desde un Data Store cuya clave es el identificador de chat.
3. **IA**: módulo `3` `http:MakeRequest`. Invoca `POST https://api.groq.com/openai/v1/chat/completions`. El body usa `model: openai/gpt-oss-120b`, mensajes de sistema/usuario, historial y una herramienta declarada `buscar_documento`. `tool_choice` está en `auto`.
4. **Decisión**: módulo `5` `builtin:BasicRouter`. Divide el procesamiento según la presencia de texto en `message.content` o una solicitud de herramienta `buscar_documento` en `message.tool_calls`.
5. **Texto**: módulo `4` envía respuesta por Telegram y módulo `21` intenta actualizar el historial.
6. **Documento**: módulo `10` `json:ParseJSON` interpreta los argumentos de la herramienta. Módulo `16` `google-drive:makeApiCall` ejecuta `GET /v3/files` filtrando por carpeta, tipo de documento y criterios opcionales.
7. **Documento encontrado**: router `12` selecciona módulo `8` `google-drive:getAFile` → módulo `11` `telegram:SendDocument` → módulo `22` `datastore:AddRecord`.
8. **Sin documentos**: router `12` selecciona módulo `15` `telegram:SendReplyMessage` → módulo `23` `datastore:AddRecord`.
9. **Alertas**: módulos Gmail `30`, `24`, `27` y `26` asociados a ciertas rutas de error del HTTP de IA y de escritura del Data Store.

## Inventario de módulos

| ID | Módulo | Responsabilidad |
|---:|---|---|
| 2 | `telegram:WatchUpdates` | Entrada vía Telegram |
| 20 | `datastore:GetRecord` | Recuperar historial por `chat.id` |
| 3 | `http:MakeRequest` | Petición a Groq con herramienta declarada |
| 5 | `builtin:BasicRouter` | Separar respuesta textual / llamada de herramienta |
| 4 | `telegram:SendReplyMessage` | Respuesta textual |
| 21 | `datastore:AddRecord` | Guardar conversación tras texto |
| 10 | `json:ParseJSON` | Analizar argumentos de `buscar_documento` |
| 16 | `google-drive:makeApiCall` | Buscar archivos por nombre |
| 12 | `builtin:BasicRouter` | Resultado encontrado / sin coincidencias |
| 8 | `google-drive:getAFile` | Recuperar contenido binario del archivo |
| 11 | `telegram:SendDocument` | Enviar archivo |
| 22 | `datastore:AddRecord` | Guardar conversación tras envío |
| 15 | `telegram:SendReplyMessage` | Mensaje de búsqueda sin resultados |
| 23 | `datastore:AddRecord` | Guardar conversación tras búsqueda vacía |
| 30, 24, 27, 26 | `google-email:sendAnEmail` | Alertas relacionadas con ciertas fallas |

## Contrato de la herramienta

Declarada en la solicitud a Groq como una función con argumentos JSON:

```json
{
  "tipo_documento": "boleto",
  "destino_o_lugar": "Oporto",
  "pasajero": "Ana"
}
```

`tipo_documento` es obligatorio. Los demás son opcionales. Los datos son criterios de búsqueda, no identificadores exactos de reservas. **El modelo solo propone los argumentos**; Google Drive se consulta posteriormente por módulos de Make.

## Localización de documentos

El módulo `16` ejecuta Google Drive API v3 `files.list` sobre una carpeta específica (ID sustituido por marcador en la plantilla pública), con una consulta `q` que combina:

- `'ID_CARPETA' in parents`
- `name contains 'tipo_documento'`
- `name contains 'destino_o_lugar'` cuando aplica
- `name contains 'pasajero'` cuando aplica
- `trashed = false`

Solicita únicamente `files(id, name)`. El operador `name contains` de Google Drive es una coincidencia **por prefijo** (no una búsqueda por palabra en cualquier parte del nombre); por eso importa una convención estable de nombres. Google Drive también filtra solo hijos directos con `in parents`, no descendientes arbitrarios.

## Estado y persistencia

El Data Store conserva un campo de texto `Historial`, asociado a la clave `chat.id`. Las rutas de guardado concatenan el historial anterior, el último mensaje del usuario y `choices[1].message.content`. En respuestas de *tool calling* ese `content` puede ser nulo o vacío; es posible que la búsqueda o el envío del documento no se reflejen adecuadamente como evento en el historial.

## Controles y errores

El escenario incorpora avisos Gmail cuando falla el módulo de Groq y cuando falla alguna de las escrituras del historial. Tenemos pendiente la aplicación de controles de autorización de remitentes, validación de entrada para mensajes no textuales y tratamiento explícito de resultados múltiples, fallos de lectura de Drive, fallos de envío Telegram o ausencia del registro inicial del Data Store. Las alertas usan mensajes estáticos y no constituyen prueba de recuperación automática.

## Decisión de ingeniería

La solución es una **automatización con IA y una herramienta de recuperación de archivos**. Puede describirse también como un **asistente conversacional con tool calling**. Por el momento no sería preciso presentarla como RAG, asistente documental semántico o agente autónomo, porque esos componentes no aparecen en el blueprint.
