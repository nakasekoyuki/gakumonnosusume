"""コマンドラインインターフェース"""

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from .loader import FukuzawaTextLoader, create_sample_texts
from .vectorstore import FukuzawaVectorStore, setup_vectorstore
from .generator import FukuzawaTextGenerator

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """福沢諭吉風テキスト生成システム"""
    pass


@cli.command()
@click.option(
    "--texts-dir",
    default="data/fukuzawa_texts",
    help="福沢諭吉のテキストが格納されているディレクトリ",
)
@click.option(
    "--persist-dir",
    default="chroma_db",
    help="ベクトルストアの保存先ディレクトリ",
)
@click.option(
    "--force",
    is_flag=True,
    help="既存のベクトルストアを削除して再作成する",
)
def setup(texts_dir: str, persist_dir: str, force: bool):
    """ベクトルストアをセットアップする"""
    console.print("\n[bold blue]📚 福沢諭吉テキストジェネレーター セットアップ[/bold blue]\n")

    # テキストディレクトリの確認
    texts_path = Path(texts_dir)
    if not texts_path.exists():
        console.print(
            f"[yellow]⚠️  テキストディレクトリが見つかりません: {texts_dir}[/yellow]"
        )
        if click.confirm("サンプルテキストを作成しますか?", default=True):
            create_sample_texts(texts_dir)
            console.print("[green]✅ サンプルテキストを作成しました[/green]")
        else:
            console.print("[red]❌ セットアップを中止しました[/red]")
            return

    # ベクトルストアのセットアップ
    try:
        vectorstore_manager = setup_vectorstore(
            texts_dir=texts_dir,
            persist_directory=persist_dir,
            force_recreate=force,
        )
        console.print(f"\n[green]✅ セットアップが完了しました![/green]")
        console.print(f"ベクトルストア: {persist_dir}")

    except Exception as e:
        console.print(f"[red]❌ エラーが発生しました: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("theme")
@click.option(
    "--persist-dir",
    default="chroma_db",
    help="ベクトルストアのディレクトリ",
)
@click.option(
    "--retrieval-k",
    default=5,
    help="RAGで取得する関連文章の数",
)
@click.option(
    "--show-context",
    is_flag=True,
    help="参考文章を表示する",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="出力ファイルパス",
)
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic"]),
    help="LLMプロバイダー",
)
def generate(
    theme: str,
    persist_dir: str,
    retrieval_k: int,
    show_context: bool,
    output: str,
    provider: str,
):
    """テーマに基づいて福沢諭吉風の文章を生成する"""
    load_dotenv()

    console.print("\n[bold blue]✍️  福沢諭吉風文章生成[/bold blue]\n")

    try:
        # ベクトルストアを読み込む
        vectorstore_manager = FukuzawaVectorStore(persist_directory=persist_dir)
        vectorstore_manager.load_vectorstore()

        # ジェネレーターを作成
        llm_provider = provider or os.getenv("LLM_PROVIDER", "anthropic")
        generator = FukuzawaTextGenerator(
            vectorstore=vectorstore_manager,
            llm_provider=llm_provider,
        )

        # 文章を生成
        article = generator.generate(
            theme=theme,
            retrieval_k=retrieval_k,
            show_context=show_context,
        )

        # 結果を表示
        console.print("\n")
        console.print(Panel(
            Markdown(article),
            title=f"[bold]テーマ: {theme}[/bold]",
            border_style="blue",
        ))

        # ファイルに保存
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# {theme}\n\n{article}\n")
            console.print(f"\n[green]✅ ファイルに保存しました: {output}[/green]")

    except FileNotFoundError as e:
        console.print(f"[red]❌ {e}[/red]")
        console.print("\n[yellow]まず 'gakumon setup' を実行してください[/yellow]")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ エラーが発生しました: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    "--persist-dir",
    default="chroma_db",
    help="ベクトルストアのディレクトリ",
)
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic"]),
    help="LLMプロバイダー",
)
def interactive(persist_dir: str, provider: str):
    """対話的モードで文章を生成する"""
    load_dotenv()

    console.print("\n[bold blue]🎓 福沢諭吉風文章生成 - 対話モード[/bold blue]\n")
    console.print("[dim]終了するには 'exit' または 'quit' を入力してください[/dim]\n")

    try:
        # ベクトルストアを読み込む
        vectorstore_manager = FukuzawaVectorStore(persist_directory=persist_dir)
        vectorstore_manager.load_vectorstore()

        # ジェネレーターを作成
        llm_provider = provider or os.getenv("LLM_PROVIDER", "anthropic")
        generator = FukuzawaTextGenerator(
            vectorstore=vectorstore_manager,
            llm_provider=llm_provider,
        )

        console.print("[green]✅ システムの準備が整いました[/green]\n")

        # 対話ループ
        while True:
            theme = Prompt.ask("\n[bold cyan]テーマを入力してください[/bold cyan]")

            if theme.lower() in ["exit", "quit", "q"]:
                console.print("\n[yellow]👋 終了します[/yellow]")
                break

            if not theme.strip():
                console.print("[yellow]⚠️  テーマを入力してください[/yellow]")
                continue

            try:
                # 文章を生成
                article = generator.generate(theme=theme)

                # 結果を表示
                console.print("\n")
                console.print(Panel(
                    Markdown(article),
                    title=f"[bold]テーマ: {theme}[/bold]",
                    border_style="blue",
                ))

                # 保存するか確認
                if click.confirm("\nファイルに保存しますか?", default=False):
                    filename = Prompt.ask(
                        "ファイル名",
                        default=f"output/{theme[:20]}.md"
                    )
                    output_path = Path(filename)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(f"# {theme}\n\n{article}\n")
                    console.print(f"[green]✅ 保存しました: {filename}[/green]")

            except Exception as e:
                console.print(f"[red]❌ エラー: {e}[/red]")

    except FileNotFoundError as e:
        console.print(f"[red]❌ {e}[/red]")
        console.print("\n[yellow]まず 'gakumon setup' を実行してください[/yellow]")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ エラーが発生しました: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option(
    "--persist-dir",
    default="chroma_db",
    help="ベクトルストアのディレクトリ",
)
@click.option(
    "--k",
    default=5,
    help="取得するドキュメント数",
)
def search(query: str, persist_dir: str, k: int):
    """ベクトルストアから関連文章を検索する"""
    console.print(f"\n[bold blue]🔍 検索: {query}[/bold blue]\n")

    try:
        # ベクトルストアを読み込む
        vectorstore_manager = FukuzawaVectorStore(persist_directory=persist_dir)
        vectorstore_manager.load_vectorstore()

        # 検索
        results = vectorstore_manager.search(query, k=k)

        # 結果を表示
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "不明")
            console.print(Panel(
                doc.page_content,
                title=f"[bold]結果 {i}[/bold] - {source}",
                border_style="green",
            ))
            console.print()

    except FileNotFoundError as e:
        console.print(f"[red]❌ {e}[/red]")
        console.print("\n[yellow]まず 'gakumon setup' を実行してください[/yellow]")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ エラーが発生しました: {e}[/red]")
        sys.exit(1)


def main():
    """メイン関数"""
    cli()


if __name__ == "__main__":
    main()
