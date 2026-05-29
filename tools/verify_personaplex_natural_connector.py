from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_connector():
    path = ROOT / "tools" / "voice" / "personaplex_natural_connector.py"
    spec = importlib.util.spec_from_file_location("personaplex_natural_connector", path)
    if not spec or not spec.loader:
        raise RuntimeError("personaplex_connector_load_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PersonaPlexNaturalConnector()


def result(ok: bool, detail=None) -> dict:
    return {"ok": bool(ok), "detail": detail}


def main() -> dict:
    connector = _load_connector()
    readiness = connector.readiness()
    policy = readiness.get("policy", {})
    repo = readiness.get("repo", {})
    deps = readiness.get("dependencies", {})
    runtime = readiness.get("runtime", {})
    torch_cuda = readiness.get("torch_cuda", {})

    checks = {
        "official_repo_cloned": result(repo.get("exists") and repo.get("readme_exists"), repo),
        "moshi_source_present": result(repo.get("moshi_source_exists") is True, repo),
        "natural_voice_set_registered": result(
            readiness.get("natural_voices", {}).get("female") == ["NATF0", "NATF1", "NATF2", "NATF3"]
            and readiness.get("natural_voices", {}).get("male") == ["NATM0", "NATM1", "NATM2", "NATM3"],
            readiness.get("natural_voices"),
        ),
        "tuka_governance_policy_active": result(
            policy.get("requires_model_license_acceptance") is True
            and policy.get("requires_hf_token") is True
            and policy.get("no_live_runtime_without_admin_gate") is True
            and policy.get("copy_provider_code_or_weights") is False,
            policy,
        ),
        "dependency_status_recorded": result(
            all(name in deps for name in ["torch", "torchaudio", "transformers", "accelerate", "huggingface_hub", "moshi"]),
            deps,
        ),
        "torch_cuda_available": result(
            torch_cuda.get("checked") is True and torch_cuda.get("cuda_available") is True,
            torch_cuda,
        ),
        "readiness_is_fail_closed": result(
            runtime.get("live_ready") is False if runtime.get("blockers") else runtime.get("live_ready") is True,
            runtime,
        ),
        "profile_file_written": result(
            (ROOT / "data" / "personaplex_natural_profile.json").exists(),
            "data/personaplex_natural_profile.json",
        ),
    }
    passed = sum(1 for item in checks.values() if item["ok"])
    report = {
        "ok": passed == len(checks),
        "phase": "personaplex_natural_connector",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "readiness": readiness,
    }
    out = ROOT / "data" / "personaplex_natural_connector_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report["report"] = str(out)
    return report


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, ensure_ascii=False))
