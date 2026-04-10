import importlib
import unittest


class ImportTests(unittest.TestCase):
    def test_server_module_imports(self):
        module = importlib.import_module("illustrator.server")
        self.assertTrue(callable(module.main))

    def test_cli_exposes_run_server(self):
        module = importlib.import_module("illustrator.cli")
        self.assertTrue(callable(module.run_server))

    def test_platform_backend_imports(self):
        module = importlib.import_module("illustrator.platform_backend")
        self.assertTrue(callable(module.get_backend))
        self.assertTrue(hasattr(module, "IllustratorBackend"))
        self.assertTrue(hasattr(module, "MacBackend"))
        self.assertTrue(hasattr(module, "WindowsBackend"))

    def test_prompt_module_imports(self):
        module = importlib.import_module("illustrator.prompt")
        self.assertTrue(callable(module.get_system_prompt))
        self.assertTrue(callable(module.get_prompt_suggestions))


if __name__ == "__main__":
    unittest.main()
