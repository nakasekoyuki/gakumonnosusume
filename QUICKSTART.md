# クイックスタートガイド（完全初心者向け）

## これだけやればOK！チェックリスト

### ☑️ 準備編（最初の1回だけ）

#### 1. GitHubからダウンロード
- [ ] GitHubのこのページで緑色の「Code」ボタンをクリック
- [ ] 「Download ZIP」をクリック
- [ ] ダウンロードしたZIPファイルを解凍
- [ ] 解凍したフォルダをデスクトップに移動
- [ ] フォルダ名を `gakumonnosusume` にする（`-main`を削除）

#### 2. Pythonをインストール
- [ ] https://www.python.org/downloads/ にアクセス
- [ ] 黄色いボタンをクリックしてダウンロード
- [ ] インストール時に **「Add Python to PATH」にチェック**（重要！）
- [ ] インストール完了

#### 3. ターミナルを開く
**Windows:**
- [ ] Windowsキーを押す
- [ ] 「cmd」と打つ
- [ ] 「コマンドプロンプト」をクリック

**Mac:**
- [ ] Command+スペース
- [ ] 「ターミナル」と打つ
- [ ] Enter

#### 4. フォルダに移動
ターミナルで打つ：
```bash
cd Desktop/gakumonnosusume
```
（デスクトップ以外に置いた場合は、そのパスを指定）

#### 5. 必要な部品をインストール
```bash
pip install -r requirements.txt
```
⏰ 5-10分かかります。待ちましょう。

#### 6. APIキーを取得
- [ ] https://console.anthropic.com/ にアクセス
- [ ] アカウント作成（メールアドレス＋パスワード）
- [ ] 左メニュー「API Keys」をクリック
- [ ] 「Create Key」をクリック
- [ ] 表示されたキー（`sk-ant-...`）をコピー

#### 7. APIキーを設定
**Windows:**
```bash
copy .env.example .env
notepad .env
```

**Mac:**
```bash
cp .env.example .env
open -a TextEdit .env
```

開いたファイルで：
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```
↓ 変更
```
ANTHROPIC_API_KEY=sk-ant-（ここにコピーしたキーを貼り付け）
```

保存して閉じる。

#### 8. セットアップを実行
```bash
python -m src.cli setup
```
⏰ 初回は5-10分かかります。

「✅ セットアップが完了しました!」と表示されたらOK！

---

### ☑️ 使用編（毎回やること）

#### 1. ターミナルを開く
- Windows: 「cmd」で検索
- Mac: Command+スペース → 「ターミナル」

#### 2. フォルダに移動
```bash
cd Desktop/gakumonnosusume
```

#### 3. 文章を生成
```bash
python -m src.cli generate "あなたのテーマ"
```

例：
```bash
python -m src.cli generate "AI時代における教育の重要性"
```

10-30秒待つと、福沢諭吉風の文章が表示されます！

---

## よく使うコマンド集

### 対話モード（何度も生成したい時）
```bash
python -m src.cli interactive
```
テーマを入力 → 文章生成 → また入力... を繰り返せます
終了は「exit」と入力

### ファイルに保存
```bash
python -m src.cli generate "テーマ" -o output/article.txt
```
`output/article.txt` というファイルができます

### 参考文章を見る
```bash
python -m src.cli generate "テーマ" --show-context
```
どの福沢諭吉の文章を参考にしたか表示されます

### 関連文章を検索するだけ
```bash
python -m src.cli search "学問"
```

---

## トラブルシューティング

### 「python: command not found」
→ Pythonがインストールされていない
→ https://www.python.org/downloads/ からインストール
→ **「Add to PATH」にチェック！**

### 「No module named 'langchain'」
→ 部品がインストールされていない
→ `pip install -r requirements.txt` を実行

### 「ベクトルストアが見つかりません」
→ セットアップしていない
→ `python -m src.cli setup` を実行

### 「ANTHROPIC_API_KEY が設定されていません」
→ `.env` ファイルにAPIキーを書いていない
→ `.env` を開いてAPIキーを貼り付け

### 文章生成が遅い
→ 正常です。10-30秒かかります
→ ネットワークに接続されているか確認

---

## テキストを追加したい場合

より精度を上げるには、福沢諭吉のテキストを追加しましょう。

### 1. 青空文庫からダウンロード
- https://www.aozora.gr.jp/ にアクセス
- 「福沢諭吉」で検索
- 好きな作品を選ぶ
- 「テキストファイル（ルビあり）」をダウンロード

### 2. ファイルを移動
- ダウンロードした `.txt` ファイルを
- `gakumonnosusume/data/fukuzawa_texts/` フォルダにコピー

### 3. データベースを更新
```bash
python -m src.cli setup --force
```

これでより多くの参考文章を使えます！

---

## 料金について

**Claude APIの料金:**
- 初回：$5の無料クレジット（約700円分）
- 1記事生成：約5-10円
- 月額料金なし（使った分だけ）

**$5で約50-100記事生成できます**

---

## 困った時は

- README.md を読む（詳しい説明）
- エラーメッセージをコピーしてGoogle検索
- GitHubのIssuesで質問

---

## まとめ

**初回セットアップ（1回だけ）:**
1. GitHubからZIPダウンロード
2. Python インストール
3. `pip install -r requirements.txt`
4. APIキー取得＆設定
5. `python -m src.cli setup`

**使う時（毎回）:**
1. ターミナルを開く
2. `cd Desktop/gakumonnosusume`
3. `python -m src.cli generate "テーマ"`

**これだけです！**
