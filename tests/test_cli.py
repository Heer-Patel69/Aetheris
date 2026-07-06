import os
import sys
import json
import unittest
import tempfile
from unittest.mock import patch, MagicMock, PropertyMock
from io import StringIO
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from kernel.cli import (
    AetherisRuntime, AetherisDoctor, AetherisInstaller,
    RuntimeState, get_runtime_dir, get_runtime_subdirs,
    __version__, BANNER, RUNTIME_STATE_FILE, PID_FILE,
    cmd_start, cmd_stop, cmd_status, cmd_doctor, cmd_version,
    cmd_update, cmd_chat, cmd_install, cmd_uninstall, main
)


class TestVersion(unittest.TestCase):
    def test_version_defined(self):
        self.assertTrue(len(__version__) > 0)
        self.assertEqual(__version__, "1.0.0")

    def test_runtime_subdirs(self):
        subdirs = get_runtime_subdirs()
        expected = ["models", "memory", "skills", "cache", "logs", "journal", "config", "runtime"]
        self.assertEqual(subdirs, expected)

    def test_banner_contains_aetheris(self):
        self.assertIn("AETHERIS", BANNER.upper())


class TestRuntimeState(unittest.TestCase):
    def test_default_state(self):
        state = RuntimeState()
        self.assertEqual(state.runtime_status, "stopped")
        self.assertEqual(state.brain_status, "unloaded")
        self.assertIsNone(state.pid)
        self.assertIsNone(state.start_time)

    def test_state_serialization(self):
        state = RuntimeState(version="1.0.0", runtime_status="active", skills_loaded=42)
        d = state.to_dict()
        self.assertEqual(d["version"], "1.0.0")
        self.assertEqual(d["runtime_status"], "active")
        self.assertEqual(d["skills_loaded"], 42)

        restored = RuntimeState.from_dict(d)
        self.assertEqual(restored.version, "1.0.0")
        self.assertEqual(restored.skills_loaded, 42)

    def test_state_with_pid(self):
        state = RuntimeState(pid=12345, start_time=1000.0)
        d = state.to_dict()
        self.assertEqual(d["pid"], 12345)
        self.assertEqual(d["start_time"], 1000.0)


