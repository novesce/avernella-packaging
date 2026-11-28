#!/usr/bin/env python3
"""Check the minimal data passed into the package publishing runners."""
import io
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SHA = "b" * 40
DIGEST = "c" * 64
DEB = "avernella_0.1+git42.bbbbbbb_amd64.deb"


class ReleaseBoundaries(unittest.TestCase):
    def render(self, metadata):
        root = Path(self.tmp.name)
        info = root / "build-info"
        info.write_bytes(metadata)
        return subprocess.run([ROOT / "scripts/aur-render", DEB, SHA, DIGEST,
                               info, root / "recipe"], capture_output=True)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)

    def test_render_arch_recipe(self):
        self.assertEqual(self.render(b"3\n11\n1\n").returncode, 0)
        recipe = self.directory / "recipe"
        self.assertIn("libvpx.so=11-64", (recipe / "PKGBUILD").read_text())
        self.assertIn("optdepends = wpewebkit", (recipe / ".SRCINFO").read_text())
        self.assertIn(f"/avernella-{SHA}/{DEB}", (recipe / ".SRCINFO").read_text())

        if shutil.which("makepkg") and os.geteuid() != 0:
            actual = subprocess.check_output(["makepkg", "--printsrcinfo"],
                                             cwd=recipe, text=True)
            self.assertEqual((recipe / ".SRCINFO").read_text(), actual)

        self.assertEqual(self.render(b"3\n11\n0\n").returncode, 0)
        self.assertNotIn("wpewebkit", (recipe / "PKGBUILD").read_text())

    def test_refuse_invalid_arch_metadata(self):
        for metadata in [b"3\n11\n1\n0\n", b"3\nlibvpx\n1\n", b"3\n11\n9\n",
                         b"3\n11\n1\n" + b"x" * 32]:
            self.assertNotEqual(self.render(metadata).returncode, 0)
        self.assertFalse((self.directory / "recipe").exists())

    def unpack(self, item, data):
        archive = self.directory / "site.tar"
        with tarfile.open(archive, "w") as output:
            item.size = len(data)
            output.addfile(item, io.BytesIO(data))
        return subprocess.run(["python3", ROOT / "scripts/unpack-static-repo",
                               archive, self.directory / "site"],
                              capture_output=True)

    def test_accept_static_payload(self):
        result = self.unpack(tarfile.TarInfo("./objects/ab/file.commit"), b"dummy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.directory / "site/objects/ab/file.commit").read_bytes(),
                         b"dummy")

    def test_refuse_static_links(self):
        link = tarfile.TarInfo("./refs/head")
        link.type = tarfile.SYMTYPE
        link.linkname = "published"
        self.assertNotEqual(self.unpack(link, b"").returncode, 0)
        self.assertFalse((self.directory / "site/refs/head").is_symlink())


if __name__ == "__main__":
    unittest.main()
