"""Behavior checks for persisted selections and the local preview server boundary.

Run: python3 -m unittest discover -s /path/to/design-previews/scripts -p 'test_*.py'
Fixtures are synthetic; browser/visual evaluation is a separate forward-test.
"""

import argparse
import base64
import json
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from urllib.parse import urlsplit

import pipeline


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="design-pipeline-test-")
        self.addCleanup(self.temporary.cleanup)
        self.run = Path(self.temporary.name) / "run"
        pipeline.init_run(argparse.Namespace(count=3, title="Synthetic fixture", project=None, run_dir=str(self.run)))
        self.candidate = self.run / "candidates/design-1"

    def complete_candidate(self):
        (self.candidate / "source/index.html").write_text("<h1>Fixture</h1>")
        (self.candidate / "preview/index.html").write_text("<h1>Fixture</h1>")
        pipeline.write_json(self.candidate / "tokens.json", {"color": {"text": "#222222"}})
        (self.candidate / "handoff.md").write_text("Synthetic structure-test fixture, not a reviewed design.")
        (self.candidate / "evidence/verification.md").write_text("This one-pixel image is test fixture data, not visual QA.")
        (self.candidate / "evidence/design-review.md").write_text("Synthetic fixture review.\nVerdict: ready\n")
        (self.candidate / "evidence/fixture.png").write_bytes(base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="))
        pipeline.validate_output(self.candidate)
        record = pipeline.read_json(self.candidate / "candidate.json")
        record.update(status="ready", revision=pipeline.fingerprint(self.candidate))
        pipeline.write_json(self.candidate / "candidate.json", record)
        return record["revision"]

    def start_server(self):
        process = subprocess.Popen([sys.executable, str(Path(pipeline.__file__)), "serve", "--run", str(self.run)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.server_process = process

        def stop():
            process.terminate()
            process.communicate(timeout=5)

        self.addCleanup(stop)
        line = process.stdout.readline()
        self.assertTrue(line, "Server exited without publishing its URL")
        published = json.loads(line)
        self.previews = published["previews"]
        return published["url"]

    def test_aborted_preview_requests_do_not_log_server_errors(self):
        (self.candidate / "preview/large.bin").write_bytes(b"x" * (8 * 1024 * 1024))
        url = self.start_server()
        address = urlsplit(url)
        with socket.create_connection((address.hostname, address.port), timeout=5) as client:
            client.sendall(("GET /candidates/design-1/preview/large.bin HTTP/1.1\r\nHost: " +
                            address.netloc + "\r\n\r\n").encode())
            self.assertTrue(client.recv(1024))
            client.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
        # Let the worker observe the reset while another request verifies continued service.
        with self.request(url + "/candidates/design-1/preview/large.bin") as response:
            self.assertEqual(response.status, 200)
        time.sleep(0.05)
        self.server_process.terminate()
        _, errors = self.server_process.communicate(timeout=5)
        self.assertEqual(errors, "")

    def request(self, url, data=None, origin=None):
        headers = {"Origin": origin} if origin else {}
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = Request(url, data=json.dumps(data).encode() if data is not None else None, headers=headers)
        return urlopen(request, timeout=5)

    def test_fresh_run_keeps_requested_count_and_has_no_choice(self):
        state = pipeline.inspect_run(self.run)
        self.assertEqual(len(state["candidates"]), 3)
        self.assertIsNone(state["selection"])
        self.assertFalse(state["selectionValid"])
        self.assertFalse(any(c["selectable"] for c in state["candidates"]))

    def test_init_never_overwrites_an_existing_run(self):
        with self.assertRaises(FileExistsError):
            pipeline.init_run(argparse.Namespace(count=1, title="Overwrite", project=None, run_dir=str(self.run)))
        self.assertEqual(pipeline.manifest(self.run)["title"], "Synthetic fixture")

    def test_incomplete_candidate_cannot_be_sealed_or_chosen(self):
        with self.assertRaises(ValueError):
            pipeline.validate_output(self.candidate)
        with self.assertRaises(ValueError):
            pipeline.choose(self.run, "design-1", "not-ready", "user-chat", "Simulated test choice")
        self.assertFalse((self.run / "selection.json").exists())

    def test_source_edit_invalidates_choice_and_old_revision(self):
        revision = self.complete_candidate()
        pipeline.choose(self.run, "design-1", revision, "user-chat", "Simulated test choice")
        self.assertTrue(pipeline.inspect_run(self.run)["selectionValid"])
        (self.candidate / "source/index.html").write_text("<h1>Changed</h1>")
        self.assertFalse(pipeline.inspect_run(self.run)["selectionValid"])
        with self.assertRaises(ValueError):
            pipeline.choose(self.run, "design-1", revision, "user-chat", "Simulated stale choice")
        self.assertEqual(pipeline.read_json(self.run / "selection.json")["revision"], revision)

    def test_wrong_revision_rejected_without_replacing_valid_choice(self):
        revision = self.complete_candidate()
        pipeline.choose(self.run, "design-1", revision, "user-chat", "Simulated test choice")
        with self.assertRaises(ValueError):
            pipeline.choose(self.run, "design-1", "different", "user-chat", "Simulated stale choice")
        self.assertTrue(pipeline.inspect_run(self.run)["selectionValid"])

    def test_resealing_requires_new_explicit_choice(self):
        revision = self.complete_candidate()
        pipeline.choose(self.run, "design-1", revision, "user-chat", "Simulated test choice")
        (self.candidate / "preview/index.html").write_text("<h1>New fixture revision</h1>")
        record = pipeline.read_json(self.candidate / "candidate.json")
        record["revision"] = pipeline.fingerprint(self.candidate)
        pipeline.write_json(self.candidate / "candidate.json", record)
        self.assertFalse(pipeline.inspect_run(self.run)["selectionValid"])
        with self.assertRaises(ValueError):
            pipeline.choose(self.run, "design-1", revision, "user-chat", "Simulated old choice")
        pipeline.choose(self.run, "design-1", record["revision"], "user-chat", "Simulated renewed choice")
        self.assertTrue(pipeline.inspect_run(self.run)["selectionValid"])

    def test_unfinished_review_cannot_be_sealed(self):
        self.complete_candidate()
        (self.candidate / "evidence/design-review.md").write_text("Verdict: ready\nOne more finding\n")
        with self.assertRaises(ValueError):
            pipeline.validate_output(self.candidate)
        (self.candidate / "evidence/design-review.md").write_text("Scores\nVerdict: needs fixes\n")
        pipeline.validate_output(self.candidate)

    def test_dependency_caches_do_not_change_revision(self):
        revision = self.complete_candidate()
        cache = self.candidate / "source/node_modules/example"
        cache.mkdir(parents=True)
        (cache / "index.js").write_text("dependency fixture")
        self.assertEqual(pipeline.fingerprint(self.candidate), revision)

    def test_symlinks_are_rejected_in_portable_artifacts(self):
        self.complete_candidate()
        (self.candidate / "preview/linked").symlink_to(self.run / "manifest.json")
        with self.assertRaises(ValueError):
            pipeline.fingerprint(self.candidate)

    def test_server_publishes_one_preview_url_per_ready_design(self):
        self.complete_candidate()
        url = self.start_server()
        self.assertEqual(self.previews, {"design-1": url + "/candidates/design-1/preview/index.html"})
        with self.request(self.previews["design-1"]) as response:
            self.assertEqual(response.read(), b"<h1>Fixture</h1>")

    def test_server_restricts_files_and_cross_origin_writes(self):
        revision = self.complete_candidate()
        (self.candidate / "preview" / "page.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
        url = self.start_server()
        for route in ("/manifest.json", "/candidates/design-1/source/index.html",
                      "/candidates/design-1/preview/%2e%2e/tokens.json"):
            with self.assertRaises(HTTPError) as result:
                self.request(url + route)
            self.assertEqual(result.exception.code, 404)
        for route in ("/api/selection", "/api/likes", "/api/notes"):
            with self.assertRaises(HTTPError) as result:
                self.request(url + route, {"candidateId": "design-1", "revision": revision}, url)
            self.assertEqual(result.exception.code, 501)
        self.assertFalse((self.run / "selection.json").exists())
        # App browser panes block sandboxed pages' external scripts, so previews carry no sandbox policy.
        with self.request(url + "/candidates/design-1/preview/index.html") as response:
            self.assertIsNone(response.headers["Content-Security-Policy"])


if __name__ == "__main__":
    unittest.main()
