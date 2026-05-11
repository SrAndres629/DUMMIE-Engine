import unittest
import os
import shutil
from layers.l2_brain.mission_workbench import MissionWorkbenchManager

class TestMissionWorkbench(unittest.TestCase):
    def setUp(self):
        self.test_dir = ".aiwg/test_workbench"
        self.manager = MissionWorkbenchManager(base_path=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_workbench(self):
        mission_id = "test_mission"
        manifest = self.manager.create_workbench(mission_id, "session1", "test goal")
        
        self.assertEqual(manifest["mission_id"], mission_id)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, mission_id, "manifest.json")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, mission_id, "objective.md")))

    def test_write_artifact_security(self):
        mission_id = "test_sec"
        self.manager.create_workbench(mission_id, "s1", "g")
        
        with self.assertRaises(ValueError):
            self.manager.write_artifact(mission_id, ".env", "SECRET=123", "env")
            
        with self.assertRaises(ValueError):
            self.manager.write_artifact(mission_id, "../../config.py", "malicious", "python")

    def test_append_decision_log(self):
        mission_id = "test_log"
        self.manager.create_workbench(mission_id, "s1", "g")
        
        self.manager.append_decision(mission_id, {"action": "test", "internal_monologue": "private"})
        
        log_path = os.path.join(self.test_dir, mission_id, "decision_log.jsonl")
        with open(log_path, "r") as f:
            log_entry = f.readline()
            data = json.loads(log_entry)
            self.assertEqual(data["action"], "test")
            self.assertNotIn("internal_monologue", data)

    def test_finalize(self):
        mission_id = "test_fin"
        self.manager.create_workbench(mission_id, "s1", "g")
        result = self.manager.finalize_workbench(mission_id, {"status": "SUCCESS"})
        
        self.assertEqual(result["status"], "finalized")
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, mission_id, "final_summary.md")))

import json
if __name__ == "__main__":
    unittest.main()
