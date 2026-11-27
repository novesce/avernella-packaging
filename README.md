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

## Flatpak (GNOME 49 runtime, with LIFF browser)

Install from the auto-updating Flatpak repository (updates on every Avernella commit):

```sh
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak remote-add --user --no-gpg-verify --if-not-exists avernella https://novesce.github.io/avernella-packaging/repo
flatpak install --user avernella io.github.novesce.Avernella
flatpak run io.github.novesce.Avernella
```

To update later, run `flatpak update --user`. Or download the standalone `.flatpak` file directly from the [`flatpak-latest` release](https://github.com/novesce/avernella-packaging/releases/tag/flatpak-latest) and install it with:

```sh
flatpak install --user ./avernella_*_x86_64.flatpak
```

To build locally from the manifest in [`flatpak/io.github.novesce.Avernella.yml`](flatpak/io.github.novesce.Avernella.yml):

```sh
flatpak install --user flathub org.gnome.Platform//49 org.gnome.Sdk//49
flatpak-builder --force-clean --user --install \
  out/flatpak-build flatpak/io.github.novesce.Avernella.yml
```

The [Flatpak workflow](.github/workflows/flatpak.yml) runs on every Avernella commit (via `avernella-source-*` tags and a scheduled check), updates `flatpak/io.github.novesce.Avernella.yml` and `flatpak/io.github.novesce.Avernella.metainfo.xml` via `scripts/flatpak-recipe`, builds Avernella with the WebKitGTK 6.0 LIFF browser and native Vulkan renderer, smoke-tests the installed app, publishes a fresh `.flatpak` bundle to Releases, and updates the Flatpak OSTree repository on GitHub Pages.

## Publishing

The [GitHub Actions workflow](.github/workflows/packages.yml) runs on `ubuntu-latest`. A push to Avernella’s `main` branch queues packaging. A scheduled check picks up any commits that still lack a release, including commits pushed together. Each published release includes the tested `.deb`, corresponding source and SHA-256 checksums. The workflow installs the package on its runner and checks that its browser helper opens a local test page.

The source repository queues builds through a dedicated deploy key for this packaging repo. The corresponding private key is stored as Avernella’s `PACKAGE_QUEUE_KEY` Actions secret. To retry a build, run `gh workflow run packages.yml -R novesce/avernella-packaging`.

When a newer release is available, the workflow builds the recipe in a clean Arch container, installs it, checks the executable and browser helpers for unresolved libraries and symbols, and runs `avernella --help`. It pushes the verified `PKGBUILD` and `.SRCINFO` to the AUR using the registered maintainer key in the `AUR_SSH_PRIVATE_KEY` packaging repository secret. To regenerate the recipe locally on Arch, run `scripts/aur-recipe path/to/release.deb FULL_APP_COMMIT output-directory`.

The Ubuntu package for source revision `8c8d0f5` backports grayscale text antialiasing on scrollable GPU textures. Its source archive contains the exact patched files, and the installed package includes the diff at `/usr/share/doc/avernella/packaging.patch`.

## Liney on Arch Linux and CachyOS

Install the separate [Liney package](https://aur.archlinux.org/packages/liney-bin) with an AUR helper.

```sh
paru -S liney-bin
```

The [Liney workflow](.github/workflows/liney-aur.yml) checks [Cytech Team’s stable releases](https://github.com/Cytech-Team/Liney/releases) every ten minutes, starting with version 0.1.36. Each AUR recipe downloads the upstream x86-64 Debian package and checks its SHA-256 digest. CI builds and checks the Arch package before pushing the recipe to the AUR. When several releases arrive between checks, CI publishes them in version order. GitHub may delay scheduled runs.

To check for releases immediately, run `gh workflow run liney-aur.yml -R novesce/avernella-packaging`.

The workflow checks that the AUR package belongs to `novesce`. After an AUR account rename, set the packaging repository’s Actions variable `AUR_MAINTAINER` to the new username.
