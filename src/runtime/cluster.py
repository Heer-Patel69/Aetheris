class ClusterManager:
    def __init__(self):
        self.nodes = {}
        self.leader = None

    def register_node(self, node_id, address):
        self.nodes[node_id] = {
            "address": address,
            "status": "HEALTHY"
        }
        if not self.leader:
            self.leader = node_id
        print(f"[Cluster] Registered node '{node_id}' at {address}. Leader: '{self.leader}'")
        return True

    def get_leader(self):
        return self.leader

    def heartbeat(self, node_id):
        if node_id in self.nodes:
            self.nodes[node_id]["status"] = "HEALTHY"
            return True
        return False
