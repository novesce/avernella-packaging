# Avernella packages

[Download the latest amd64 package](https://github.com/novesce/avernella-packaging/releases/latest) for [Avernella](https://github.com/novesce/avernella). Use the Ubuntu release identified in the release notes.

```sh
sudo apt install ./avernella_*_amd64.deb
```

The package includes the executable, desktop launcher, icon, and WebKitGTK helper. The build also includes the WPE WebKit helper when Ubuntu provides the WPE Wayland SDK. Avernella prefers WPE on Wayland when available.

## Arch Linux and CachyOS

Install [avernella-bin from the AUR](https://aur.archlinux.org/packages/avernella-bin) with an AUR helper.

```sh
paru -S avernella-bin
```

To build with the standard Arch tools, run the following as your regular user.

```sh
sudo pacman -S --needed base-devel git
git clone https://aur.archlinux.org/avernella-bin.git
cd avernella-bin
makepkg -si
```

The recipe fetches the x86-64 Ubuntu release from GitHub, verifies its SHA-256 checksum and installs its payload as an Arch package. The dependencies include the precise libvpx and OpenSSL library versions used by that release.

## Publishing

The [GitHub Actions workflow](.github/workflows/packages.yml) runs on `ubuntu-latest`. A push to Avernella’s `main` branch queues packaging. A scheduled check picks up any commits that still lack a release, including commits pushed together. Each published release includes the tested `.deb`, corresponding source and SHA-256 checksums. The workflow installs the package on its runner and checks that its browser helper opens a local test page.

The source repository queues builds through a dedicated deploy key for this packaging repo. The corresponding private key is stored as Avernella’s `PACKAGE_QUEUE_KEY` Actions secret. To retry a build, run `gh workflow run packages.yml -R novesce/avernella-packaging`.

When a newer release is available, the workflow builds the recipe in a clean Arch container, installs it, checks the executable and browser helpers for unresolved libraries and symbols, and runs `avernella --help`. It pushes the verified `PKGBUILD` and `.SRCINFO` to the AUR using the registered maintainer key in the `AUR_SSH_PRIVATE_KEY` packaging repository secret. To regenerate the recipe locally on Arch, run `scripts/aur-recipe path/to/release.deb FULL_APP_COMMIT output-directory`.
