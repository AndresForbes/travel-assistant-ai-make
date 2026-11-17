# Arquitectura técnica

El escenario está construido en **Make** y utiliza Telegram como interfaz conversacional. La lógica principal combina un modelo de lenguaje, almacenamiento de contexto y una herramienta para recuperar archivos desde Google Drive.

Esta documentación describe los módulos y las rutas presentes en el blueprint compartido.

## Flujo general

1. **Entrada — Telegram (`2`):** el disparador `telegram:WatchUpdates` recibe el mensaje del usuario.
2. **Contexto — Data Store (`20`):** se recupera el historial asociado al identificador del chat.
3. **Interpretación — Groq (`3`):** una petición HTTP envía el itinerario configurado, el contexto conversacional, el mensaje actual y la definición de la herramienta `buscar_documento`.
4. **Enrutamiento — Router (`5`):** separa las respuestas de texto de las solicitudes de herramienta.
5. **Respuesta conversacional (`4` y `21`):** envía la respuesta a Telegram y actualiza el historial.
6. **Recuperación documental (`10` y `16`):** interpreta el JSON de `buscar_documento` y realiza una búsqueda de archivos en Google Drive.
7. **Entrega (`12`, `8`, `11` y `22`):** si existen coincidencias, recupera el archivo, lo envía por Telegram y actualiza el historial.
8. **Sin coincidencias (`15` y `23`):** comunica el resultado de la búsqueda y actualiza el historial.
9. **Notificaciones:** los módulos Gmail `30`, `24`, `27` y `26` están asociados a rutas de error del módulo HTTP y del Data Store.

## Módulos principales

| ID | Módulo Make | Función |
|---:|---|---|
| 2 | `telegram:WatchUpdates` | Recibe mensajes |
| 20 | `datastore:GetRecord` | Recupera historial |
| 3 | `http:MakeRequest` | Llama al modelo alojado por Groq |
| 5 | `builtin:BasicRouter` | Decide la ruta según la respuesta |
| 4 | `telegram:SendReplyMessage` | Envía respuestas de texto |
| 21 | `datastore:AddRecord` | Actualiza historial en la ruta de texto |
| 10 | `json:ParseJSON` | Procesa argumentos de la herramienta |
| 16 | `google-drive:makeApiCall` | Consulta archivos con Google Drive API v3 |
| 12 | `builtin:BasicRouter` | Separa resultados con o sin coincidencias |
| 8 | `google-drive:getAFile` | Recupera el archivo |
| 11 | `telegram:SendDocument` | Envía el documento por Telegram |
| 22 | `datastore:AddRecord` | Actualiza historial tras el envío |
| 15 | `telegram:SendReplyMessage` | Informa cuando no hay coincidencias |
| 23 | `datastore:AddRecord` | Actualiza historial de la búsqueda |
| 30, 24, 27, 26 | `google-email:sendAnEmail` | Envía alertas de determinadas rutas de error |

## Integración de IA mediante function calling

La petición de Groq utiliza el modelo `openai/gpt-oss-120b`, con `tool_choice: auto`, y declara una herramienta llamada `buscar_documento`.

**Ejemplo ficticio de argumentos:**

```json
{
  "tipo_documento": "boleto",
  "destino_o_lugar": "Oporto",
  "pasajero": "Ana"
}
```

El parámetro `tipo_documento` es obligatorio; `destino_o_lugar` y `pasajero` son opcionales. El modelo interpreta la solicitud y genera los argumentos. La ejecución de la herramienta está a cargo de Make, mediante sus módulos de Google Drive.

## Búsqueda de archivos

El módulo `16` realiza una petición `GET /v3/files` a Google Drive API v3. La consulta se limita a una carpeta definida y combina criterios de tipo de documento, destino y pasajero cuando están presentes.

Se utiliza el operador `name contains`. En Google Drive, este operador busca coincidencias por prefijo de nombre; por eso la nomenclatura de archivos y la forma de combinar criterios son parte de la configuración que se debe validar para cada uso.

El módulo recupera los campos `id` y `name` para descargar el archivo seleccionado y entregarlo por Telegram. La búsqueda es por **metadatos del nombre**, sin analizar internamente el contenido de los documentos.

## Memoria conversacional

El escenario emplea un Data Store con un campo `Historial`, identificado por `message.chat.id`. La conversación previa se incorpora a la siguiente solicitud del modelo para mantener referencias contextuales entre mensajes.

Las rutas de guardado almacenan el historial concatenando los mensajes anteriores, el mensaje nuevo del usuario y el valor mapeado desde la respuesta del modelo.

## Alcance de esta versión

Esta implementación está orientada a un itinerario proporcionado en el mensaje de sistema y a una carpeta documental designada. La arquitectura permite explorar extensiones como índices de documentos, múltiples itinerarios y autorización de usuarios. Las propuestas de evolución se encuentran en [ROADMAP.md](ROADMAP.md).
