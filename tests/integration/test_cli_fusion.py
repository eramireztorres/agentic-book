from pathlib import Path

from agentic_book.interfaces.cli.main import main


def test_cli_fusion_search_returns_mcp_result(tmp_path: Path, capsys) -> None:
    assert main(["--content-root", "content", "--data-dir", str(tmp_path), "ingest"]) == 0

    assert (
        main(
            [
                "--data-dir",
                str(tmp_path),
                "fusion-search",
                "--query",
                "Streamable HTTP",
                "--query",
                "MCP resources",
                "--final-top-k",
                "3",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "concept.mcp" in output
    assert "results=" in output
