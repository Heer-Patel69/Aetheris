import sys
import unittest
from pathlib import Path

# Add scripts directory to path to allow importing compile_repo
scripts_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

import compile_repo

class TestCompileRepo(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(compile_repo.slugify("Hello World!"), "hello-world")
        self.assertEqual(compile_repo.slugify("Aetheris Engine OS v3.0"), "aetheris-engine-os-v30")

    def test_extract_references(self):
        sample_text = "This skill implements SPEC-040 (SRE Engine) and relates to RFC-003 (Skill Intelligence)."
        rfcs, specs = compile_repo.extract_references(sample_text)
        self.assertIn("RFC-003", rfcs)
        self.assertIn("SPEC-040", specs)
        self.assertEqual(len(rfcs), 1)
        self.assertEqual(len(specs), 1)

    def test_parse_markdown_sections(self):
        sample_md = """# Title
Some intro text here.

## Inputs
Input data structure is defined.

## Outputs
Output payload structure is returned.
"""
        sections = compile_repo.parse_markdown_sections(sample_md)
        self.assertIn("Introduction", sections)
        self.assertIn("Inputs", sections)
        self.assertIn("Outputs", sections)
        self.assertTrue("Input data structure" in sections["Inputs"])
        self.assertTrue("Output payload structure" in sections["Outputs"])

    def test_compiled_database_exists(self):
        # Verify that the data.json database was created by the compiler
        db_file = Path(__file__).resolve().parent.parent / "web" / "public" / "data.json"
        self.assertTrue(db_file.exists(), f"data.json does not exist at {db_file}")
        
        # Verify it loads as valid JSON
        import json
        with open(db_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertIn("skills", data)
        self.assertIn("rfcs", data)
        self.assertIn("specs", data)
        self.assertIn("docs", data)
        self.assertIn("search_index", data)
        self.assertIn("graph", data)
        
        # Verify we have entries
        self.assertTrue(len(data["skills"]) > 0, "No skills compiled in database")
        self.assertTrue(len(data["specs"]) > 0, "No specs compiled in database")

if __name__ == "__main__":
    unittest.main()
