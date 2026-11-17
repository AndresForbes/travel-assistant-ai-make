# Configuración y puesta en marcha

El archivo `blueprints/asistente-viaje.public.blueprint.json` contiene valores ficticios y referencias sin configurar; **no se debe activar tal cual**.

## Requisitos

- Cuenta Make con acceso a los módulos usados y capacidad de crear un Data Store.
- Bot de Telegram creado y controlado por quien despliega.
- Cuenta y API key vigente de Groq, almacenada de manera segura en Make.
- Cuenta Google Drive con acceso a una carpeta de documentos de prueba.
- Cuenta Gmail para notificaciones (opcional; si se conserva el manejo de errores existente).
- Documentos de prueba **ficticios** para verificar el flujo antes de usar información personal.

## Importar el blueprint

1. En Make, crea un **escenario nuevo**.
2. En el editor, usa el menú de tres puntos → **Import blueprint** y selecciona el JSON público.
3. Guarda el escenario después de revisar la configuración y las conexiones. La importación no restituye tus credenciales de servicios externos.
4. Si Make muestra problemas al importar por los identificadores de conexión vacíos, vuelve a seleccionar la conexión o recrea el módulo afectado. La compatibilidad de importación de esta versión anonimizada **no fue validada en una cuenta Make**.

Referencia: [Make — Scenario blueprints](https://help.make.com/blueprints).

## Configurar módulos

| Módulo | Qué configurar |
|---|---|
| **2 — Telegram trigger** | Crear/reconectar bot y webhook; revisar qué tipos de mensaje acepta |
| **20, 21, 22, 23 — Data Store** | Crear almacén de registros con campo de texto `Historial`; seleccionar el mismo almacén en todos |
| **3 — HTTP / Groq** | Establecer credencial nueva, modelo compatible, verificar `POST`, `messages` y definición de `buscar_documento` |
| **3 — System prompt** | Cambiar únicamente el itinerario ficticio por uno verdadero en entorno privado, sin publicarlo en GitHub |
| **16 — Google Drive API** | Reconectar cuenta; sustituir `REEMPLAZAR_ID_CARPETA_DRIVE` por una carpeta propia; verificar permisos y criterios `q` |
| **8 — Google Drive file** | Reconectar cuenta; comprobar cómo selecciona una coincidencia y entrega el contenido binario |
| **4, 11, 15 — Telegram output** | Reconectar bot y confirmar chat de destino |
| **30, 24, 27, 26 — Gmail** | Reconectar remitente; sustituir `avisos@example.invalid` por una dirección que controles |


## Convención de archivos

La búsqueda del blueprint usa `name contains` y criterios acumulativos con `and`. Es importante que cada término necesario sea compatible con el **comienzo** del nombre del archivo. El mecanismo original puede resultar restrictivo cuando solicita simultáneamente tipo, ciudad y pasajero. Para pruebas reproducibles, primero usa casos simples con un solo criterio y luego verifica las combinaciones. Consulta [`examples/nombres-archivos.txt`](../examples/nombres-archivos.txt).

