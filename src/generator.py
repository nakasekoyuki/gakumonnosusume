"""福沢諭吉風の文章を生成するモジュール"""

import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from langchain.schema import Document
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from .vectorstore import FukuzawaVectorStore


class FukuzawaTextGenerator:
    """福沢諭吉風のテキストを生成するクラス"""

    def __init__(
        self,
        vectorstore: FukuzawaVectorStore,
        llm_provider: str = "anthropic",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        Args:
            vectorstore: FukuzawaVectorStoreインスタンス
            llm_provider: LLMプロバイダー ("openai" または "anthropic")
            model_name: 使用するモデル名
            temperature: 生成の温度パラメータ
            max_tokens: 最大トークン数
        """
        # 環境変数を読み込む
        load_dotenv()

        self.vectorstore = vectorstore
        self.llm_provider = llm_provider
        self.temperature = temperature
        self.max_tokens = max_tokens

        # LLMを初期化
        self.llm = self._initialize_llm(model_name)

        # 文体ガイドを読み込む
        self.style_guide = self._load_style_guide()

        # プロンプトテンプレートを作成
        self.prompt_template = self._create_prompt_template()

    def _initialize_llm(self, model_name: Optional[str]):
        """LLMを初期化する"""
        if self.llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY が環境変数に設定されていません")

            model = model_name or os.getenv(
                "MODEL_NAME", "claude-3-5-sonnet-20241022"
            )
            print(f"🤖 Claude を初期化中: {model}")

            return ChatAnthropic(
                api_key=api_key,
                model=model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

        elif self.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY が環境変数に設定されていません")

            model = model_name or os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
            print(f"🤖 OpenAI を初期化中: {model}")

            return ChatOpenAI(
                api_key=api_key,
                model=model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

        else:
            raise ValueError(f"未対応のLLMプロバイダー: {self.llm_provider}")

    def _load_style_guide(self) -> str:
        """文体ガイドを読み込む"""
        style_guide_path = Path("prompts/fukuzawa_style_guide.md")

        if not style_guide_path.exists():
            print("⚠️  文体ガイドが見つかりません。デフォルトを使用します。")
            return self._get_default_style_guide()

        with open(style_guide_path, "r", encoding="utf-8") as f:
            return f.read()

    def _get_default_style_guide(self) -> str:
        """デフォルトの文体ガイド"""
        return """
福沢諭吉の文体特徴:
- 断定的な「である」調
- 簡潔明瞭な文章
- 実学重視の論理展開
- 西洋文明との比較
- 具体例から一般原則への演繹
- 独立自尊の精神
"""

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """プロンプトテンプレートを作成する"""
        system_message = f"""あなたは福沢諭吉の文体と論理形態を完璧に模倣する文章生成AIです。

以下の文体ガイドに厳密に従って文章を書いてください:

{self.style_guide}

重要な指示:
1. 必ず福沢諭吉の「である」調で書くこと
2. 実学的・実践的な視点を重視すること
3. 具体例を用いて論を展開すること
4. 独立自尊の精神を忘れないこと
5. 現代の読者にも理解できる明快な論理展開を心がけること
"""

        human_message = """以下は福沢諭吉の実際のテキストからの参考文章です:

{context}

---

上記の参考文章と文体ガイドに基づき、以下のテーマについて福沢諭吉風の文章を書いてください:

テーマ: {theme}

{additional_instructions}
"""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message),
        ])

    def generate(
        self,
        theme: str,
        retrieval_k: int = 5,
        additional_instructions: str = "",
        show_context: bool = False,
    ) -> str:
        """
        テーマに基づいて福沢諭吉風の文章を生成する

        Args:
            theme: 文章のテーマ
            retrieval_k: RAGで取得する関連文章の数
            additional_instructions: 追加の指示
            show_context: 参考文章を表示するか

        Returns:
            生成された文章
        """
        print(f"\n📝 テーマ: {theme}")
        print(f"🔍 関連文章を検索中...")

        # RAGで関連文章を取得
        related_docs = self.vectorstore.search(theme, k=retrieval_k)

        if not related_docs:
            print("⚠️  関連文章が見つかりませんでした。一般的な文体で生成します。")
            context = "（参考文章なし）"
        else:
            context = self._format_context(related_docs)

        if show_context:
            print("\n📚 参考文章:")
            print("=" * 60)
            print(context)
            print("=" * 60)

        # プロンプトを構築
        messages = self.prompt_template.format_messages(
            context=context,
            theme=theme,
            additional_instructions=additional_instructions or "特になし",
        )

        print(f"\n✍️  文章を生成中...")

        # LLMで生成
        response = self.llm.invoke(messages)

        print(f"✅ 文章を生成しました\n")

        return response.content

    def _format_context(self, documents: List[Document]) -> str:
        """参考文章をフォーマットする"""
        formatted_parts = []

        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "不明")
            formatted_parts.append(f"【参考文章 {i}】 (出典: {source})\n{doc.page_content}\n")

        return "\n---\n\n".join(formatted_parts)

    def generate_with_structure(
        self,
        theme: str,
        structure: str = "序論・本論・結論",
        retrieval_k: int = 5,
    ) -> str:
        """
        指定された構造で文章を生成する

        Args:
            theme: 文章のテーマ
            structure: 文章の構造指定
            retrieval_k: RAGで取得する関連文章の数

        Returns:
            生成された文章
        """
        additional_instructions = f"""
文章は以下の構造で書いてください:
{structure}

各セクションを明確に区別し、論理的な流れを作ってください。
"""
        return self.generate(
            theme=theme,
            retrieval_k=retrieval_k,
            additional_instructions=additional_instructions,
        )


def create_generator(
    vectorstore_path: str = "chroma_db",
    llm_provider: Optional[str] = None,
) -> FukuzawaTextGenerator:
    """
    ジェネレーターを簡単に作成する便利関数

    Args:
        vectorstore_path: ベクトルストアのパス
        llm_provider: LLMプロバイダー

    Returns:
        FukuzawaTextGenerator インスタンス
    """
    load_dotenv()

    # 環境変数から設定を読み込む
    provider = llm_provider or os.getenv("LLM_PROVIDER", "anthropic")

    # ベクトルストアを読み込む
    vectorstore_manager = FukuzawaVectorStore(persist_directory=vectorstore_path)
    vectorstore_manager.load_vectorstore()

    # ジェネレーターを作成
    generator = FukuzawaTextGenerator(
        vectorstore=vectorstore_manager,
        llm_provider=provider,
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("MAX_TOKENS", "2000")),
    )

    return generator


if __name__ == "__main__":
    # テスト用
    from .vectorstore import setup_vectorstore
    from .loader import create_sample_texts

    # サンプルテキストとベクトルストアを準備
    create_sample_texts()
    vectorstore_manager = setup_vectorstore(force_recreate=True)

    # ジェネレーターを作成
    generator = FukuzawaTextGenerator(vectorstore=vectorstore_manager)

    # テスト生成
    theme = "AI時代における教育の重要性"
    article = generator.generate(theme, show_context=True)

    print("\n" + "=" * 80)
    print("生成された文章:")
    print("=" * 80)
    print(article)
    print("=" * 80)
