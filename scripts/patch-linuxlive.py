#!/usr/bin/env python3
"""Add first-class XFCE support to the pinned linuxlive build engine.

The patch is deliberately strict: if upstream changes any of the extension
points, the build stops instead of silently producing a broken desktop.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    data = path.read_text(encoding="utf-8")
    count = data.count(old)
    if count != 1:
        raise SystemExit(
            f"Patch mismatch in {path}: expected one occurrence, found {count}: {old!r}"
        )
    path.write_text(data.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: patch-linuxlive.py PATH-TO-LINUXLIVE-CHECKOUT", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    required = [
        root / "linuxlive/data/catalog.yaml",
        root / "linuxlive/data/spec.schema.json",
        root / "linuxlive/compiler/plan.py",
        root / "linuxlive/compiler/options.py",
        root / "linuxlive/data/rootfs/common/usr/libexec/linuxlive/bootcheck",
        root / "linuxlive/data/rootfs/common/usr/libexec/linuxlive/finalize",
        root / "linuxlive/data/rootfs/ubuntu/usr/libexec/linuxlive/install-to-disk",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("Not a complete linuxlive checkout; missing:\n" + "\n".join(missing))

    # Add the Ubuntu XFCE desktop variant without rewriting catalog.yaml (and
    # destroying its carefully maintained upstream comments).
    catalog = root / "linuxlive/data/catalog.yaml"
    catalog_text = catalog.read_text(encoding="utf-8")
    if "\n  xfce:\n" not in catalog_text:
        marker = "\napps:\n"
        if catalog_text.count(marker) != 1:
            raise SystemExit("Could not find the unique 'apps:' catalog insertion point")
        xfce = """
  xfce:
    label: Xfce
    shell_process: xfce4-session
    ubuntu:
      # XFCE 4.20 desktop, LightDM login, hardware controls and common utilities.
      packages: [xfce4, xfce4-goodies, lightdm, lightdm-gtk-greeter, xserver-xorg, network-manager-applet, wpasupplicant, wireless-regdb, bluez, blueman, pipewire-audio, pipewire-pulse, libspa-0.2-bluetooth, wireplumber, pavucontrol, alsa-utils, xfce4-pulseaudio-plugin, gvfs, gvfs-backends, udisks2, thunar-volman, thunar-archive-plugin, xarchiver, exfatprogs, ntfs-3g, xfce-polkit, greybird-gtk-theme, elementary-xfce-icon-theme, fonts-noto-core, fonts-noto-color-emoji, fonts-dejavu-core, xfce4-whiskermenu-plugin, mousepad, ristretto, parole, catfish, atril, simple-scan, xfce4-screensaver, xfce4-power-manager, xfce4-screenshooter, xdg-user-dirs, cups, cups-bsd, ipp-usb, sane-airscan, system-config-printer, gnome-software, gnome-software-plugin-flatpak]