class TestAetherisRuntime(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('kernel.cli.get_runtime_dir')
        self.mock_get_dir = self.patcher.start()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_runtime = Path(self.temp_dir) / ".aetheris"
        self.mock_get_dir.return_value = self.temp_runtime

    def tearDown(self):
        self.patcher.stop()
        import shutil
        if self.temp_runtime.exists():
            shutil.rmtree(self.temp_runtime)

    def test_initialization(self):
        runtime = AetherisRuntime()
        self.assertFalse(runtime.is_running())

    def test_initialize_directories(self):
        runtime = AetherisRuntime()
        result = runtime.initialize_directories()
        self.assertTrue(result)

        # Verify all subdirs created
        for subdir in get_runtime_subdirs():
            self.assertTrue((self.temp_runtime / subdir).exists(), f"Missing: {subdir}")

        # Verify config created
        config_file = self.temp_runtime / "config" / "aetheris.yaml"
        self.assertTrue(config_file.exists())

        # Verify memory subdirs
        memory_dir = self.temp_runtime / "memory"
        for d in ["episodic", "semantic", "procedural", "working"]:
            self.assertTrue((memory_dir / d).exists(), f"Missing memory subdir: {d}")

    def test_start_stop_lifecycle(self):
        runtime = AetherisRuntime()
        runtime.initialize_directories()

        # Start
        result = runtime.start(foreground=False)
        self.assertTrue(result)
        self.assertTrue(runtime.is_running())
        self.assertEqual(runtime.state.runtime_status, "active")

        # Can't double-start
        result2 = runtime.start(foreground=False)
        self.assertFalse(result2)

        # Stop
        result3 = runtime.stop()
        self.assertTrue(result3)
        self.assertFalse(runtime.is_running())
        self.assertEqual(runtime.state.runtime_status, "stopped")

    def test_state_persistence(self):
        runtime = AetherisRuntime()
        runtime.initialize_directories()
        runtime.start(foreground=False)
        runtime.stop()

        # State file should exist
        self.assertTrue(RUNTIME_STATE_FILE.exists())

        # Load state from file
        with open(RUNTIME_STATE_FILE) as f:
            data = json.load(f)
        self.assertEqual(data["runtime_status"], "stopped")
        self.assertIn("version", data)

    def test_get_status(self):
        runtime = AetherisRuntime()
        runtime.initialize_directories()
        runtime.start(foreground=False)

        status = runtime.get_status()
        self.assertEqual(status["version"], __version__)
        self.assertEqual(status["runtime"], "active")
        self.assertIn("platform", status)
        self.assertIn("python_version", status)

        runtime.stop()


class TestAetherisDoctor(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('kernel.cli.get_runtime_dir')
        self.mock_get_dir = self.patcher.start()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_runtime = Path(self.temp_dir) / ".aetheris"
        self.mock_get_dir.return_value = self.temp_runtime

        # Initialize runtime for doctor tests
        self.runtime = AetherisRuntime()
        self.runtime.initialize_directories()

    def tearDown(self):
        self.patcher.stop()
        import shutil
        if self.temp_runtime.exists():
            shutil.rmtree(self.temp_runtime)

    def test_doctor_runtime_installed_check(self):
        doctor = AetherisDoctor()
        result = doctor._check_runtime_installed()
        self.assertTrue(result)

    def test_doctor_configuration_check(self):
        doctor = AetherisDoctor()
        result = doctor._check_configuration()
        self.assertTrue(result)

    def test_doctor_skills_check(self):
        doctor = AetherisDoctor()
        result = doctor._check_skills()
        self.assertTrue(result)

    def test_doctor_memory_check(self):
        doctor = AetherisDoctor()
        result = doctor._check_memory()
        self.assertTrue(result)

    def test_doctor_environment_check(self):
        doctor = AetherisDoctor()
        result = doctor._check_environment()
        self.assertTrue(result)

    def test_doctor_permissions_check(self):
        doctor = AetherisDoctor()
        result = doctor._check_permissions()
        self.assertTrue(result)

    def test_doctor_run_all(self):
        doctor = AetherisDoctor()
        result = doctor.run_all_checks()
        self.assertTrue(result)
        self.assertEqual(len(doctor.checks), 9)


class TestAetherisInstaller(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('kernel.cli.get_runtime_dir')
        self.mock_get_dir = self.patcher.start()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_runtime = Path(self.temp_dir) / ".aetheris"
        self.mock_get_dir.return_value = self.temp_runtime

    def tearDown(self):
        self.patcher.stop()
        import shutil
        if self.temp_runtime.exists():
            shutil.rmtree(self.temp_runtime)

    def test_install(self):
        installer = AetherisInstaller()
        result = installer.install()
        self.assertTrue(result)

        # Verify directories were created
        for subdir in get_runtime_subdirs():
            self.assertTrue((self.temp_runtime / subdir).exists())

    def test_uninstall(self):
        installer = AetherisInstaller()
        installer.install()
        result = installer.uninstall()
        self.assertTrue(result)
        self.assertFalse(self.temp_runtime.exists())

    def test_update(self):
        installer = AetherisInstaller()
        result = installer.update()
        self.assertTrue(result)


class TestCLICommands(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('kernel.cli.get_runtime_dir')
        self.mock_get_dir = self.patcher.start()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_runtime = Path(self.temp_dir) / ".aetheris"
        self.mock_get_dir.return_value = self.temp_runtime

    def tearDown(self):
        self.patcher.stop()
        import shutil
        if self.temp_runtime.exists():
            shutil.rmtree(self.temp_runtime)

    def test_cmd_version_output(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            mock_args = MagicMock()
            cmd_version(mock_args)
            output = fake_out.getvalue()
            self.assertIn(__version__, output)

    def test_cmd_doctor_output(self):
        # Initialize directories first
        runtime = AetherisRuntime()
        runtime.initialize_directories()
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                mock_args = MagicMock()
                cmd_doctor(mock_args)
            # Doctor should pass on fresh install
            self.assertEqual(cm.exception.code, 0)

    def test_cmd_install_output(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                mock_args = MagicMock()
                mock_args.method = "pip"
                cmd_install(mock_args)
            self.assertEqual(cm.exception.code, 0)

    def test_cmd_uninstall_output(self):
        # First install
        installer = AetherisInstaller()
        installer.install()

        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                mock_args = MagicMock()
                cmd_uninstall(mock_args)
            self.assertEqual(cm.exception.code, 0)

    def test_cmd_start_stop(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            mock_args = MagicMock()
            mock_args.foreground = False
            mock_args.f = False
            cmd_start(mock_args)
            output = fake_out.getvalue()
            self.assertIn("Starting", output)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            mock_args = MagicMock()
            cmd_stop(mock_args)
            output = fake_out.getvalue()
            self.assertIn("Stopping", output)

    def test_cmd_status_output(self):
        # Start first
        runtime = AetherisRuntime()
        runtime.initialize_directories()
        runtime.start(foreground=False)

        with patch('sys.stdout', new=StringIO()) as fake_out:
            mock_args = MagicMock()
            cmd_status(mock_args)
            output = fake_out.getvalue()
            self.assertIn("STATUS", output.upper())

        runtime.stop()

    def test_cmd_update_output(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            mock_args = MagicMock()
            cmd_update(mock_args)
            output = fake_out.getvalue()
            self.assertIn("Updating", output)


class TestCLIMainEntry(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('kernel.cli.get_runtime_dir')
        self.mock_get_dir = self.patcher.start()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_runtime = Path(self.temp_dir) / ".aetheris"
        self.mock_get_dir.return_value = self.temp_runtime

    def tearDown(self):
        self.patcher.stop()
        import shutil
        if self.temp_runtime.exists():
            shutil.rmtree(self.temp_runtime)

    @patch('sys.argv', ['aetheris', '--help'])
    def test_help_output(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

    @patch('sys.argv', ['aetheris', 'version'])
    def test_version_command(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            self.assertIn(__version__, output)

    @patch('sys.argv', ['aetheris'])
    def test_no_args_shows_banner(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            self.assertIn("AETHERIS", output.upper())


if __name__ == "__main__":
    unittest.main()
