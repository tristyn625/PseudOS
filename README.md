# PseudOS

**PseudOS 0.1.0** is a portable, Ubuntu-based desktop operating system built around **XFCE 4.20**. It is designed to start from a USB drive, provide a familiar graphical desktop, and optionally keep changes between boots.

This repository contains the PseudOS specification, original artwork, XFCE integration patch, and GitHub Actions workflow. The workflow compiles the ISO using a pinned revision of the open-source [`linuxlive`](https://github.com/Eric-Ness/linuxlive) live-ISO builder.

## What is in the first build

- Ubuntu 26.04 LTS base and the Ubuntu generic kernel.
- XFCE 4.20 desktop, LightDM login manager, and GTK greeter.
- Original PseudOS wallpaper, logo, and boot branding.
- Firefox, VLC, LibreOffice, and Thunderbird, installed from Flathub.
- Thunar file manager, Mousepad text editor, Geany IDE, Ristretto image viewer, Parole media player, Atril PDF viewer, Simple Scan, Catfish search, Xarchiver, and common XFCE utilities.
- Broad Linux device firmware, Wi-Fi and wired networking through NetworkManager, Bluetooth and Bluetooth-audio support, PipeWire audio, exFAT/NTFS removable-drive support, printer support, and network-scanner support.
- GNOME Software with Flatpak support, plus Synaptic for traditional Ubuntu packages.
- A live boot menu, optional USB persistence, and the upstream install-to-disk utility.
- A reproducible GitHub Actions build with QEMU tests for UEFI, Secure Boot, BIOS, USB persistence across reboots, and a disposable virtual-disk installation.

The initial image includes a lightweight development starter set (Geany, Git, Python virtual environments, and common command-line tools). Larger creative applications such as GIMP remain available through the software manager rather than being forced into the base image.

## Build the ISO

1. Push this repository to GitHub (or commit the files to its `main` branch).
2. Open the repository's **Actions** tab.
3. Select **Build PseudOS** and choose **Run workflow**, or simply push a commit to `main`.
4. Open the completed workflow run and download the `PseudOS-0.1.0-amd64` artifact.
5. The artifact contains the ISO, its SHA-256 checksum, and the installed-package manifest. Build logs, boot reports, and inspection data are in the separate `PseudOS-build-diagnostics` artifact.

The workflow fetches the live-ISO builder at this exact commit so that builds do not silently change when upstream moves:

`fda95dd28424064f70347481fa6ee5b3b989dcd1`

It then applies `scripts/patch-linuxlive.py` to add XFCE support, generates the artwork, compiles `linuxlive.yaml`, builds the Ubuntu image with Podman, assembles the hybrid ISO, and boots it in QEMU. The build is not considered verified unless the desktop and USB persistence checks pass.

## Boot and persistence

Test the ISO in a virtual machine before writing it to a physical USB drive. The intended first milestone is a live XFCE desktop that works without installing anything to the computer's internal drive.

The first live boot-menu entry enables persistence. Ubuntu's casper live system creates a `writable` partition in free space after the ISO on a suitable USB drive. The alternate clean-session entry starts without using the saved changes. Persistence needs room beyond the ISO itself, so use a USB drive larger than the image; **8 GB or more is a practical target**. The actual ISO size will be shown in the workflow summary after the first successful build.

## Installing to a computer

The upstream builder supplies an **Install PseudOS** launcher and boot-menu entry. Its current installer is intentionally simple: it repartitions and formats the selected whole disk. It does not provide dual-boot setup or disk encryption. It requires an explicit confirmation matching the selected disk, but that is not a substitute for care.

**Do not run the installer on a computer or drive containing files you need.** The first release should be tested in a virtual machine. Real-hardware installation, Wi-Fi, Bluetooth, audio, sleep, and graphics compatibility still need testing on different computers.

## Repository layout

```text
.github/workflows/build.yml   GitHub Actions build and QEMU tests
assets/                       Generated logo and wallpaper
linuxlive.yaml                PseudOS operating-system specification
scripts/make_art.py           Generates the original artwork
scripts/patch-linuxlive.py    Adds XFCE support to the pinned builder
scripts/first-login.sh        Applies XFCE appearance defaults
```

## Changing the system

- Add or remove native Ubuntu packages in the XFCE package list inside `scripts/patch-linuxlive.py`, or in the `packages` section of `linuxlive.yaml` for PseudOS-specific extras.
- Add or remove Flathub app IDs under `apps` in `linuxlive.yaml` (the builder catalog includes Firefox, VLC, LibreOffice, Thunderbird, GIMP, and other common applications).
- Adjust the logo and wallpaper by editing `scripts/make_art.py` and rebuilding.
- Add hardware firmware or developer utilities in the `packages` section of `linuxlive.yaml`.
- Change the USB persistence setting with `persistence: true` in `linuxlive.yaml`.
- Change the default XFCE theme, icons, wallpaper, and user defaults in `scripts/first-login.sh`.

The XFCE patch is strict by design. If the pinned upstream source changes one of the locations that the patch expects, the build stops with a useful error rather than pretending it produced a working XFCE image.

## Licenses and attribution

PseudOS's build integration is intended to be distributed under **GPL-3.0-or-later**. The ISO build uses [Eric-Ness/linuxlive](https://github.com/Eric-Ness/linuxlive), also GPL-3.0-or-later, at the pinned revision above. PseudOS's logo, wallpaper, and project-specific scripts are original project assets. Ubuntu, XFCE, Firefox, VLC, and other included software remain under their respective upstream licenses and trademarks.

## Current status

This is the first full PseudOS build configuration, not a claim that the ISO has already succeeded or that every computer is supported. The GitHub Actions run is the next proof point. If it fails, the `PseudOS-build-diagnostics` artifact and failed workflow step will identify the part that needs fixing.
