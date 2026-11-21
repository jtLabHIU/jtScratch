# jtScratch
etrobo environment addon for jtScratch and jtS3H.

## Install repositories

Run `jtScratch install [<absolute path to jtScratchRepos>]`. If the path is
omitted, repositories are stored in `$ETROBO_USERPROFILE/jtScratchRepos`. The
addon exposes that directory at `repos` through a symbolic link, so the
filesystem containing the addon must support symbolic links (for example,
NTFS).

The installer clones `scratch-editor`, `scratch-desktop`, and then `s3h` when
their directories do not already exist. Existing Git repositories are reused
without cloning, and `npm install` is run in each case. The installer reads
the Node.js version from `scratch-editor/.nvmrc`, installs and activates it
with nvm, and installs nvm itself if needed. It uses `sudo apt` to install
Git, curl, and the build tools required by native npm dependencies
(`build-essential` and `python3`). For scratch-desktop Windows Electron builds,
the installer enables the i386 architecture and installs `wine64`, `wine32:i386`,
`mono-devel`, and `libnss3`. The Wine runtimes are needed to run Windows
installer tooling during cross-builds. In WSL, it also installs nvm-windows
through winget and activates the Node.js version from `.nvmrc` for Windows-side
debugging. Logs are written separately to `logs/install_scratch-editor.log`,
`logs/install_scratch-desktop.log`, `logs/install_s3h.log`, and `logs/windows-node.log`.

Opening `jtScratch.code-workspace` starts an integrated terminal and runs
`jtScratch activate`. This activates the Node.js version specified by
`scratch-editor/.nvmrc` with nvm on WSL and nvm-windows. If the Windows
version is not installed, it runs `jtScratch install` to prepare it. It then
leaves an interactive shell open in the jtScratch addon directory. VS Code may
ask permission to run the automatic workspace task the first time.

Run `jtScratch build` from the activated shell to build `scratch-editor` with
`npm run build`.

Run `jtScratch build desktop` to build an unsigned Windows NSIS x64 package
of `scratch-desktop`. The package is written to `scratch-desktop/dist`.
Build output is saved to `logs/build_scratch-editor.log` or
`logs/build_scratch-desktop.log`, respectively, and replaced on each build.

Run `jtScratch start` from the activated shell to start `scratch-editor` with
`npm start`.

## Memory requirements

The build and start processes can be slow on machines with limited memory. As
a reference, processing on an 8 GB machine can take five times as long as on a
32 GB machine. During a build, VS Code may mistake a temporarily unresponsive
WSL environment for a hang, which can cause the build to fail. If a build
fails this way, run it from an etrobo shell started in shell mode, or from the
addon terminal opened with `addonman open jtScratch terminal`, instead of
using the VS Code integrated terminal.
