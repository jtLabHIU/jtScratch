# jtScratch
etrobo environment addon for jtScratch and jtS3H.

## Install repositories

Run `jtScratch install [<absolute path to jtScratchRepos>]`. If the path is
omitted, repositories are stored in `$HOME/jtScratchRepos`. The addon exposes
that directory at `repos` through a symbolic link, so the filesystem containing
the addon must support symbolic links (for example, NTFS).

The installer clones `scratch-editor` and then `s3h` when their directories do
not already exist. Existing Git repositories are reused without cloning, and
`npm install` is run in either case. The installer reads the Node.js version
from `scratch-editor/.nvmrc`, installs and activates it with nvm, and installs
nvm itself if needed. It uses `sudo apt` to install Git, curl, and the build
tools required by native npm dependencies (`build-essential` and `python3`).
Their logs are written separately to `logs/scratch-editor.log` and
`logs/s3h.log`.

Opening `jtScratch.code-workspace` starts an integrated terminal and runs
`jtScratch activate`. This activates the Node.js version specified by
`scratch-editor/.nvmrc` with nvm, then leaves an interactive shell open in the
jtScratch addon directory. VS Code may ask permission to run the automatic
workspace task the first time.

Run `jtScratch build` from the activated shell to build `scratch-editor` with
`npm run build`.

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
