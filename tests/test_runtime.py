import unittest
from pathlib import Path
from runtime import AutonomousRuntimeEngine, SandboxedExecutor, IPCManager, RPCServer, ClusterManager

class TestRuntime(unittest.TestCase):
    def setUp(self):
        self.workspace_path = Path("c:/AI/Agency owner/aetheris/scratch/test_runtime_workspace")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.runtime = AutonomousRuntimeEngine(self.workspace_path)

    def test_sandbox_execution(self):
        executor = SandboxedExecutor(self.workspace_path)
        res = executor.execute("python -c \"print('Sandbox Test')\"")
        self.assertTrue(res["success"])
        self.assertIn("Sandbox Test", res["stdout"])

    def test_sandbox_path_validation(self):
        executor = SandboxedExecutor(self.workspace_path)
        self.assertTrue(executor.is_safe(self.workspace_path / "src" / "app.py"))
        self.assertFalse(executor.is_safe("c:/Windows/System32/cmd.exe"))

    def test_ipc_channels(self):
        ipc = IPCManager()
        self.assertTrue(ipc.publish("test-channel", {"event": "START"}))
        events = ipc.read_channel("test-channel")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "START")

    def test_rpc_methods(self):
        server = RPCServer()
        server.register_method("add", lambda x, y: x + y)
        res = server.call("add", 10, 20)
        self.assertEqual(res, 30)

    def test_cluster_nodes(self):
        cluster = ClusterManager()
        self.assertTrue(cluster.register_node("node-1", "http://127.0.0.1:8001"))
        self.assertEqual(cluster.get_leader(), "node-1")
        self.assertTrue(cluster.heartbeat("node-1"))
