{
  description = "Toolchain for fetching APKs and publishing the F-Droid repository";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      # Upstream only skips APKs that raise BuildException, so one broken or
      # exotic APK (modded/re-signed builds do this) aborts the entire
      # `fdroid update`.  Broaden that catch so a bad APK is skipped instead.
      # Token-level replacement rather than a .patch file, so this survives
      # upstream reformatting; substituteInPlace fails loudly if it vanishes.
      # (the upstream warning text still says "invalid signature")
      fdroidserver =
        pkgs:
        pkgs.fdroidserver.overridePythonAttrs (old: {
          postPatch = ''${(old.postPatch or "")}
            substituteInPlace fdroidserver/update.py \
              --replace-fail 'except BuildException:' 'except Exception:'
          '';
        });

      # per-system toolchain shell
      shell =
        pkgs:
        pkgs.mkShellNoCC {
          name = "fdroid-repo";

          packages = [
            # fdroidserver ships its own Python env (androguard included) and
            # puts apksigner/gradlew-fdroid on PATH.
            (fdroidserver pkgs)
            pkgs.apksigner
            # `fdroid deploy` rsyncs the repo into serverwebroot
            pkgs.rsync
            # `fdroid update` insists on a Java JDK being present
            pkgs.jdk

            # icon.py
            pkgs.apktool
            pkgs.imagemagick

            # downloader/modules/classes.py merges split APKs with it
            pkgs.apkeditor

            # downloader modules unpack Actions/nightly.link artifacts
            pkgs.p7zip
            pkgs.wget

            # publish.sh bind-mounts its generated config.yml with it
            pkgs.bubblewrap

            # downloader/requirements.txt: httpx, telethon
            (pkgs.python3.withPackages (
              ps: [
                ps.httpx
                ps.telethon
              ]
            ))
          ];

          # Use the packaged tools instead of vendored jars.
          APKTOOL_PATH = "apktool";
          APKEDITOR_PATH = "APKEditor";

          shellHook = ''
            echo "fdroidserver $(fdroid --version 2>/dev/null)"
          '';
        };

      forAllSystems =
        f:
        nixpkgs.lib.genAttrs systems (
          system:
          f (import nixpkgs {
            inherit system;
            # aapt (Android SDK build-tools) ships under a non-free license
            config = {
              allowUnfree = true;
            };
          })
        );
    in
    {
      devShells = forAllSystems (pkgs: {
        default = shell pkgs;
      });

      # `nix build .#` builds the patched fdroidserver, handy for local checks
      packages = forAllSystems (pkgs: {
        default = fdroidserver pkgs;
      });
    };
}
