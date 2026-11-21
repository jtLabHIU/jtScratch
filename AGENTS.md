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

- `repos/scratch-editor`
- `repos/scratch-desktop`
- `repos/s3h`

実際のクローン先は `jtScratch install` の引数、または既定の `$ETROBO_USERPROFILE/jtScratchRepos` で決まります。Windows側からもリポジトリを使う処理があるため、Windows環境ではクローン先をWindowsファイルシステムからアクセスできる場所にしてください。

## 作業前の確認

1. 変更対象がアドオン本体か、インストール先の外部リポジトリかを確認する。
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
- 入力変値は原則としてダブルクォートで囲み、パスはシェル展開前に検証します。
- 失敗時は標準エラーへ具体的な原因を出し、成功時と区別できるエラー文にします。
- コマンドの終了コードを確認し、失敗を黙って無視しません。
- 長くても人間が追いやすいコードを優先します。
- `--help`/`usage` と `--version`/`version`/`ver` の動作を維持します。
- サブコマンド名とスクリプト名を一致させます。

## パスと環境変数

- アドオンの絶対パスは `$ETROBO_ADDON/$addon_name` または `$addon_dir` として扱います。
- `$NVM_DIR` は未設定時に `$HOME/.nvm` を使用します。
- Node.jsのバージョンは `repos/scratch-editor/.nvmrc` を正として扱います。
- `jtScratchRepos` は実際のクローン先です。絶対パスで指定し、未指定時は `$ETROBO_USERPROFILE/jtScratchRepos` を使用します。Windows環境ではWindowsファイルシステムからアクセス可能な場所を指定します。
- WSLでは、Windows側のパス変換に `wslpath`、Node.jsのセットアップに `powershell.exe` を必要に応じて使用します。
- `repos` は実際のクローン先を指すシンボリックリンクとして維持し、内部スクリプトからの固定された参照パスとして扱います。既存のリンク先を勝手に削除・変更しません。
- `ETROBO_ADDON_JTSCRATCH_ACTIVATION` は有効化済みシェルでのみ `activated` を設定します。

## インストール仕様

- リポジトリ取得順は `scratch-editor`、`scratch-desktop`、`s3h` です。
- `scripts/install` が実際のクローン先を準備し、`repos/` のシンボリックリンクを作成します。リンクを含むファイルシステムはシンボリックリンクをサポートする必要があります。
- 対象ディレクトリが存在する場合は再cloneせず、Gitリポジトリとして利用します。
- 既存ディレクトリがGitリポジトリでない場合は、誤った上書きをせずエラーにします。
- 各リポジトリのログは別々に `logs/<repository-name>.log`へ保存します。
- 基本パッケージはGit、curl、build-essential、python3です。
- Windows ElectronビルドにはWine/i386、mono-devel、libnss3が必要です。
- WSLでは、Linux側とWindows側のnvm/Node.js環境を必要に応じて準備します。
- 外部通信や管理者権限を伴う処理は、変更理由と失敗時の案内を明確にします。

## ビルドと検証

変更がスクリプトに影響する場合は、以下を可能な範囲で実行します。

```sh
bash -n scripts/jtScratch
bash -n scripts/install
bash -n scripts/activate
bash -n scripts/build
bash -n scripts/start

git --no-pager diff --check
git --no-pager diff -- addon/jtScratch
```

環境準備や実ビルドは副作用が大きいため、リポジトリ取得、sudoによるAPT、nvm、npm、Wine設定を自動実行しないでください。
動作確認が必要な場合は、既に準備済みのシェルとリポジトリを使用し、実行内容と副作用を事前に説明します。
実行した場合も、外部リポジトリのソースや依存関係をこのアドオンの作業ディレクトリへ無断で変更しません。

## テンプレートとしての利用ルール

このファイルはテンプレートです。新しいサブコマンドや仕様を追加する場合は、次を合わせて更新してください。

- 対応する `scripts/<subcommand>` を追加する。
- `README.md` に利用方法と副作用を記載する。
- `jtScratch.code-workspace` がタスク変更に影響するか確認する。
- ヘルプ、バージョン表示、エラー処理、ログ出力の規約を維持する。
- この `AGENTS.md` のコマンド一覧とディレクトリ説明を更新する。