import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ADDON_DIR = Path(__file__).resolve().parents[1]


class ScriptValidationTests(unittest.TestCase):
    def test_build_logs_are_separate_and_include_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            addon = root / "jtScratch"
            editor = addon / "repos/scratch-editor"
            desktop = addon / "repos/scratch-desktop"
            commands = root / "commands"
            for directory in (editor, desktop, commands, desktop / "node_modules/.bin"):
                directory.mkdir(parents=True, exist_ok=True)
            for repository in (editor, desktop):
                (repository / "package.json").write_text("{}")
            npm = commands / "npm"
            npm.write_text(
                '#!/usr/bin/env bash\n'
                'echo "npm stdout: $*"\n'
                'echo "npm stderr: $*" >&2\n'
                'if [ "$FAIL_NPM" == "$*" ]; then exit 7; fi\n'
            )
            npm.chmod(0o755)
            builder = desktop / "node_modules/.bin/electron-builder"
            builder.write_text('#!/usr/bin/env bash\necho "packaged: $*"\n')
            builder.chmod(0o755)
            environment = os.environ.copy()
            environment.update(
                ETROBO_ADDON=str(root),
                PATH=f"{commands}{os.pathsep}{environment['PATH']}",
                FAIL_NPM="",
            )
            script = str(ADDON_DIR / "scripts/build")
            help_result = subprocess.run(
                ["bash", script, "--help"], env=environment, capture_output=True, text=True
            )
            self.assertEqual(help_result.returncode, 0)
            self.assertFalse((addon / "logs").exists())
            editor_result = subprocess.run(
                ["bash", script], env=environment, capture_output=True, text=True
            )
            self.assertEqual(editor_result.returncode, 0, editor_result.stderr)
            editor_log = addon / "logs/build_scratch-editor.log"
            self.assertIn("npm stdout: run build", editor_log.read_text())
            self.assertIn("npm stderr: run build", editor_log.read_text())
            self.assertIn("npm stderr: run build", editor_result.stdout)

            desktop_result = subprocess.run(
                ["bash", script, "desktop"],
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertEqual(desktop_result.returncode, 0, desktop_result.stderr)
            desktop_log = addon / "logs/build_scratch-desktop.log"
            self.assertIn("npm stdout: run clean", desktop_log.read_text())
            self.assertIn("npm stdout: run fetch", desktop_log.read_text())
            self.assertIn("npm stdout: run compile", desktop_log.read_text())
            self.assertIn("packaged: --win nsis --x64 --publish never", desktop_log.read_text())
            self.assertIn("npm stdout: run build", editor_log.read_text())

            environment["FAIL_NPM"] = "run build"
            failed_result = subprocess.run(
                ["bash", script], env=environment, capture_output=True, text=True
            )
            self.assertNotEqual(failed_result.returncode, 0)
            self.assertIn(str(editor_log), failed_result.stderr)
            self.assertIn("npm stderr: run build", editor_log.read_text())
            self.assertNotIn("completed successfully", editor_log.read_text())
            self.assertIn("packaged:", desktop_log.read_text())

    def test_build_stops_if_log_cannot_be_created(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log_path = root / "jtScratch/logs/build_scratch-editor.log"
            log_path.mkdir(parents=True)
            environment = os.environ.copy()
            environment["ETROBO_ADDON"] = str(root)
            result = subprocess.run(
                ["bash", str(ADDON_DIR / "scripts/build")],
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"Could not write log file: {log_path}", result.stderr)

    def test_unknown_subcommand_reports_error_on_stderr(self):
        environment = os.environ.copy()
        environment["ETROBO_ADDON"] = str(ADDON_DIR.parent)
        result = subprocess.run(
            ["bash", str(ADDON_DIR / "scripts/jtScratch"), "not-a-subcommand"],
            env=environment,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not-a-subcommand", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_existing_repository_must_be_valid(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repos = root / "repos"
            logs = root / "logs"
            repository = repos / "s3h"
            repository.mkdir(parents=True)
            logs.mkdir()
            (repository / ".git").mkdir()

            environment = os.environ.copy()
            environment.update(
                INSTALL_SCRIPT=str(ADDON_DIR / "scripts/install"),
                jt_scratch_repos=str(repos),
                logs_dir=str(logs),
            )
            command = (
                'set -o pipefail; bash() { echo "mock npm install"; }; '
                'source <(sed -n \'/^install_repository() {$/,/^}$/p\' "$INSTALL_SCRIPT"); '
                'install_repository s3h example'
            )
            result = subprocess.run(
                ["bash", "-c", command], env=environment, capture_output=True, text=True
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not a valid Git repository", result.stderr)
            self.assertNotIn("mock npm install", result.stdout)

            (repository / ".git").rmdir()
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            result = subprocess.run(
                ["bash", "-c", command], env=environment, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Using existing repository", result.stdout)
            self.assertIn("mock npm install", result.stdout)

    def test_activation_rejects_missing_nvm_after_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            addon = root / "jtScratch"
            editor = addon / "repos/scratch-editor"
            editor.mkdir(parents=True)
            (editor / ".nvmrc").write_text("20\n")
            scripts = addon / "scripts"
            scripts.mkdir()
            installer = scripts / "install"
            installer.write_text("#!/usr/bin/env bash\nexit 0\n")
            installer.chmod(0o755)
            environment = os.environ.copy()
            environment.update(ETROBO_ADDON=str(root), NVM_DIR=str(root / "missing-nvm"))
            result = subprocess.run(
                ["bash", str(ADDON_DIR / "scripts/activate")],
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("nvm is not installed", result.stderr)
            self.assertIn("after installation", result.stderr)

    def test_install_rejects_nvm_load_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            commands = root / "commands"
            commands.mkdir()
            for name, body in (("sudo", "exit 0"), ("dpkg", "echo i386")):
                command = commands / name
                command.write_text(f"#!/usr/bin/env bash\n{body}\n")
                command.chmod(0o755)
            nvm = root / "nvm"
            nvm.mkdir()
            (nvm / "nvm.sh").write_text("return 2\n")
            environment = os.environ.copy()
            environment.update(
                ETROBO_ADDON=str(ADDON_DIR.parent),
                NVM_DIR=str(nvm),
                PATH=f"{commands}{os.pathsep}{environment['PATH']}",
            )
            result = subprocess.run(
                ["bash", str(ADDON_DIR / "scripts/install"), str(root / "repos")],
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Could not load nvm", result.stderr)
            self.assertFalse((root / "repos").exists())

    @unittest.skipUnless(
        shutil.which("powershell.exe") and shutil.which("wslpath"),
        "Windows PowerShell and wslpath are required",
    )
    def test_windows_node_script_has_script_parameters(self):
        script = subprocess.check_output(
            ["wslpath", "-w", str(ADDON_DIR / "scripts/setup-windows-node.ps1")],
            text=True,
        ).strip()
        environment = os.environ.copy()
        environment["JTSCRATCH_TEST_SCRIPT"] = script
        environment["WSLENV"] = ":".join(
            filter(None, [environment.get("WSLENV"), "JTSCRATCH_TEST_SCRIPT"])
        )
        command = (
            "$tokens = $null; $errors = $null; "
            "$ast = [System.Management.Automation.Language.Parser]::ParseFile("
            "$env:JTSCRATCH_TEST_SCRIPT, [ref]$tokens, [ref]$errors); "
            "if ($errors.Count -ne 0 -or $null -eq $ast.ParamBlock) { exit 1 }; "
            "$names = @($ast.ParamBlock.Parameters | ForEach-Object { $_.Name.VariablePath.UserPath }); "
            "if ('NodeVersion' -notin $names -or 'SwitchOnly' -notin $names) { exit 1 }"
        )
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", command],
            env=environment,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
