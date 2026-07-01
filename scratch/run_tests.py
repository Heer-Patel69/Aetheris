import sys
import os
sys.path.insert(0, os.path.abspath("src"))
import pytest
sys.exit(pytest.main(["-v"]))