"""
        catalog.write_text(catalog_text.replace(marker, "\n" + xfce + marker, 1), encoding="utf-8")

    # Keep the catalog's own explanation of GTK language packs accurate.
    replace_once(
        catalog,
        "-gnome- for GNOME and GTK programs (GNOME and Cinnamon)",
        "-gnome- for GNOME and GTK programs (GNOME, Cinnamon, and XFCE)",
    )

    # Keep the JSON schema's desktop enum in lockstep with the catalog.
    schema_path = root / "linuxlive/data/spec.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    desktop_enum = schema["properties"]["desktop"]["enum"]
    if "xfce" not in desktop_enum:
        desktop_enum.append("xfce")
        schema_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # XFCE's file manager is Thunar. This only matters when a spec pins apps.
    replace_once(
        root / "linuxlive/compiler/plan.py",
        'FILE_MANAGERS = {"gnome": "org.gnome.Nautilus.desktop", "kde": "org.kde.dolphin.desktop", "cinnamon": "nemo.desktop"}',
        'FILE_MANAGERS = {"gnome": "org.gnome.Nautilus.desktop", "kde": "org.kde.dolphin.desktop", "cinnamon": "nemo.desktop", "xfce": "thunar.desktop"}',
    )

    # XFCE is GTK-based, so include the matching translation pack for a
    # non-English spec just as GNOME and Cinnamon do.
    replace_once(
        root / "linuxlive/compiler/options.py",
        'if plan.desktop.id in ("gnome", "cinnamon"):',
        'if plan.desktop.id in ("gnome", "cinnamon", "xfce"):',
    )

    # Let the existing live-session verifier detect that XFCE's session ran.
    replace_once(
        root / "linuxlive/data/rootfs/common/usr/libexec/linuxlive/bootcheck",
        "for proc in gnome-shell plasmashell cinnamon cage; do",
        "for proc in gnome-shell plasmashell cinnamon xfce4-session cage; do",
    )

    # XFCE uses LightDM. Enable its graphical target and validate the display
    # manager just as the upstream Cinnamon integration does.
    finalizer = root / "linuxlive/data/rootfs/common/usr/libexec/linuxlive/finalize"
    replace_once(
        finalizer,
        "enable_services() {",
        '''brand_xfce() {
\tgreeter=/etc/lightdm/lightdm-gtk-greeter.conf
\t[ -f "$greeter" ] || die "LightDM GTK greeter configuration is missing"
\tunit=/etc/systemd/system/display-manager.service
\tprintf '/usr/sbin/lightdm\\n' >/etc/X11/default-display-manager
\t[ -e "$unit" ] || ln -s /usr/lib/systemd/system/lightdm.service "$unit"
\tsystemctl set-default graphical.target
\tcase "$(readlink -f "$unit")" in
\t*/lightdm.service) ;;
\t*) die "display-manager.service is $(readlink -f "$unit"), not lightdm" ;;
\tesac
\tlog "XFCE 4.20 session and LightDM configured"
}

enable_services() {''',
    )
    replace_once(
        finalizer,
        "cinnamon) brand_cinnamon ;;\n*) die \"unknown desktop $LL_DESKTOP\" ;;",
        "cinnamon) brand_cinnamon ;;\nxfce) brand_xfce ;;\n*) die \"unknown desktop $LL_DESKTOP\" ;;",
    )

    # Give installed systems a PseudOS firmware entry instead of an Ubuntu-named one.
    installer = root / "linuxlive/data/rootfs/ubuntu/usr/libexec/linuxlive/install-to-disk"
    replace_once(
        installer,
        'in_target grub-install --target="$efi_target" --efi-directory=/boot/efi --bootloader-id=ubuntu --uefi-secure-boot "$@"',
        'in_target grub-install --target="$efi_target" --efi-directory=/boot/efi --bootloader-id=PseudOS --uefi-secure-boot "$@"',
    )

    # The installer writes the installed user's LightDM autologin preference.
    replace_once(
        installer,
        'cinnamon) mkdir -p "$target/etc/lightdm/lightdm.conf.d" && printf \'[Seat:*]\\nautologin-user=%s\\n\' "$user" >"$target/etc/lightdm/lightdm.conf.d/91-linuxlive-autologin.conf" ;;',
        'cinnamon | xfce) mkdir -p "$target/etc/lightdm/lightdm.conf.d" && printf \'[Seat:*]\\nautologin-user=%s\\n\' "$user" >"$target/etc/lightdm/lightdm.conf.d/91-linuxlive-autologin.conf" ;;',
    )

    # Static LightDM configuration is copied into the built root filesystem by
    # linuxlive's normal desktop-tree mechanism.
    desktop_root = root / "linuxlive/data/rootfs/xfce"
    lightdm_dir = desktop_root / "etc/lightdm/lightdm.conf.d"
    lightdm_dir.mkdir(parents=True, exist_ok=True)
    (lightdm_dir / "90-linuxlive.conf").write_text(
        "# PseudOS: use the XFCE session and the GTK greeter.\n"
        "[Seat:*]\n"
        "greeter-session=lightdm-gtk-greeter\n"
        "user-session=xfce\n"
        "autologin-session=xfce\n",
        encoding="utf-8",
    )
    (desktop_root / "etc/lightdm/lightdm-gtk-greeter.conf").parent.mkdir(parents=True, exist_ok=True)
    (desktop_root / "etc/lightdm/lightdm-gtk-greeter.conf").write_text(
        "[greeter]\n"
        "background=/usr/share/backgrounds/linuxlive/pseudos-wallpaper.png\n"
        "theme-name=Greybird\n"
        "icon-theme-name=elementary-xfce\n"
        "font-name=Noto Sans 10\n"
        "logo=/usr/share/pixmaps/linuxlive-logo.png\n"
        "indicators=~host;~spacer;~clock;~spacer;~session;~power\n",
        encoding="utf-8",
    )

    print("XFCE support added to the pinned linuxlive source tree.")
    print("Desktop: XFCE 4.20 | Display manager: LightDM | Session check: xfce4-session")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
