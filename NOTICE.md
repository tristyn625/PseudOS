# Third-party build component

PseudOS uses the `linuxlive` live-ISO build system by Eric Ness:

- Repository: https://github.com/Eric-Ness/linuxlive
- Pinned source commit: `fda95dd28424064f70347481fa6ee5b3b989dcd1`
- License: GNU General Public License, version 3 or later (GPL-3.0-or-later)

The PseudOS workflow fetches that source at the pinned commit and applies the local XFCE integration patch in `scripts/patch-linuxlive.py`. The upstream source is not vendored into this repository.
