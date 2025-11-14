# 学問のすゝめ (Gakumon no Susume) - 福沢諭吉風テキストジェネレーター

福沢諭吉のテキストを参照して、福沢諭吉の文体と論理形態で文章を生成するシステムです。

## 特徴

### 二段階生成アプローチ

1. **RAG（Retrieval Augmented Generation）層**
   - 福沢諭吉の実際のテキストからテーマに関連する文章を検索
   - 関連性の高い参考文章をコンテキストとして提供

2. **文体・論理形態プロンプト層**
   - 福沢諭吉の文体特徴を体系化したガイドライン
   - 論理展開パターン（問題提起→批判→解決策、対比論法など）
   - 「である」調、実学重視、独立自尊の精神を反映

### 技術スタック

- **LangChain**: RAGフレームワーク
- **ChromaDB**: ベクトルデータベース
- **Claude/GPT-4**: 高品質な日本語生成
- **Multilingual-E5**: 日本語対応埋め込みモデル

## インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd gakumonnosusume
```

### 2. 仮想環境の作成（推奨）

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

```bash
cp .env.example .env
```

`.env` ファイルを編集して、APIキーを設定してください：

```bash
# Anthropic (Claude) - 推奨
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# または OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# LLMプロバイダー選択
LLM_PROVIDER=anthropic  # または openai
```

### 5. CLIツールのインストール（オプション）

```bash
pip install -e .
```

これにより、`gakumon` コマンドがどこからでも使えるようになります。

## 使い方

### 初期セットアップ

福沢諭吉のテキストファイルを `data/fukuzawa_texts/` に配置してください。

テキストファイルがない場合、サンプルテキストで試すことができます：

```bash
python -m src.cli setup
```

または（インストール後）：

```bash
gakumon setup
```

### テキストの準備

`data/fukuzawa_texts/` ディレクトリに `.txt` ファイルを追加してください：

```
data/fukuzawa_texts/
├── gakumon_no_susume.txt       # 学問のすゝめ
├── bunmeiron_no_gairyaku.txt   # 文明論之概略
├── fukuo_jiden.txt             # 福翁自伝
└── ...
```

テキストを追加したら、ベクトルストアを再作成：

```bash
gakumon setup --force
```

### 文章生成

#### コマンドライン

```bash
gakumon generate "AI時代における教育の重要性"
```

オプション：

```bash
# 参考文章を表示
gakumon generate "教育改革" --show-context

# ファイルに保存
gakumon generate "独立自尊の精神" -o output/article.md

# 検索する関連文章の数を変更
gakumon generate "文明開化" --retrieval-k 10

# OpenAIを使用
gakumon generate "実学の価値" --provider openai
```

#### 対話モード

```bash
gakumon interactive
```

対話的にテーマを入力して文章を生成できます。

#### プログラムから使用

```python
from src.vectorstore import setup_vectorstore
from src.generator import FukuzawaTextGenerator

# ベクトルストアをセットアップ
vectorstore = setup_vectorstore()

# ジェネレーターを作成
generator = FukuzawaTextGenerator(vectorstore=vectorstore)

# 文章を生成
article = generator.generate(
    theme="明治時代の教育改革",
    retrieval_k=5
)

print(article)
```

### 検索機能

ベクトルストアから関連文章を検索：

```bash
gakumon search "学問の目的"
```

## プロジェクト構造

```
gakumonnosusume/
├── data/
│   └── fukuzawa_texts/          # 福沢諭吉のテキスト格納
├── prompts/
│   └── fukuzawa_style_guide.md  # 文体・論理形態ガイド
├── src/
│   ├── __init__.py
│   ├── loader.py                # テキスト読み込み
│   ├── vectorstore.py           # ベクトルDB管理
│   ├── generator.py             # 文章生成エンジン
│   └── cli.py                   # CLIインターフェース
├── chroma_db/                   # ベクトルストア（自動生成）
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
└── README.md
```

## カスタマイズ

### 文体ガイドの編集

`prompts/fukuzawa_style_guide.md` を編集して、文体や論理形態の指示をカスタマイズできます。

### パラメータ調整

`.env` ファイルで各種パラメータを調整：

```bash
# モデル設定
MODEL_NAME=claude-3-5-sonnet-20241022
TEMPERATURE=0.7
MAX_TOKENS=2000

# RAG設定
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=5

# 埋め込みモデル
EMBEDDING_MODEL=intfloat/multilingual-e5-large
```

## 開発

### テストの実行

```bash
# ローダーのテスト
python -m src.loader

# ベクトルストアのテスト
python -m src.vectorstore

# ジェネレーターのテスト（要APIキー）
python -m src.generator
```

### 新しいテキストの追加

1. `.txt` ファイルを `data/fukuzawa_texts/` に追加
2. ベクトルストアを再作成: `gakumon setup --force`
3. 完了！

## トラブルシューティング

### ベクトルストアが見つからない

```bash
gakumon setup
```

を実行してベクトルストアを作成してください。

### APIキーエラー

`.env` ファイルに正しいAPIキーが設定されているか確認してください。

### メモリ不足

埋め込みモデルが大きい場合、メモリ不足になることがあります。
`.env` の `EMBEDDING_MODEL` をより小さいモデルに変更してください：

```bash
EMBEDDING_MODEL=intfloat/multilingual-e5-small
```

### 生成結果が期待通りでない

- `prompts/fukuzawa_style_guide.md` を編集して指示を調整
- `RETRIEVAL_K` を増やして、より多くの参考文章を使用
- `TEMPERATURE` を調整（0.5-0.9の範囲で実験）

## ライセンス

MIT License

## 謝辞

このプロジェクトは福沢諭吉の偉大な著作から着想を得ています。
