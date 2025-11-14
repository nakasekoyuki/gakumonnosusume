"""福沢諭吉のテキストを読み込み、チャンク化するモジュール"""

import os
from pathlib import Path
from typing import List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.schema import Document


class FukuzawaTextLoader:
    """福沢諭吉のテキストファイルを読み込み、処理するクラス"""

    def __init__(
        self,
        texts_dir: str = "data/fukuzawa_texts",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Args:
            texts_dir: 福沢諭吉のテキストが格納されているディレクトリ
            chunk_size: 各チャンクのサイズ（文字数）
            chunk_overlap: チャンク間のオーバーラップ（文字数）
        """
        self.texts_dir = Path(texts_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 日本語テキストに適したテキスト分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "、", " ", ""],
            length_function=len,
        )

    def load_texts(self, file_pattern: str = "**/*.txt") -> List[Document]:
        """
        指定されたディレクトリから福沢諭吉のテキストファイルを読み込む

        Args:
            file_pattern: 読み込むファイルのパターン（globパターン）

        Returns:
            読み込んだドキュメントのリスト
        """
        if not self.texts_dir.exists():
            raise FileNotFoundError(
                f"テキストディレクトリが見つかりません: {self.texts_dir}"
            )

        print(f"📚 テキストを読み込み中: {self.texts_dir}")

        # ディレクトリ内のテキストファイルを読み込む
        loader = DirectoryLoader(
            str(self.texts_dir),
            glob=file_pattern,
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=True,
        )

        documents = loader.load()
        print(f"✅ {len(documents)} 件のファイルを読み込みました")

        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        ドキュメントをチャンクに分割する

        Args:
            documents: 分割するドキュメントのリスト

        Returns:
            分割されたドキュメントのリスト
        """
        print(f"✂️  テキストをチャンクに分割中...")

        chunks = self.text_splitter.split_documents(documents)

        print(f"✅ {len(chunks)} 個のチャンクに分割しました")
        return chunks

    def load_and_split(self, file_pattern: str = "**/*.txt") -> List[Document]:
        """
        テキストの読み込みと分割を一度に行う便利メソッド

        Args:
            file_pattern: 読み込むファイルのパターン

        Returns:
            分割されたドキュメントのリスト
        """
        documents = self.load_texts(file_pattern)
        chunks = self.split_documents(documents)
        return chunks

    def get_sample_text(self, num_chunks: int = 3) -> List[str]:
        """
        サンプルテキストを取得する（デバッグ用）

        Args:
            num_chunks: 取得するチャンク数

        Returns:
            サンプルテキストのリスト
        """
        chunks = self.load_and_split()
        return [chunk.page_content for chunk in chunks[:num_chunks]]


def create_sample_texts(output_dir: str = "data/fukuzawa_texts"):
    """
    サンプルの福沢諭吉風テキストを作成する（デモ用）

    Args:
        output_dir: 出力ディレクトリ
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 学問のすゝめ からの抜粋（簡略版）
    gakumon_sample = """学問のすゝめ

天は人の上に人を造らず人の下に人を造らずと言えり。されば天より人を生ずるには、万人は万人みな同じ位にして、生まれながら貴賎上下の差別なく、万物の霊たる身と心との働きをもって天地の間にあるよろずの物を資り、もって衣食住の用を達し、自由自在、互いに人の妨げをなさずしておのおの安楽にこの世を渡らしめ給うの趣意なり。

されども今、広くこの人間世界を見渡すに、かしこき人あり、おろかなる人あり、貧しきもあり、富めるもあり、貴人もあり、下人もありて、その有様雲と泥との相違あるに似たるはなんぞや。

その次第はなはだ明らかなり。実語教に、人学ばざれば智なし、智なき者は愚人なりとあり。されば賢人と愚人との別は学ぶと学ばざるとによりてできるものなり。

人は生まれながらにして貴賎貧富の別なし。ただ学問を勤めて物事をよく知る者は貴人となり富人となり、無学なる者は貧人となり下人となるなり。
"""

    civilization_sample = """文明論之概略

文明とは人の精神発達の趣旨をいうなり。されば文明開化の有様は、人の智徳を進めて明らかにし、事理を議論して明弁に、人の心身を労働に慣らして敏活に働かしめ、なおまた人間の交わりを篤くし、徳義心を起こして、衣食住より以上に高尚なる楽しみを知らしむるをいうなり。

西洋諸国の有様を見るに、学問は盛んに、技術は精しく、法律は明らかに、諸般の事物みな整頓して、文明の名に恥じざるものなり。

これに反して我が日本国の有様はいかん。学問に心を用いる者は少なく、技術もまた進まず、法律は整わず、商売は活発ならず、人心は陋習に囚われて、外国との交際もまた円滑ならず。これすなわち未だ文明の域に達せざる国なり。

されども我が日本も今より大いに学問を勧め、智識を進め、旧来の陋習を破り、外国の良法を採用し、人々の精神を一新すれば、文明開化の域に進むこと決して難きにあらざるなり。
"""

    with open(output_path / "gakumon_no_susume.txt", "w", encoding="utf-8") as f:
        f.write(gakumon_sample)

    with open(output_path / "bunmeiron_no_gairyaku.txt", "w", encoding="utf-8") as f:
        f.write(civilization_sample)

    print(f"✅ サンプルテキストを作成しました: {output_dir}")


if __name__ == "__main__":
    # サンプルテキストを作成
    create_sample_texts()

    # ローダーをテスト
    loader = FukuzawaTextLoader()
    chunks = loader.load_and_split()

    print("\n📝 サンプルチャンク:")
    for i, chunk in enumerate(chunks[:2], 1):
        print(f"\n--- チャンク {i} ---")
        print(chunk.page_content[:200] + "...")
