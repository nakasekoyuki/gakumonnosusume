"""ベクトルストアを管理し、福沢諭吉のテキストを検索するモジュール"""

import os
from pathlib import Path
from typing import List, Optional

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


class FukuzawaVectorStore:
    """福沢諭吉のテキストをベクトル化して検索可能にするクラス"""

    def __init__(
        self,
        persist_directory: str = "chroma_db",
        embedding_model: str = "intfloat/multilingual-e5-large",
        collection_name: str = "fukuzawa_texts",
    ):
        """
        Args:
            persist_directory: ベクトルデータベースの保存先
            embedding_model: 使用する埋め込みモデル
            collection_name: コレクション名
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        print(f"🔧 埋め込みモデルを初期化中: {embedding_model}")

        # 日本語対応の埋め込みモデルを初期化
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        self.vectorstore: Optional[Chroma] = None

    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """
        ドキュメントからベクトルストアを作成する

        Args:
            documents: ベクトル化するドキュメントのリスト

        Returns:
            作成されたベクトルストア
        """
        print(f"🔨 ベクトルストアを作成中...")
        print(f"   ドキュメント数: {len(documents)}")

        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
        )

        print(f"✅ ベクトルストアを作成しました: {self.persist_directory}")
        return self.vectorstore

    def load_vectorstore(self) -> Chroma:
        """
        既存のベクトルストアを読み込む

        Returns:
            読み込んだベクトルストア

        Raises:
            FileNotFoundError: ベクトルストアが存在しない場合
        """
        if not Path(self.persist_directory).exists():
            raise FileNotFoundError(
                f"ベクトルストアが見つかりません: {self.persist_directory}\n"
                "先に create_vectorstore() でベクトルストアを作成してください。"
            )

        print(f"📂 ベクトルストアを読み込み中: {self.persist_directory}")

        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
        )

        print(f"✅ ベクトルストアを読み込みました")
        return self.vectorstore

    def search(
        self,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Document]:
        """
        クエリに関連するドキュメントを検索する

        Args:
            query: 検索クエリ
            k: 取得するドキュメント数
            score_threshold: スコアの閾値（設定した場合、これ以上のスコアのみ返す）

        Returns:
            関連するドキュメントのリスト
        """
        if self.vectorstore is None:
            raise ValueError(
                "ベクトルストアが初期化されていません。"
                "先に load_vectorstore() または create_vectorstore() を実行してください。"
            )

        print(f"🔍 検索中: {query[:50]}...")

        if score_threshold is not None:
            # スコア付きで検索
            docs_with_scores = self.vectorstore.similarity_search_with_score(
                query, k=k * 2  # 閾値でフィルタするため多めに取得
            )
            docs = [
                doc for doc, score in docs_with_scores
                if score >= score_threshold
            ][:k]
        else:
            docs = self.vectorstore.similarity_search(query, k=k)

        print(f"✅ {len(docs)} 件のドキュメントを取得しました")
        return docs

    def get_retriever(self, k: int = 5):
        """
        Retriever オブジェクトを取得する（LangChain用）

        Args:
            k: 取得するドキュメント数

        Returns:
            Retrieverオブジェクト
        """
        if self.vectorstore is None:
            raise ValueError(
                "ベクトルストアが初期化されていません。"
            )

        return self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )

    def delete_vectorstore(self):
        """ベクトルストアを削除する"""
        import shutil

        if Path(self.persist_directory).exists():
            shutil.rmtree(self.persist_directory)
            print(f"🗑️  ベクトルストアを削除しました: {self.persist_directory}")
        else:
            print(f"⚠️  ベクトルストアが存在しません: {self.persist_directory}")

    def get_or_create_vectorstore(
        self, documents: Optional[List[Document]] = None
    ) -> Chroma:
        """
        既存のベクトルストアを読み込むか、なければ新規作成する

        Args:
            documents: 新規作成時に使用するドキュメント

        Returns:
            ベクトルストア
        """
        try:
            return self.load_vectorstore()
        except FileNotFoundError:
            if documents is None:
                raise ValueError(
                    "ベクトルストアが存在せず、ドキュメントも提供されていません"
                )
            return self.create_vectorstore(documents)


def setup_vectorstore(
    texts_dir: str = "data/fukuzawa_texts",
    persist_directory: str = "chroma_db",
    force_recreate: bool = False,
) -> FukuzawaVectorStore:
    """
    ベクトルストアをセットアップする便利関数

    Args:
        texts_dir: テキストディレクトリ
        persist_directory: ベクトルストアの保存先
        force_recreate: 既存のベクトルストアを削除して再作成するか

    Returns:
        セットアップされたFukuzawaVectorStore
    """
    from .loader import FukuzawaTextLoader

    vectorstore_manager = FukuzawaVectorStore(persist_directory=persist_directory)

    if force_recreate:
        vectorstore_manager.delete_vectorstore()

    # ベクトルストアが存在しない場合のみ作成
    if not Path(persist_directory).exists():
        loader = FukuzawaTextLoader(texts_dir=texts_dir)
        documents = loader.load_and_split()
        vectorstore_manager.create_vectorstore(documents)
    else:
        vectorstore_manager.load_vectorstore()

    return vectorstore_manager


if __name__ == "__main__":
    # テスト用
    from loader import FukuzawaTextLoader, create_sample_texts

    # サンプルテキストを作成
    create_sample_texts()

    # ローダーでテキストを読み込み
    loader = FukuzawaTextLoader()
    documents = loader.load_and_split()

    # ベクトルストアを作成
    vectorstore_manager = FukuzawaVectorStore()
    vectorstore_manager.delete_vectorstore()  # テスト用に既存のものを削除
    vectorstore_manager.create_vectorstore(documents)

    # 検索テスト
    print("\n🔍 検索テスト")
    results = vectorstore_manager.search("学問の重要性", k=3)

    for i, doc in enumerate(results, 1):
        print(f"\n--- 検索結果 {i} ---")
        print(doc.page_content[:200] + "...")
