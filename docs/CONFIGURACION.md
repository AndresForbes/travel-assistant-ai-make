# Configuración del escenario

El [blueprint compartido](../blueprints/asistente-viaje.public.blueprint.json) es una versión **anonimizada** del escenario Make. Incluye datos de ejemplo y marcadores para que cada persona pueda conectar sus propios servicios.

## Requisitos

- Una cuenta de **Make** con acceso a los módulos y a un Data Store.
- Un bot propio de **Telegram**.
- Una clave de API válida de **Groq**.
- Acceso a una carpeta de **Google Drive** con archivos de prueba.
- Una conexión de **Gmail** para las alertas opcionales.
- Un itinerario y documentos ficticios con los que validar el funcionamiento.

## Importar en Make

1. Crear un escenario en Make.
2. Abrir el menú de tres puntos del editor y seleccionar **Import blueprint**.
3. Elegir el archivo `blueprints/asistente-viaje.public.blueprint.json`.
4. Reconectar los módulos que requieran autenticación y configurar los identificadores propios.
5. Guardar y probar el flujo con datos ficticios.

La importación de este blueprint anonimizado todavía no se ha verificado en una segunda cuenta de Make; algunas referencias deben asignarse de nuevo desde el editor.

Documentación oficial: [Scenario blueprints — Make](https://help.make.com/blueprints).

## Configuración por módulo

| Módulo | Configuración |
|---|---|
| **2 — Telegram** | Vincular el bot y registrar el webhook |
| **20, 21, 22 y 23 — Data Store** | Crear un almacén con campo de texto `Historial` y seleccionarlo en los cuatro módulos |
| **3 — HTTP / Groq** | Configurar un método seguro para la credencial de Groq; revisar modelo, mensajes y herramienta `buscar_documento` |
| **3 — Instrucciones del asistente** | Sustituir el itinerario ficticio del mensaje de sistema por el correspondiente a la instancia privada |
| **16 — Búsqueda en Google Drive** | Conectar la cuenta y sustituir `REEMPLAZAR_ID_CARPETA_DRIVE` por el identificador de una carpeta propia |
| **8 — Descarga de Google Drive** | Conectar la cuenta y comprobar la recuperación de los archivos |
| **4, 11 y 15 — Respuestas Telegram** | Vincular el bot para los mensajes de texto y archivos |
| **30, 24, 27 y 26 — Alertas Gmail** | Conectar Gmail y personalizar la dirección de notificaciones ficticia |

## Organización de los archivos

El mecanismo de búsqueda utiliza el nombre de los archivos y combina los criterios disponibles. Conviene definir una nomenclatura consistente y probar cómo se comporta `name contains` cuando se agregan criterios de tipo, destino y pasajero.

Hay ejemplos ficticios en [examples/nombres-archivos.txt](../examples/nombres-archivos.txt).

## Validación

La puesta en marcha se completa comprobando los flujos de texto, la recuperación de documentos, las conversaciones con contexto y las alertas correspondientes. Los casos están organizados en [PRUEBAS.md](PRUEBAS.md).

Los documentos reales, las credenciales y los datos de los viajeros permanecen en la instancia privada de Make y Google Drive, no en este repositorio.
