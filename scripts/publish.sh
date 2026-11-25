#!/usr/bin/env bash
#
# Download APKs, generate icons, build and stage the F-Droid repository.
#
# CI runs exactly this file inside `nix develop` (see flake.nix), so the same
# command works locally:
#
#   nix develop -c bash -c \
#     'KEYSTOREPASS=... SERVERWEBROOT=$PWD/../wroot/fdroid ./scripts/publish.sh'
#
# The dev shell provides: fdroid, apksigner, rsync, java, apktool, magick,
# 7z, wget, bwrap and python3 with httpx + telethon.
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")/.."

REPO_DIR=fdroid
OUT_DIR=public
# `fdroid deploy` insists that the webroot ends in /fdroid
SERVERWEBROOT="${SERVERWEBROOT:-/fdroid}"

if [[ -z "${KEYSTOREPASS:-}" ]]; then
  echo "::error::KEYSTOREPASS is not set"
  exit 1
fi
# bwrap lets fdroid see a generated config.yml without touching the checkout.
# If user namespaces are unavailable, fall back to swapping the file in and out.
if [[ "${PUBLISH_NO_BWRAP:-0}" != "1" ]] &&
  command -v bwrap >/dev/null 2>&1 &&
  bwrap --bind / / --dev-bind /dev /dev --proc /proc -- true 2>/dev/null; then
  BWRAP=1
else
  BWRAP=0
  echo "bwrap unavailable, temporarily rewriting $REPO_DIR/config.yml instead"
fi

TMPDIR_WORK="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_WORK"' EXIT

# fdroidserver only ever reads ./config.yml from the current directory, so the
# effective config is generated here and bind-mounted over the tracked file.
# It holds no secrets: fdroidserver 2.3+ resolves `{env: VAR}` values itself.
CONFIG="$TMPDIR_WORK/config.yml"
{
  sed -E "s|^serverwebroot:.*|serverwebroot: ${SERVERWEBROOT}|" "$REPO_DIR/config.yml"
  printf 'keystorepass:\n  env: KEYSTOREPASS\nkeypass:\n  env: KEYSTOREPASS\n'
} >"$CONFIG"
chmod 600 "$CONFIG"

if ((BWRAP == 0)); then
  cp -p "$REPO_DIR/config.yml" "$TMPDIR_WORK/config.yml.orig"
  trap 'cp -p "$TMPDIR_WORK/config.yml.orig" "$REPO_DIR/config.yml"; rm -rf "$TMPDIR_WORK"' EXIT
  install -m 600 "$CONFIG" "$REPO_DIR/config.yml"
fi

# Run an fdroid command as if the repo dir contained the generated config.
fdroid_run() {
  if ((BWRAP == 1)); then
    bwrap \
      --bind / / \
      --dev-bind /dev /dev \
      --proc /proc \
      --ro-bind "$CONFIG" "$PWD/$REPO_DIR/config.yml" \
      --chdir "$PWD/$REPO_DIR" \
      --setenv KEYSTOREPASS "$KEYSTOREPASS" \
      -- "$@"
  else
    (cd "$REPO_DIR" && "$@")
  fi
}

mkdir -p "$REPO_DIR/repo"

echo "::group::Fetch APKs"
python3 downloader/main.py
echo "::endgroup::"

shopt -s nullglob
apks=("$REPO_DIR"/repo/*.apk)
echo "found ${#apks[@]} apk(s)"
if ((${#apks[@]} == 0)); then
  echo "::error::no APKs were downloaded, refusing to publish an empty repo"
  exit 1
fi

echo "::group::Generate icons"
for apk in "${apks[@]}"; do
  python3 icon.py "$apk" "$REPO_DIR/repo" || echo "::warning::icon.py failed for $apk"
done
echo "::endgroup::"

echo "::group::fdroid update"
fdroid_run fdroid update \
  --create-metadata \
  --use-date-from-apk \
  --rename-apks \
  --verbose
echo "::endgroup::"

echo "::group::fdroid deploy"
mkdir -p "$SERVERWEBROOT"
fdroid_run fdroid deploy --verbose
# only the current APKs get published, the archive is dropped
rm -rf "$SERVERWEBROOT/archive"
echo "::endgroup::"

if [[ ! -s "$SERVERWEBROOT/repo/index.xml" ]]; then
  echo "::error::$SERVERWEBROOT/repo/index.xml is missing - 'fdroid deploy' did not stage anything"
  exit 1
fi

echo "::group::Assemble $OUT_DIR"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"
shopt -s dotglob
mv "$SERVERWEBROOT"/* "$OUT_DIR"/
cp index.html "$OUT_DIR"/
[[ -d "$OUT_DIR/repo" ]] && cp index.html "$OUT_DIR/repo"/
cp index.html "$OUT_DIR/404.html"
printf 'published %s apk(s), %s total\n' \
  "$(find "$OUT_DIR/repo" -maxdepth 1 -name '*.apk' | wc -l)" "$(du -sh "$OUT_DIR" | cut -f1)"
echo "::endgroup::"
