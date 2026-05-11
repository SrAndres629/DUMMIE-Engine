import unittest
import sys
import os

# Ensure the project root is in sys.path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from layers.l2_brain.cognitive_hooks import classify_authority_level

class TestAuthorityClassification(unittest.TestCase):
    def test_a0_basic_query_and_explanations(self):
        self.assertEqual(classify_authority_level("How does the brain work?"), "A0")
        self.assertEqual(classify_authority_level("What is DUMMIE?"), "A0")
        self.assertEqual(classify_authority_level("Can you explain what sudo does?"), "A0")
        self.assertEqual(classify_authority_level("analiza tokens de contexto"), "A0")
        self.assertEqual(classify_authority_level("revisa driver architecture documentation"), "A0")
        self.assertEqual(classify_authority_level("analiza estrategia de Facebook"), "A0")
        self.assertEqual(classify_authority_level("qué es un archivo .env"), "A0")

    def test_a1_workspace_edit(self):
        self.assertEqual(classify_authority_level("Edit the README.md to add a title"), "A1")
        self.assertEqual(classify_authority_level("Refactor this function in main.py"), "A1")
        self.assertEqual(classify_authority_level("Crea un archivo de prueba"), "A1")
        self.assertEqual(classify_authority_level("edit README.md"), "A1")
        self.assertEqual(classify_authority_level("refactor model_router.py"), "A1")

    def test_a2_build_and_install(self):
        self.assertEqual(classify_authority_level("npm install lodash"), "A2")
        self.assertEqual(classify_authority_level("Run the tests with pytest"), "A2")
        self.assertEqual(classify_authority_level("Build the docker container"), "A2")
        self.assertEqual(classify_authority_level("run pytest"), "A2")

    def test_a3_workstation_ui(self):
        self.assertEqual(classify_authority_level("Open the browser and go to google.com"), "A3")
        self.assertEqual(classify_authority_level("Usa chrome para buscar noticias"), "A3")
        self.assertEqual(classify_authority_level("Start a gui session"), "A3")
        self.assertEqual(classify_authority_level("open Chrome"), "A3")
        self.assertEqual(classify_authority_level("usa Playwright para revisar la UI"), "A3")

    def test_a4_external_action(self):
        self.assertEqual(classify_authority_level("Publish this to twitter"), "A4")
        self.assertEqual(classify_authority_level("Send an email to the team"), "A4")
        self.assertEqual(classify_authority_level("Publica en instagram el resumen"), "A4")
        self.assertEqual(classify_authority_level("post this to TikTok"), "A4")

    def test_a5_critical_and_sensitive(self):
        self.assertEqual(classify_authority_level("sudo apt install nvidia-driver"), "A5")
        self.assertEqual(classify_authority_level("Delete all credentials in .env"), "A5")
        self.assertEqual(classify_authority_level("Modifica los secretos del kernel"), "A5")
        self.assertEqual(classify_authority_level("Update payment tokens"), "A5")
        self.assertEqual(classify_authority_level("sudo rm -rf /"), "A5")
        self.assertEqual(classify_authority_level("edita .env"), "A5")
        self.assertEqual(classify_authority_level("delete credentials"), "A5")
        self.assertEqual(classify_authority_level("actualiza drivers NVIDIA"), "A5")

    def test_false_positive_prevention(self):
        # "edit" is A1, but "tweet" makes it A4
        self.assertEqual(classify_authority_level("Edit my last tweet"), "A4")
        # "sudo" alone is A0 if it's an explanation
        self.assertEqual(classify_authority_level("What is sudo?"), "A0")
        # "sudo" followed by a command is A5
        self.assertEqual(classify_authority_level("run sudo ls"), "A5")

if __name__ == "__main__":
    unittest.main()
