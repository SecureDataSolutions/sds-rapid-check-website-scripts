import contextlib
import io
import runpy
import socket
import sys
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "third_party_scripts.py"
FIXTURE = ROOT / "tests" / "fixtures" / "page.html"


class OfflineFileTests(unittest.TestCase):
    def test_file_mode_requires_site_and_uses_saved_html_without_network(self):
        output = io.StringIO()
        arguments = [str(SCRIPT), "--file", str(FIXTURE), "--site", "https://www.example.com"]
        with patch.object(sys, "argv", arguments), \
                patch.object(urllib.request, "build_opener", side_effect=AssertionError("network used")), \
                patch.object(urllib.request, "urlopen", side_effect=AssertionError("network used")), \
                patch.object(socket, "create_connection", side_effect=AssertionError("network used")), \
                patch.object(socket, "socket", side_effect=AssertionError("network used")), \
                contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(SCRIPT), run_name="__main__")
        self.assertEqual(result.exception.code, 0)

        self.assertIn("cdn.example.net", output.getvalue())
        self.assertIn("1 with an integrity attribute", output.getvalue())
        self.assertNotIn("www.example.com (", output.getvalue())
        self.assertIn("No finding is not proof of no compromise", output.getvalue())

    def test_file_mode_requires_site(self):
        with patch.object(sys, "argv", [str(SCRIPT), "--file", str(FIXTURE)]), \
                patch.object(urllib.request, "build_opener", side_effect=AssertionError("network used")), \
                patch.object(socket, "create_connection", side_effect=AssertionError("network used")), \
                patch.object(socket, "socket", side_effect=AssertionError("network used")), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(SCRIPT), run_name="__main__")
        self.assertEqual(result.exception.code, 2)

    def test_empty_file_with_address_is_rejected_without_network(self):
        build_opener = patch.object(urllib.request, "build_opener", side_effect=AssertionError("network used"))
        with patch.object(sys, "argv", [str(SCRIPT), "--file", "", "https://example.net", "--site", "https://example.com"]), \
                build_opener as opener, \
                patch.object(urllib.request, "urlopen", side_effect=AssertionError("network used")), \
                patch.object(socket, "create_connection", side_effect=AssertionError("network used")), \
                patch.object(socket, "socket", side_effect=AssertionError("network used")), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(SCRIPT), run_name="__main__")

        self.assertEqual(result.exception.code, 2)
        opener.assert_not_called()

    def test_empty_file_uses_offline_path_without_network(self):
        output = io.StringIO()
        build_opener = patch.object(urllib.request, "build_opener", side_effect=AssertionError("network used"))
        with patch.object(sys, "argv", [str(SCRIPT), "--file", "", "--site", "https://example.com"]), \
                build_opener as opener, \
                patch.object(urllib.request, "urlopen", side_effect=AssertionError("network used")), \
                patch.object(socket, "create_connection", side_effect=AssertionError("network used")), \
                patch.object(socket, "socket", side_effect=AssertionError("network used")), \
                contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(SCRIPT), run_name="__main__")

        self.assertEqual(result.exception.code, 1)
        self.assertIn("could not read saved page", output.getvalue())
        opener.assert_not_called()


if __name__ == "__main__":
    unittest.main()
