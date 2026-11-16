#!/bin/sh
# Apply PseudOS's default XFCE appearance in both the live and installed user.
set -eu

WALLPAPER=/usr/share/backgrounds/linuxlive/pseudos-wallpaper.png

command -v xfconf-query >/dev/null 2>&1 || exit 0
[ -r "$WALLPAPER" ] || exit 0

# Wait briefly for the XFCE settings daemon and desktop channel to come online.
tries=0
while ! xfconf-query -c xfce4-desktop -l >/dev/null 2>&1; do
    tries=$((tries + 1))
    [ "$tries" -lt 15 ] || exit 0
    sleep 1
done

# Set every wallpaper target XFCE has created for this display session.
xfconf-query -c xfce4-desktop -l 2>/dev/null |
    while IFS= read -r property; do
        case "$property" in
            */last-image)
                xfconf-query -c xfce4-desktop -p "$property" --set "$WALLPAPER" 2>/dev/null || true
                style_property=${property%last-image}image-style
                xfconf-query -c xfce4-desktop -p "$style_property" --create --type int --set 5 2>/dev/null || true
                ;;
        esac
    done

# Ensure a sensible default target exists for a newly created XFCE profile.
xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/last-image \
    --create --type string --set "$WALLPAPER" 2>/dev/null || true
xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/image-style \
    --create --type int --set 5 2>/dev/null || true

# Greybird + elementary-XFCE keep the desktop lightweight and coherent.
xfconf-query -c xsettings -p /Net/ThemeName \
    --create --type string --set Greybird 2>/dev/null || true
xfconf-query -c xsettings -p /Net/IconThemeName \
    --create --type string --set elementary-xfce 2>/dev/null || true
xfconf-query -c xsettings -p /Gtk/FontName \
    --create --type string --set "Noto Sans 10" 2>/dev/null || true
xfconf-query -c xfwm4 -p /general/theme \
    --create --type string --set Greybird 2>/dev/null || true

# Give Thunar useful default folders in the user's home directory.
if command -v xdg-user-dirs-update >/dev/null 2>&1; then
    xdg-user-dirs-update >/dev/null 2>&1 || true
fi

exit 0
