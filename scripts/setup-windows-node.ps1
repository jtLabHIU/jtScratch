# Helper script for installing and switching Node.js versions
#   in Windows PowerShell
# Copyright (c) 2026 jtLab, Hokkaido Information University
# Contextualized by TANAHASHI, Jiro(aka jtFuruhata) <jt@do-johodai.ac.jp>
# Assisted by Copilot and Gemini
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#

# Receive the Node.js version to activate and optionally check without installing.
param (
    [Parameter(Mandatory = $true)]
    [string]$NodeVersion,
    [switch]$SwitchOnly
)

$addon_name = "jtScratch"
$script_name = "setup-windows-node.ps1"

# Stop on PowerShell errors so the catch block can report setup failures.
$ErrorActionPreference = 'Stop'

# Refresh this process's environment variables from the Windows registry.
function Update-EnvironmentFromRegistry {
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $pathEntries = @($machinePath, $userPath)

    foreach ($name in @('NVM_HOME', 'NVM_SYMLINK')) {
        $value = [Environment]::GetEnvironmentVariable($name, 'User')
        if ([string]::IsNullOrWhiteSpace($value)) {
            $value = [Environment]::GetEnvironmentVariable($name, 'Machine')
        }
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
            $pathEntries += $value
        }
    }

    $env:Path = ($pathEntries | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique) -join ';'
}

# Locate nvm.exe using NVM_HOME first, then the current process PATH.
function Find-NvmExecutable {
    if (-not [string]::IsNullOrWhiteSpace($env:NVM_HOME)) {
        $nvmPath = Join-Path $env:NVM_HOME 'nvm.exe'
        if (Test-Path -LiteralPath $nvmPath -PathType Leaf) {
            return $nvmPath
        }
    }

    $nvmCommand = Get-Command 'nvm.exe' -ErrorAction SilentlyContinue
    if ($null -ne $nvmCommand) {
        return $nvmCommand.Source
    }

    return $null
}

try {
    # Normalize and validate the requested Node.js version.
    $NodeVersion = $NodeVersion.Trim()
    if ([string]::IsNullOrWhiteSpace($NodeVersion)) {
        throw 'A Node.js version is required.'
    }
    if ($NodeVersion.StartsWith('v')) {
        $NodeVersion = $NodeVersion.Substring(1)
    }

    # Refresh the environment and locate nvm-windows.
    Update-EnvironmentFromRegistry
    $nvmPath = Find-NvmExecutable

    # Install nvm-windows with winget when installation is allowed and nvm is missing.
    if ([string]::IsNullOrWhiteSpace($nvmPath)) {
        if ($SwitchOnly) {
            throw 'nvm-windows is not installed. Run jtScratch install first.'
        }

        $wingetCommand = Get-Command 'winget.exe' -ErrorAction SilentlyContinue
        if ($null -eq $wingetCommand) {
            throw 'winget is not available. Install nvm-windows and retry.'
        }

        $wingetArguments = @(
            'install',
            '--id', 'CoreyButler.NVMforWindows',
            '--exact',
            '--silent',
            '--accept-package-agreements',
            '--accept-source-agreements'
        )
        & $wingetCommand.Source @wingetArguments
        if ($LASTEXITCODE -ne 0) {
            throw "winget could not install nvm-windows (exit code $LASTEXITCODE)."
        }

        Update-EnvironmentFromRegistry
        $nvmPath = Find-NvmExecutable
        if ([string]::IsNullOrWhiteSpace($nvmPath)) {
            throw 'nvm-windows was installed but nvm.exe was not found. Restart Windows and retry.'
        }
    }

    # Read installed Node.js versions and check whether the requested version is present.
    $installedVersions = & $nvmPath list
    if ($LASTEXITCODE -ne 0) {
        throw "nvm-windows could not list installed Node.js versions (exit code $LASTEXITCODE)."
    }

    $versionPattern = "(?i)^\s*(?:\*)?\s*v?$([regex]::Escape($NodeVersion))(?=\s|$)"
    $nodeVersionIsInstalled = $installedVersions | Where-Object { $_ -match $versionPattern }

    # Install the requested version unless SwitchOnly requires it to already exist.
    if (-not $nodeVersionIsInstalled) {
        if ($SwitchOnly) {
            throw "Node.js $NodeVersion is not installed on Windows. Run jtScratch install first."
        }

        & $nvmPath install $NodeVersion
        if ($LASTEXITCODE -ne 0) {
            throw "nvm-windows could not install Node.js $NodeVersion (exit code $LASTEXITCODE)."
        }
    }

    # Activate the requested Node.js version and report success.
    & $nvmPath use $NodeVersion
    if ($LASTEXITCODE -ne 0) {
        throw "nvm-windows could not activate Node.js $NodeVersion (exit code $LASTEXITCODE)."
    }

    Write-Output "Windows Node.js $NodeVersion is ready and active."
    exit 0
}
# Report setup or activation errors to stderr and return a failure exit code.
catch {
    [Console]::Error.WriteLine("Error: $($_.Exception.Message)")
    exit 1
}
