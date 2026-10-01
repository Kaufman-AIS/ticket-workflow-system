import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("patch-paca-caddy.py")


class PatchPacaCaddyTests(unittest.TestCase):
    def test_adds_discovery_scorer_route_and_is_idempotent(self):
        initial = """site {
	# -- ChatGPT remote MCP (OAuth gateway) ----------------------------------------
	handle /mcp {
		reverse_proxy paca-chatgpt-mcp:8771
	}
	# -- Web application (SPA) -----------------------------------------------------
	handle {
		reverse_proxy web:3000
	}
}
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            caddyfile = Path(temp_dir) / "Caddyfile"
            caddyfile.write_text(initial)

            subprocess.run([sys.executable, str(SCRIPT), str(caddyfile)], check=True)
            patched = caddyfile.read_text()

            self.assertIn("method POST path /hooks/discovery-score", patched)
            self.assertIn("rewrite * /score", patched)
            self.assertIn("reverse_proxy discovery-scorer:8091", patched)

            subprocess.run([sys.executable, str(SCRIPT), str(caddyfile)], check=True)
            self.assertEqual(caddyfile.read_text().count("/hooks/discovery-score"), 1)


if __name__ == "__main__":
    unittest.main()
