#!/usr/bin/env python3
"""A multi-commit push and interrupted releases in each packaging channel."""
from pathlib import Path
import json
import os
import runpy
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLIST = runpy.run_path(str(ROOT / "scripts/pending-formats"))["worklist"]


class PackageQueue(unittest.TestCase):
    def test_flatpak_queue(self):
        first, second, third = (c * 40 for c in "abc")
        # Old per-commit RPMs no longer count as anything pending.
        rpm = f"avernella-0.1.git77.{first[:7]}-1.x86_64.rpm"
        flat = f"avernella_0.1+git78.{second[:7]}_x86_64.flatpak"
        releases = {"avernella-" + first: {rpm}, "avernella-" + second: {flat}}
        pending = WORKLIST([first, second, third], releases)
        self.assertEqual(list(pending), ["flatpak"])
        self.assertEqual(pending["flatpak"], [first, second, third])
        releases["avernella-" + second].add(flat + ".sha256")
        self.assertEqual(WORKLIST([first, second, third], releases)["flatpak"],
                         [first, third])

    def test_debian_partial_releases(self):
        # Run the real gh JSON filter on synthetic API output without a token.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = dict(os.environ, PATH=f"{tmp}:" + os.environ["PATH"],
                       GITHUB_REPOSITORY="owner/packages", FIXTURE=tmp)
            def run(*cmd):
                return subprocess.check_output(cmd, env=env, cwd=root,
                                               text=True).strip()
            run("git", "init", "-q")
            commits = []
            for i in range(3):
                run("git", "-c", "user.name=Test", "-c", "user.email=test@example.org",
                    "commit", "-q", "--allow-empty", "-m", str(i))
                commits.append(run("git", "rev-parse", "HEAD"))
            names = ["avernella_1_amd64.deb", "avernella-source.tar.gz", "SHA256SUMS"]
            def release(sha, assets):
                return {"tag_name": "avernella-" + sha, "draft": False,
                        "assets": [{"name": n, "state": "uploaded", "size": 10}
                                   for n in assets]}
            (root / "releases").write_text(json.dumps([
                release(commits[0], names), release(commits[1], names[:1]),
                release(commits[2], ["avernella-x86_64.rpm"])]))
            gh = root / "gh"
            gh.write_text('#!/bin/bash\nexec jq -r "${!#}" "$FIXTURE/releases"\n')
            gh.chmod(0o755)
            self.assertEqual(run(ROOT / "scripts/pending", tmp).splitlines(),
                             commits[1:])

    def test_liney_recipe(self):
        recipe = ROOT / "liney/recipe"
        artifacts = ("1" * 64, "2" * 64)
        rendered = subprocess.check_output([recipe, "0.1.36", *artifacts],
                                           text=True)
        self.assertIn("pkgver=0.1.36\n", rendered)
        self.assertIn(f"sha256sums=('{artifacts[0]}' '{artifacts[1]}')", rendered)
        self.assertNotIn("@VERSION@", rendered)
        for version, deb_sum, license_sum in (
                ("0.01.36", *artifacts), ("0.1.36", "unknown", artifacts[1]),
                ("0.1.36", artifacts[0], "unknown")):
            rejected = subprocess.run([recipe, version, deb_sum, license_sum],
                                      capture_output=True, check=False)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(rejected.stdout, b"")


if __name__ == "__main__":
    unittest.main()
