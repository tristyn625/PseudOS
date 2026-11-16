# Build information

- Distribution: Ubuntu 26.04 LTS (Resolute Raccoon)
- Architecture: amd64
- Desktop: XFCE 4.20
- Display manager: LightDM with the GTK greeter
- Desktop applications: Firefox, VLC, LibreOffice, Thunderbird, Synaptic, Geany, Mousepad, and XFCE utilities
- Hardware and peripherals: broad firmware, NetworkManager, Bluetooth/PipeWire audio, removable storage, printing, and scanning
- Live-ISO engine: `Eric-Ness/linuxlive`
- Live-ISO engine revision: `fda95dd28424064f70347481fa6ee5b3b989dcd1`
- Build workflow: `.github/workflows/build.yml`

The build is reproducible at the project-configuration level: the external build engine is pinned to an exact Git commit, while Ubuntu packages and Flathub applications are resolved from their repositories when the workflow runs.

The ISO has **not** yet been built or boot-tested. A successful GitHub Actions run is required before calling this release verified. Real hardware compatibility also remains to be tested.
