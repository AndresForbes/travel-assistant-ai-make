"""Offline structural tests. These do not execute Make or call service APIs."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_blueprint import BLUEPRINT, all_modules, inspect_blueprint


class BlueprintStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(BLUEPRINT.read_text(encoding='utf-8'))
        cls.modules = list(all_modules(cls.doc['flow']))

    def test_security_markers(self):
        self.assertEqual([], inspect_blueprint())

    def test_topology(self):
        self.assertEqual(18, len(self.modules))
        self.assertEqual(2, sum(m['module'] == 'builtin:BasicRouter' for m in self.modules))
        self.assertEqual(4, sum(m['module'] == 'google-email:sendAnEmail' for m in self.modules))

    def test_function_tool_contract(self):
        m = next(m for m in self.modules if m['module'] == 'http:MakeRequest')
        body = json.loads(m['mapper']['jsonStringBodyContent'])
        tool = next(t['function'] for t in body['tools'] if t['function']['name'] == 'buscar_documento')
        self.assertEqual(['tipo_documento'], tool['parameters']['required'])
        self.assertEqual({'tipo_documento', 'destino_o_lugar', 'pasajero'}, set(tool['parameters']['properties']))
        self.assertEqual('auto', body['tool_choice'])

    def test_public_template_is_not_deployable_without_setup(self):
        m = next(m for m in self.modules if m['module'] == 'google-drive:makeApiCall')
        self.assertIn('REEMPLAZAR_ID_CARPETA_DRIVE', m['mapper']['qs'][0]['value'])
        m = next(m for m in self.modules if m['module'] == 'http:MakeRequest')
        self.assertIn('REEMPLAZAR_CON_API_KEY_DE_GROQ', str(m['mapper']['headers']))
        self.assertIn('ITINERARIO FICTICIO', json.loads(m['mapper']['jsonStringBodyContent'])['messages'][0]['content'])


if __name__ == '__main__':
    unittest.main()
