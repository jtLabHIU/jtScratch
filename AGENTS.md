# jtScratch Development Guide

> Copyright (c) 2026 jtLab, Hokkaido Information University  
> Contextualized by TANAHASHI, Jiro(aka jtFuruhata) <jt@do-johodai.ac.jp>  
> See LICENSE

このファイルは、`addon/jtScratch` を対象とするAIエージェントおよび開発者向けの作業指針です。
`addon/jtScratch` 自体が独立したGitリポジトリです。作業対象を変更する場合は、
リポジトリの境界を確認し、外側のetroboリポジトリと混同しないでください。

## 概要

`jtScratch` は、etrobo環境に棚橋研究室版Scratch3関連のリポジトリとビルド環境を追加するアドオンです。

- `scripts/jtScratch` はサブコマンドのディスパッチャーです。
- `scripts/install` はリポジトリ、Node.js/nvm、OS依存パッケージを準備します。
- `scripts/activate` は `.nvmrc` に指定されたNode.jsを有効化し、対話シェルを起動します。
- `scripts/build` は `scratch-editor` またはWindows版 `scratch-desktop` をビルドします。
- `scripts/start` は `scratch-editor` を開発サーバーとして起動します。
- `repos/` は、クローン先の場所にかかわらず内部スクリプトが同じパスで外部リポジトリを参照できるようにするシンボリックリンクです。リポジトリ本体はこのディレクトリにコミットしません。
- `logs/` はインストールおよびビルドのログ配置先です。

内部スクリプトは、外部リポジトリを次の固定パスから参照します。これらの実際のクローン先は `repos/` のリンク先であり、ユーザーが手作業で配置するのではなく、通常は `jtScratch install` が準備します。

- `repos/scratch-editor`: https://github.com/jtLabHIU/scratch-editor.git
- `repos/scratch-desktop`: https://github.com/jtLabHIU/scratch-desktop.git
- `repos/s3h`: https://github.com/jtLabHIU/s3h.git

実際のクローン先は `jtScratch install` の引数、または既定の `$ETROBO_USERPROFILE/jtScratchRepos` で決まります。Windows側からもリポジトリを使う処理があるため、Windows環境ではクローン先をWindowsファイルシステムからアクセスできる場所にします。

## 作業前の確認

1. 変更対象がアドオン本体か、インストール先の外部リポジトリかを確認する。jtScratch関連のセッションでは、`repos/` のリンク先にあるクローン済み外部リポジトリを変更しない。jtScratch配下のこのリポジトリが管理する範囲外のファイルを変更する必要がある場合は、変更前に都度ユーザーに確認する。
2. `README.md`、対象スクリプト、および `jtScratch.code-workspace` の動作を確認する。
3. 不要な変更、生成物、既存の外部リポジトリ変更を上書きしない。
4. 作業前後で `git status --short` を確認する。

## コマンド

コマンドは通常、etrobo環境で初期化されたシェルから実行します。

```sh
# リポジトリとNode.js環境をインストール
jtScratch install [<absolute-path-to-jtScratchRepos>]

# 環境を有効化し、アドオンディレクトリで対話シェルを開く
jtScratch activate

# scratch-editorをビルド
jtScratch build

# Windows版scratch-desktopをビルド
jtScratch build desktop

# scratch-editorを起動
jtScratch start

# 環境の無効化
jtScratch activate deactivate
```

VS Codeでは、`jtScratch.code-workspace` を開くと自動タスクによって環境が有効化されます。
変更後は少なくとも `bash -n scripts/<対象スクリプト>` を実行し、シェル構文を検証します。

## シェルスクリプト規約

- Bashスクリプトは `#!/usr/bin/env bash` を使用します。
- `if` の条件式では角括弧を省略せず、比較演算子は統一して `[ "$a" == "$b" ]` の形式を使います。
- 変数は参照時に原則としてダブルクォートで囲み、パスはシェル展開前に検証します。
- 失敗時は標準エラーへ具体的な原因を出し、成功時と区別できるエラー文にします。
- コマンドの終了コードを確認し、失敗を黙って無視しません。
- 長くても人間が追いやすいコードを優先します。
- 処理のブロックごとに、その動作内容を表すコメントを平易な英語で書きます。
- `--help`/`usage` と `--version`/`version`/`ver` の動作を維持します。
- サブコマンド名とスクリプト名を一致させます。

## パスと環境変数

- アドオンの絶対パスは `$ETROBO_ADDON/$addon_name` または `$addon_dir` として扱います。
- `$NVM_DIR` は未設定時に `$HOME/.nvm` を使用します。
- Node.jsのバージョンは `repos/scratch-editor/.nvmrc` を正として扱います。
- `jtScratchRepos` は実際のクローン先です。絶対パスで指定し、未指定時は `$ETROBO_USERPROFILE/jtScratchRepos` を使用します。Windows環境ではWindowsファイルシステムからアクセス可能な場所を指定します。
- WSLでは、Windows側のパス変換に `wslpath`、Node.jsのセットアップに `powershell.exe` を必要に応じて使用します。
- `repos` は実際のクローン先を指すシンボリックリンクとし、内部スクリプトからの固定された参照パスとして扱います。既存のリンク先を勝手に削除・変更しません。
- `ETROBO_ADDON_JTSCRATCH_ACTIVATION` は有効化済みシェルでのみ `activated` を設定します。

