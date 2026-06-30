import json
from pathlib import Path

from agentic_book.infrastructure.evaluation.json_dataset import load_retrieval_eval_cases
from agentic_book.interfaces.cli.main import main


def test_ground_truth_dataset_loads() -> None:
    cases = load_retrieval_eval_cases(Path("evals/retrieval/ground_truth.json"))

    assert len(cases) >= 5
    assert any(not case.answerable for case in cases)


def test_cli_eval_retrieval_passes_baseline(tmp_path: Path, capsys) -> None:
    data_dir = tmp_path / "data"
    assert main(["--content-root", "content", "--data-dir", str(data_dir), "ingest"]) == 0

    report_path = tmp_path / "reports" / "latest.json"
    assert main(["--data-dir", str(data_dir), "eval-retrieval", "--write-report", str(report_path)]) == 0

    output = capsys.readouterr().out
    assert "profile=baseline" in output
    assert "retrieval_mode=lexical" in output
    assert "cases=" in output
    assert "hit_rate=" in output
    assert "mrr=" in output
    assert "abstention_rate=" in output
    assert "FAIL:" not in output
    report = json.loads(report_path.read_text())
    assert report["profile"] == "baseline"
    assert report["retrieval_mode"] == "lexical"
    assert report["cases"] >= 5


def test_cli_eval_retrieval_guarded_profile_requires_unanswerable_success(tmp_path: Path, capsys) -> None:
    data_dir = tmp_path / "data"
    assert main(["--content-root", "content", "--data-dir", str(data_dir), "ingest"]) == 0

    assert main(["--data-dir", str(data_dir), "eval-retrieval", "--profile", "guarded"]) == 0

    output = capsys.readouterr().out
    assert "profile=guarded" in output
    assert "retrieval_mode=hybrid" in output
    assert "unanswerable_success_rate=1.000" in output
    assert "abstained=true" in output
    assert "FAIL:" not in output


def test_cli_eval_matrix_writes_aggregate_report(tmp_path: Path, capsys) -> None:
    data_dir = tmp_path / "data"
    assert main(["--content-root", "content", "--data-dir", str(data_dir), "ingest"]) == 0

    report_path = tmp_path / "reports" / "matrix.json"
    assert main(["--data-dir", str(data_dir), "eval-matrix", "--write-report", str(report_path)]) == 0

    output = capsys.readouterr().out
    assert "PASS: row=baseline" in output
    assert "PASS: row=vector" in output
    assert "PASS: row=guarded" in output
    assert f"report={report_path}" in output
    report = json.loads(report_path.read_text())
    assert report["passed"] is True
    assert [row["row"] for row in report["rows"]] == ["baseline", "vector", "guarded"]
    assert report["rows"][0]["profile"] == "baseline"
    assert report["rows"][1]["retrieval_mode"] == "vector"
    assert report["rows"][2]["profile"] == "guarded"
