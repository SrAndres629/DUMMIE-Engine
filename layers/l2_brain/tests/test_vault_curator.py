import unittest
import os
import shutil
import json
from layers.l2_brain.vault_curator import VaultCurator

class TestVaultCurator(unittest.TestCase):
    def setUp(self):
        self.test_vault = ".aiwg/test_vault"
        self.test_wb = ".aiwg/test_wb_for_vault"
        os.makedirs(self.test_wb, exist_ok=True)
        self.curator = VaultCurator(vault_path=self.test_vault)

    def tearDown(self):
        if os.path.exists(self.test_vault):
            shutil.rmtree(self.test_vault)
        if os.path.exists(self.test_wb):
            shutil.rmtree(self.test_wb)

    def test_extract_golden_path(self):
        # Setup mock successful workbench
        mission_id = "m_win"
        os.makedirs(os.path.join(self.test_wb, mission_id), exist_ok=True)
        wb_path = os.path.join(self.test_wb, mission_id)
        
        with open(os.path.join(wb_path, "manifest.json"), "w") as f:
            json.dump({"mission_id": mission_id}, f)
        with open(os.path.join(wb_path, "outcome_metrics.json"), "w") as f:
            json.dump({"status": "SUCCESS", "goal": "win everything"}, f)
        with open(os.path.join(wb_path, "final_summary.md"), "w") as f:
            f.write("I won.")
            
        entries = self.curator.extract_vault_entries(mission_id, wb_path)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["entry_type"], "golden_path")

    def test_security_rejection(self):
        entry = {
            "vault_id": "test",
            "mission_id": "m1",
            "entry_type": "decision",
            "summary": "found my API_KEY_HERE",
            "created_at": "now"
        }
        with self.assertRaises(ValueError):
            self.curator.store_vault_entry(entry)

    def test_finalize_and_clean(self):
        mission_id = "m_final"
        wb_path = os.path.join(self.test_wb, mission_id)
        os.makedirs(wb_path, exist_ok=True)
        
        with open(os.path.join(wb_path, "manifest.json"), "w") as f:
            json.dump({"mission_id": mission_id}, f)
        with open(os.path.join(wb_path, "outcome_metrics.json"), "w") as f:
            json.dump({"status": "SUCCESS"}, f)
        with open(os.path.join(wb_path, "final_summary.md"), "w") as f:
            f.write("Success summary")
            
        result = self.curator.finalize_and_clean(mission_id, wb_path)
        self.assertEqual(result["entries_promoted"], 1)
        self.assertTrue(os.path.exists(result["stored_paths"][0]))

if __name__ == "__main__":
    unittest.main()
