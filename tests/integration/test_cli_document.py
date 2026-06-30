from pathlib import Path

from agentic_book.interfaces.cli.main import main


def test_cli_get_document_prints_body(tmp_path: Path, capsys) -> None:
    assert main(["--content-root", "content", "--data-dir", str(tmp_path), "ingest"]) == 0

    assert main(["--data-dir", str(tmp_path), "get-document", "concept.mcp"]) == 0

    output = capsys.readouterr().out
    assert "# Model Context Protocol" in output
    assert "Streamable HTTP" in output
