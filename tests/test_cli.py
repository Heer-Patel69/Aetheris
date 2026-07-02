import sys
import unittest
from unittest.mock import patch
from io import StringIO
from pathlib import Path

# Add src to sys.path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from kernel.core import main

class TestCLI(unittest.TestCase):
    @patch('sys.argv', ['aetheris', '--version'])
    def test_version_long(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)
            self.assertIn("Aetheris Kernel v3.1.0", fake_out.getvalue())

    @patch('sys.argv', ['aetheris', '-v'])
    def test_version_short(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)
            self.assertIn("Aetheris Kernel v3.1.0", fake_out.getvalue())

if __name__ == "__main__":
    unittest.main()
