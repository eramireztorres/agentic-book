import json

from agentic_book.interfaces.cli.main import main


def test_cli_capabilities_prints_machine_readable_contract(capsys) -> None:
    assert main(["capabilities", "--json"]) == 0

    capabilities = json.loads(capsys.readouterr().out)
    assert capabilities["name"] == "Agentic Book"
    assert "hybrid" in capabilities["retrieval_modes"]
    assert capabilities["vector_store"] == "memory"
    assert "lancedb" in capabilities["supported_vector_stores"]
    assert capabilities["mcp"]["search_abstention"]["parameter"] == "min_score"
    assert {profile["name"] for profile in capabilities["retrieval_eval_profiles"]} == {
        "baseline",
        "guarded",
        "custom",
    }
    assert {row["row"] for row in capabilities["retrieval_eval_matrix_rows"]} == {"baseline", "vector", "guarded"}
    assert "vector_store" in capabilities["cloud_ready_boundaries"]
