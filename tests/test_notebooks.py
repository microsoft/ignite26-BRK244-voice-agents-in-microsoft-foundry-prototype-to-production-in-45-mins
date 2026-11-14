import ast
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NotebookTests(unittest.TestCase):
    def test_notebooks_are_clean_and_code_compiles(self):
        names = [
            "01_quickstart_voice_session.ipynb",
            "02_turn_taking_and_barge_in.ipynb",
            "03_multilingual_code_switching.ipynb",
        ]
        for name in names:
            with self.subTest(notebook=name):
                notebook = json.loads((ROOT / "src/notebooks" / name).read_text())
                self.assertEqual(notebook["nbformat"], 4)
                self.assertEqual(notebook["metadata"]["kernelspec"]["name"], "brk244")
                code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
                self.assertGreaterEqual(len(code_cells), 2)
                for cell in code_cells:
                    self.assertIsNone(cell["execution_count"])
                    self.assertEqual(cell["outputs"], [])
                    compile("".join(cell["source"]), name, "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)

    def test_new_attendee_links_resolve(self):
        paths = [ROOT / "README.md", *list((ROOT / "instructions").glob("*.md")), ROOT / "docs/capabilities.md"]
        for path in paths:
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text()):
                if target.startswith(("https://", "http://", "#")):
                    continue
                with self.subTest(page=path.name, target=target):
                    self.assertTrue((path.parent / target.split("#")[0]).exists())

if __name__ == "__main__":
    unittest.main()