## インストール仕様

- リポジトリ取得順は `scratch-editor`、`scratch-desktop`、`s3h` です。
- `scripts/install` が実際のクローン先を準備し、`repos/` のシンボリックリンクを作成します。リンクを配置するファイルシステムはNTFSなどシンボリックリンクをサポートする必要があることをユーザーに案内します。
- 対象ディレクトリが存在する場合は再cloneせず、Gitリポジトリとして利用します。
- 既存ディレクトリがGitリポジトリでない場合は、誤った上書きをせずエラーにします。
- 各リポジトリのログは別々に `logs/install_<repository-name>.log`へ保存します。
- ビルドに必要な基本パッケージは、エージェントが必要に応じて判断します。
- Windows Electronビルドに必要なパッケージも、エージェントが必要に応じて判断します。
- WSLでは、Linux側のnvm/Node.js環境を準備し、そのインストール完了後、Windows側でのデバッグに必要なNode.js環境を別途用意したPowerShellスクリプトで準備します。Node.jsのバージョン管理にはnvmを使用します。
- インストール中に外部通信や管理者権限が必要な処理を行う場合は、その目的をユーザーに示します。失敗した場合は、原因と対処方法、または確認すべきログを案内します。

## 環境有効化の仕様

- `scripts/activate` は主に `addonman open jtScratch` から呼び出され、ビルドや実行に必要な環境を有効化します。
- 有効化されたシェルでは `ETROBO_ADDON_JTSCRATCH_ACTIVATION` を `activated` に設定し、有効化されていない場合は未設定にします。
- nvm、必要なNode.jsバージョン、または `repos/scratch-editor/.nvmrc` が存在しない場合は、`jtScratch install` を呼び出して準備します。
- Windows側も必要に応じてnvmでNode.jsのバージョンを切り替え、環境が準備されていない場合は `jtScratch install` を呼び出します。Windows側の処理には別途PowerShellスクリプトを使用できます。
- `jtScratch activate deactivate` または `jtScratch activate --deactivate` では、Linux側のNode.jsをnvmのデフォルトバージョンに戻します。Windows側のNode.jsバージョンは変更しなくても構いません。
- 有効化または無効化の最後に対話Bashを起動し、カレントディレクトリをアドオンディレクトリにします。

## ビルド仕様

- `jtScratch build` は `repos/scratch-editor` で `npm run build` を実行します。
- `jtScratch start` は `repos/scratch-editor` で `npm start` を実行し、開発サーバーを起動します。
- `jtScratch build desktop` は `repos/scratch-desktop` でクリーン、メディア取得、コンパイルを行い、Windows向けのNSIS x64パッケージを公開せずにビルドします。
- ビルドログはリポジトリごとに `logs/build_<repository-name>.log` へ保存し、ビルドのたびに同じファイルを上書きします。
- `s3h` のビルドは今後の課題とし、現時点では実行しません。

## ビルドと検証

変更がスクリプトに影響する場合は、アドオンディレクトリで `scripts/` 配下のPowerShellスクリプト以外のファイルを `bash -n` で確認します。

```sh
failed=0
while IFS= read -r -d '' script; do
    bash -n "$script" || failed=1
done < <(find scripts -type f ! -name '*.ps1' -print0)
[ "$failed" == 0 ]
```

PowerShellスクリプトも、PowerShellでアドオンディレクトリから構文を確認します。スクリプト自体は実行しません。

```powershell
$failed = $false
Get-ChildItem -Path scripts -Filter '*.ps1' -File -Recurse | ForEach-Object {
    $tokens = $null
    $parseErrors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors) {
        $parseErrors | ForEach-Object { Write-Error $_ }
        $failed = $true
    }
}
if ($failed) { throw 'PowerShell syntax check failed.' }
```

アドオンディレクトリで回帰テストを実行します。テストは一時ディレクトリと模擬コマンドを使用します。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

あわせて、アドオンディレクトリで変更内容を確認します。

```sh
git --no-pager diff --check
git --no-pager diff
```

環境準備や実ビルドは副作用が大きいため、リポジトリ取得、sudoによるAPT、nvm、npm、Wine設定を自動実行しません。
動作確認が必要な場合は、既に準備済みのシェルとリポジトリを使用し、実行内容と副作用を事前に説明します。
実行した場合も、外部リポジトリのソースや依存関係をこのアドオンの作業ディレクトリへ無断で変更しません。

## テンプレートとしての利用ルール

このファイルはテンプレートです。新しいサブコマンドや仕様を追加する場合は、次を合わせて更新してください。

- 対応する `scripts/<subcommand>` を追加する。
- `README.md` に利用方法と副作用を記載する。
- `jtScratch.code-workspace` がタスク変更に影響するか確認する。
- ヘルプ、バージョン表示、エラー処理、ログ出力の規約に従う。
- この `AGENTS.md` のコマンド一覧は必ず更新し、ディレクトリ説明を含むその他の記載も必要に応じて更新する。
