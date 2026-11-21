# Avernella Debian packages

[Download the latest amd64 package](https://github.com/novesce/avernella-packaging/releases/latest) for [Avernella](https://github.com/novesce/avernella). Use the Ubuntu release identified in the release notes.

```sh
sudo apt install ./avernella_*_amd64.deb
```

The package includes the executable, desktop launcher, icon, and WebKitGTK helper. The build also includes the WPE WebKit helper when Ubuntu provides the WPE Wayland SDK. Avernella prefers WPE on Wayland when available.

The [GitHub Actions workflow](.github/workflows/packages.yml) runs on `ubuntu-latest`. A push to Avernella’s `main` branch queues packaging. A scheduled check picks up any commits that still lack a release, including commits pushed together. Each published release includes the tested `.deb`, corresponding source and SHA-256 checksums. The workflow installs the package on its runner and checks that its browser helper opens a local test page.

The source repository queues builds through a dedicated deploy key for this packaging repo. The corresponding private key is stored as Avernella’s `PACKAGE_QUEUE_KEY` Actions secret. To retry a build, run `gh workflow run packages.yml -R novesce/avernella-packaging`.
