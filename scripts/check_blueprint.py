#!/usr/bin/env python3
"""Validation of the shareable Make blueprint (offline/static, no external calls).

This is a defensive check for *some* common errors. It is not a privacy audit.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / 'blueprints' / 'asistente-viaje.public.blueprint.json'
REQUIRED_MODULES = {
    'telegram:WatchUpdates', 'datastore:GetRecord', 'datastore:AddRecord',
    'http:MakeRequest', 'builtin:BasicRouter', 'json:ParseJSON',
    'google-drive:makeApiCall', 'google-drive:getAFile',
    'telegram:SendDocument', 'telegram:SendReplyMessage',
    'google-email:sendAnEmail',
}


def all_modules(flow):
    """Traverse Make routers and onerror branches."""
    for module in flow:
        yield module
        for route in module.get('routes', []):
            yield from all_modules(route.get('flow', []))
        yield from all_modules(module.get('onerror', []))


def inspect_blueprint(path=BLUEPRINT):
    """Return human-readable errors; never send input data to a third party."""
    errors = []
    if not Path(path).is_file():
        return [f'Blueprint no encontrado: {path}']
    raw = Path(path).read_text(encoding='utf-8')
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [f'JSON inválido: {exc}']
    if not isinstance(doc, dict) or not isinstance(doc.get('flow'), list):
        return ['No es un blueprint Make con lista flow']
    modules = list(all_modules(doc['flow']))
    kinds = {m.get('module') for m in modules}
    missing = REQUIRED_MODULES - kinds
    if missing:
        errors.append(f'Faltan módulos esperados: {sorted(missing)}')
    if len(modules) != 18:
        errors.append(f'Se esperaban 18 módulos (incluidas rutas de error); encontrados {len(modules)}')
    ids = [m.get('id') for m in modules]
    if len(ids) != len(set(ids)):
        errors.append('Hay IDs de módulo duplicados')

    # Straightforward indicators only — additional human review is mandatory.
    patterns = {
        'Posible clave de Groq': r'(?i)\bgsk_[A-Za-z0-9]{15,}',
        'Posible token GitHub': r'(?i)\b(?:ghp_|gho_|ghu_|ghs_|github_pat_)[A-Za-z0-9_]{12,}',
        'Posible clave OpenAI': r'\bsk-[A-Za-z0-9_-]{16,}',
        'Teléfono internacional': r'\+\d{9,15}',
            }
    for name, pattern in patterns.items():
        if re.search(pattern, raw):
            errors.append(name)
    folder_ids = re.findall(r"'([A-Za-z0-9_-]{22,})'(?= in parents)", raw)
    if any(item != 'REEMPLAZAR_ID_CARPETA_DRIVE' for item in folder_ids):
        errors.append('ID real de carpeta Drive en consulta')
    emails = re.findall(r'\b[A-Za-z0-9_.+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', raw)
    if any(not address.lower().endswith('@example.invalid') for address in emails):
        errors.append('Aparece una dirección de correo que no es de ejemplo')
    if 'REEMPLAZAR_CON_API_KEY_DE_GROQ' not in raw or 'REEMPLAZAR_ID_CARPETA_DRIVE' not in raw:
        errors.append('Faltan marcadores de configuración en la plantilla pública')

    http = [m for m in modules if m.get('module') == 'http:MakeRequest']
    if len(http) == 1:
        try:
            body = json.loads(http[0]['mapper']['jsonStringBodyContent'])
            funcs = [entry.get('function', {}).get('name') for entry in body.get('tools', [])]
            if 'buscar_documento' not in funcs:
                errors.append('Falta la definición de herramienta buscar_documento')
            if not body.get('messages'):
                errors.append('La solicitud a Groq no contiene mensajes')
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'Body Groq no es un JSON válido: {type(exc).__name__}')
    else:
        errors.append('Se esperaba un solo módulo HTTP para Groq')
    for m in modules:
        for name, value in m.get('parameters', {}).items():
            if name in ('__IMTCONN__', '__IMTHOOK__', 'datastore') and value is not None:
                errors.append(f'Identificador no anonimizado en módulo {m.get("id")}')
    return errors


def main():
    errors = inspect_blueprint()
    if errors:
        print('ERROR: problemas detectados en el blueprint público:')
        for issue in errors:
            print(f' - {issue}')
        return 1
    print('OK: blueprint público JSON válido; módulos y patrones básicos revisados.')
    print('AVISO: se requiere revisión manual de seguridad y prueba de importación/ejecución en Make.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
