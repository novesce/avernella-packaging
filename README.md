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

## Fedora (COPR)

Install from the [novesce/avernella COPR](https://copr.fedorainfracloud.org/coprs/novesce/avernella/) on Fedora 43, 44 and 45 (`x86_64`):

```sh
sudo dnf copr enable novesce/avernella
sudo dnf install avernella
```

To update later, run `sudo dnf upgrade avernella`.

The RPM repackages the same verified Ubuntu `.deb` as the default release and the AUR, so every format ships one build. Fedora 43 and 44 have libvpx 1.15 (`libvpx.so.9`) while the release links libvpx 1.16, so the RPM also carries Ubuntu 26.04's `libvpx.so.12`, pinned by SHA-256, privately in `/usr/lib/avernella`. It neither requires nor provides a system libvpx. All other libraries come from Fedora. Rawhide (the coming Fedora 46) has moved to OpenSSL 4 while the release links OpenSSL 3, so COPR does not build for it yet.

If you used the earlier self-hosted DNF repository, remove it and switch to COPR. The package name and version numbering are unchanged, so `dnf` upgrades in place:

```sh
sudo rm -f /etc/yum.repos.d/avernella.repo
sudo dnf copr enable novesce/avernella
sudo dnf upgrade avernella
```

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

The Flatpak repackages the same verified Ubuntu `.deb` as the default release, the AUR and COPR, so every format ships one build. The GNOME 49 runtime provides its libraries except three: the manifest builds `libqrencode`, `libsrtp` (with OpenSSL) and `zbar`, and installs Ubuntu 26.04's `libvpx.so.12`, pinned by SHA-256, in `/app/lib` because the runtime only has `libvpx.so.11`. The [Flatpak workflow](.github/workflows/flatpak.yml) builds each queued commit once its Debian release exists, pins that `.deb`'s SHA-256 in `flatpak/io.github.novesce.Avernella.yml` and the metainfo via `scripts/flatpak-recipe`, smoke-tests the installed app (no unresolved libraries or symbols, the bundled libvpx in use, `avernella --help`), publishes a fresh `.flatpak` bundle to Releases, and updates the Flatpak OSTree repository on GitHub Pages.

## Publishing

The [GitHub Actions workflow](.github/workflows/packages.yml) runs on `ubuntu-latest`. A scheduled check on packaging’s `main` branch picks up any Avernella commits that still lack a release, including commits pushed together. Each published release includes the tested `.deb`, corresponding source and SHA-256 checksums. The workflow installs the package on its runner and checks that its browser helper opens a local test page.

For immediate builds, configure `PACKAGE_DISPATCH_TOKEN` in the source repository with a fine-grained token scoped to this repository and **Actions: write**. The source workflow dispatches the packaging workflows on `main`. The workflows also run on their regular schedules.

The [desktop format queue](.github/workflows/source-formats.yml) walks upstream history after `d4aaebc` and checks which versioned releases still need a Flatpak. A multi-commit push schedules each missing source SHA. Each job checks out that SHA and attaches its verified package to the corresponding release. The Debian queue runs independently and checks for the Debian asset, source archive and checksum. Only the current upstream revision updates the rolling Flatpak channel. The default release, the AUR and COPR use the verified Debian package.

Scheduled checks reconcile unfinished commits every 20 minutes. To run a check immediately, use `gh workflow run packages.yml -R novesce/avernella-packaging` for Debian and `gh workflow run source-formats.yml -R novesce/avernella-packaging` for Flatpak.

When a newer release is available, the workflow builds the recipe in a clean Arch container, installs it, checks the executable and browser helpers for unresolved libraries and symbols, and runs `avernella --help`. It pushes the verified `PKGBUILD` and `.SRCINFO` to the AUR using the registered maintainer key in the `AUR_SSH_PRIVATE_KEY` packaging repository secret. To regenerate the recipe locally on Arch, run `scripts/aur-recipe path/to/release.deb FULL_APP_COMMIT output-directory`.

For Fedora, the same workflow asks COPR which version it last built. When the release is newer, it renders [`rpm/avernella.spec.in`](rpm/avernella.spec.in) with `scripts/copr-recipe`, then builds, installs and checks the RPM with `scripts/fedora-check` in Fedora 43, 44 and 45 containers: no unresolved libraries or symbols, the bundled libvpx in use, and `avernella --help`. Only then does it submit the source RPM with `copr-cli build novesce/avernella`, using the COPR API configuration in the `COPR_CONFIG` packaging repository secret (the contents of `~/.config/copr` from https://copr.fedorainfracloud.org/api/). COPR API tokens expire after 180 days.

The Ubuntu package for source revision `8c8d0f5` backports grayscale text antialiasing on scrollable GPU textures. Its source archive contains the exact patched files, and the installed package includes the diff at `/usr/share/doc/avernella/packaging.patch`.

## Liney on Arch Linux and CachyOS

Install the separate [Liney package](https://aur.archlinux.org/packages/liney-bin) with an AUR helper.

```sh
paru -S liney-bin
```

The [Liney workflow](.github/workflows/liney-aur.yml) checks [Cytech Team’s stable releases](https://github.com/Cytech-Team/Liney/releases) every ten minutes, starting with version 0.1.36. Each AUR recipe downloads the upstream x86-64 Debian package and checks its SHA-256 digest. CI builds and checks the Arch package before pushing the recipe to the AUR. When several releases arrive between checks, CI publishes them in version order. GitHub may delay scheduled runs.

To check for releases immediately, run `gh workflow run liney-aur.yml -R novesce/avernella-packaging`.

The workflow checks that the AUR package belongs to `novesce`. After an AUR account rename, set the packaging repository’s Actions variable `AUR_MAINTAINER` to the new username.
