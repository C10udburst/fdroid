# Cloudburst's fdroid repository

This repository contains the metadata for the Cloudburst F-Droid repository.

To add this repository to your F-Droid client, scan the QR code below or add it manually from https://c10udburst.github.io/fdroid/repo/

![qr](https://c10udburst.github.io/fdroid/repo/index.png)

## Avaliable apps

To see what apps are avaliable in this repository, click [here](https://c10udburst.github.io/fdroid/repo/)

## Building locally

The toolchain is pinned in `flake.lock` (fdroidserver, apksigner, apktool,
apkeditor, ImageMagick, 7z, rsync, python with httpx/telethon), so CI and local
runs use the exact same tools:

```bash
# put fdroid/keystore.jks in place first, then:
nix develop -c bash -c 'KEYSTOREPASS=... ./scripts/publish.sh'          # stages into /fdroid
nix develop -c bash -c 'KEYSTOREPASS=... SERVERWEBROOT=$PWD/../wroot/fdroid ./scripts/publish.sh'
```

`scripts/publish.sh` downloads the APKs (`downloader/`), generates icons
(`icon.py`), runs `fdroid update` + `fdroid deploy` and assembles `public/` for
`actions/upload-pages-artifact`.