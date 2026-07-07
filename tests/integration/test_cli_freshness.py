from pathlib import Path

from agentic_book.interfaces.cli.main import main


def test_cli_validate_strict_freshness_accepts_content_fixtures(capsys) -> None:
    assert main(["--content-root", "content", "validate-content", "--strict-freshness"]) == 0

    output = capsys.readouterr().out
    assert "checked=35" in output
    assert "ok=true" in output


def test_cli_stale_report_and_update_proposal(tmp_path: Path, capsys) -> None:
    data_dir = tmp_path / "data"
    proposals_dir = tmp_path / "proposals"
    assert main(["--content-root", "content", "--data-dir", str(data_dir), "ingest"]) == 0

    assert main(["--data-dir", str(data_dir), "stale-report"]) == 0
    stale_output = capsys.readouterr().out
    assert "checked=35" in stale_output
    assert "stale=0" in stale_output

    assert (
        main(
            [
                "--data-dir",
                str(data_dir),
                "propose-doc-update",
                "concept.mcp",
                "--reason",
                "Possible upstream protocol change",
                "--source-hint",
                "https://modelcontextprotocol.io/docs",
                "--proposals-dir",
                str(proposals_dir),
            ]
        )
        == 0
    )
    proposal_output = capsys.readouterr().out
    assert "proposal=" in proposal_output
    assert "status=needs-human-review" in proposal_output
    assert list((proposals_dir / "documentation-updates").glob("*.md"))
    assert list((proposals_dir / "documentation-updates").glob("*.json"))
