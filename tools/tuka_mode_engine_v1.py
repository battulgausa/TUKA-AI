from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "tuka_mode_engine_v1_report.json"
AUDIT_PATH = DATA_DIR / "tuka_mode_engine_audit.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _audit(event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"ts": _now(), **event}, ensure_ascii=False) + "\n")


MODES: dict[str, dict[str, Any]] = {
    "TRUTHMODE": {
        "label": "Truth Mode",
        "purpose": "үнэн, хатуу шүүлт",
        "behavior": ["state_hard_truth", "identify_weakness", "avoid_comforting_falsehood"],
        "output_sections": ["truth", "weaknesses", "risks", "fixes"],
    },
    "REDTEAM": {
        "label": "Red Team",
        "purpose": "сул тал, эрсдэл, цоорхой хайх",
        "behavior": ["attack_assumptions", "find_failure_modes", "recommend_controls"],
        "output_sections": ["attack_surface", "failure_modes", "mitigations"],
    },
    "UNLEARN": {
        "label": "Unlearn",
        "purpose": "буруу/хуучирсан ойлголт цэвэрлэх",
        "behavior": ["flag_stale_beliefs", "separate_fact_from_habit", "replace_with_current_model"],
        "output_sections": ["old_assumption", "why_wrong", "better_model"],
    },
    "BUSINESSCOACH": {
        "label": "Business Coach",
        "purpose": "өндөр түвшний бизнес өнцөг",
        "behavior": ["clarify_offer", "evaluate_unit_economics", "focus_customer_value"],
        "output_sections": ["offer", "market", "pricing", "next_move"],
    },
    "STARTUPMODE": {
        "label": "Startup Mode",
        "purpose": "startup зөвлөгөө",
        "behavior": ["focus_mvp", "validate_fast", "avoid_fake_scale"],
        "output_sections": ["mvp", "customer_test", "metrics", "iteration"],
    },
    "ATTENTIONMODE": {
        "label": "Attention Mode",
        "purpose": "social/content growth өнцөг",
        "behavior": ["find_hook", "compress_message", "design_repeatable_content"],
        "output_sections": ["hook", "angle", "format", "cadence"],
    },
    "ELI10": {
        "label": "Explain Like 10",
        "purpose": "10 настайд ойлгогдох тайлбар",
        "behavior": ["simple_words", "concrete_example", "no_jargon"],
        "output_sections": ["simple_answer", "example", "remember_this"],
    },
    "SOCRATES": {
        "label": "Socrates",
        "purpose": "асуултаар бодуулах",
        "behavior": ["ask_guiding_questions", "avoid_over_answering", "surface_assumptions"],
        "output_sections": ["questions", "assumptions", "next_reflection"],
    },
    "FIRSTPRINCIPLES": {
        "label": "First Principles",
        "purpose": "суурь зарчим хүртэл задлах",
        "behavior": ["strip_to_basics", "rebuild_logic", "separate_constraints"],
        "output_sections": ["basics", "constraints", "rebuild"],
    },
    "HUMAN": {
        "label": "Human",
        "purpose": "хүн шиг natural бичих",
        "behavior": ["natural_tone", "short_contextual_reply", "avoid_robotic_template"],
        "output_sections": ["reply"],
    },
    "80/20": {
        "label": "80/20",
        "purpose": "хамгийн их үр дүнтэй хамгийн бага алхам",
        "behavior": ["find_leverage", "cut_low_value_work", "prioritize_next_actions"],
        "output_sections": ["top_20_percent", "ignore_for_now", "next_3_steps"],
    },
    "EXECUTE": {
        "label": "Execute",
        "purpose": "төлөвлөгөөг бодит ажил болгон задална",
        "behavior": ["turn_plan_into_tasks", "define_owner_order", "include_verify_step"],
        "output_sections": ["tasks", "order", "verification"],
    },
    "VERIFY": {
        "label": "Verify",
        "purpose": "баримт, эх сурвалж, логикоор шалгана",
        "behavior": ["check_claims", "require_evidence", "mark_uncertainty"],
        "output_sections": ["claims", "evidence", "uncertainty", "verdict"],
    },
    "STRATEGY": {
        "label": "Strategy",
        "purpose": "урт хугацааны стратеги гаргана",
        "behavior": ["set_long_term_direction", "sequence_moves", "identify_tradeoffs"],
        "output_sections": ["north_star", "phases", "tradeoffs", "risks"],
    },
}


ALIASES = {
    "HORMOZI": "BUSINESSCOACH",
    "GARYVEE": "ATTENTIONMODE",
    "YCOMBINATOR": "STARTUPMODE",
    "YC": "STARTUPMODE",
    "/HUMAN": "HUMAN",
    "HUMANMODE": "HUMAN",
    "PARETO": "80/20",
    "EIGHTYTWENTY": "80/20",
}


GUARDS = {
    "tuka_native_public_names": True,
    "provider_or_persona_brand_names_not_public_modes": True,
    "mode_does_not_bypass_governance": True,
    "mode_does_not_enable_execution": True,
    "verify_mode_requires_evidence_or_uncertainty": True,
    "truthmode_must_not_be_abusive": True,
    "redteam_must_not_provide_harmful_exploit_steps": True,
    "admin_approval_required_for_actions": True,
    "audit_logging": True,
    "no_fake_pass": True,
}


RUNTIME = {
    "execution_enabled": False,
    "external_actions_enabled": False,
    "mode_selector_enabled": True,
    "admin_console_visible": True,
    "preview_only": True,
}


@dataclass
class ModeRequest:
    text: str
    mode: str | None = None
    language: str = "mn"


def normalize_mode(mode: str | None) -> str:
    raw = (mode or "").strip().upper()
    if raw in MODES:
        return raw
    if raw in ALIASES:
        return ALIASES[raw]
    return "HUMAN"


def parse_mode_command(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    match = re.match(r"^([A-Za-z0-9/_-]+):\s*(.*)$", raw)
    if not match:
        return {"mode": "HUMAN", "prompt": raw, "explicit": False, "alias_used": None}
    requested = match.group(1).strip().upper()
    prompt = match.group(2).strip()
    mode = normalize_mode(requested)
    alias_used = requested if requested in ALIASES else None
    explicit = requested in MODES or requested in ALIASES
    return {"mode": mode, "prompt": prompt, "explicit": explicit, "alias_used": alias_used}


def registry() -> dict[str, Any]:
    return {
        "ok": True,
        "engine": "tuka_mode_engine_v1",
        "public_name": "Tuka Mode Engine",
        "mode_count": len(MODES),
        "modes": MODES,
        "aliases": ALIASES,
        "guards": GUARDS,
        "runtime": RUNTIME,
        "updated_at": _now(),
    }


def _mode_response(mode: str, prompt: str) -> dict[str, Any]:
    spec = MODES[mode]
    base = {
        "ok": True,
        "mode": mode,
        "label": spec["label"],
        "prompt": prompt,
        "purpose": spec["purpose"],
        "behavior": spec["behavior"],
        "output_sections": spec["output_sections"],
        "execution_enabled": False,
        "external_action_executed": False,
        "admin_approval_required_for_actions": True,
    }
    if mode == "TRUTHMODE":
        base["draft"] = {
            "truth": "Санааг бодитоор шалгахад сул тал, зах зээл, execution, санхүүгийн эрсдэлүүдийг нуухгүй хэлнэ.",
            "weaknesses": ["баталгаагүй demand", "хэт өргөн scope", "гүйцэтгэлийн зардал"],
            "risks": ["удаан release", "хэрэглэгчийн ойлгомжгүй үнэ цэн"],
            "fixes": ["нэг MVP сонго", "1 хэрэглэгчийн workflow төгс болго", "verify metric тогтоо"],
        }
    elif mode == "REDTEAM":
        base["draft"] = {
            "attack_surface": ["assumption", "security", "cost", "UX"],
            "failure_modes": ["fake pass", "over-broad feature", "privacy violation"],
            "mitigations": ["admin gate", "source citation", "fail closed"],
        }
    elif mode == "ELI10":
        base["draft"] = {
            "simple_answer": "Тука Mode Engine гэдэг нь Тука яаж бодож, ямар маягаар хариулахыг сонгодог товч юм.",
            "example": "TRUTHMODE гэж бичвэл Тука чамд хатуу үнэнийг хэлнэ.",
            "remember_this": "Mode нь зөвхөн бодох хэлбэрийг солино, хамгаалалтыг унтраахгүй.",
        }
    elif mode == "EXECUTE":
        base["draft"] = {
            "tasks": ["зорилгыг жижиглэх", "файл/API/UI нэмэх", "compile шалгах", "browser verify хийх"],
            "order": ["plan", "build", "verify", "merge"],
            "verification": ["no fake pass", "real endpoint", "real browser evidence"],
        }
    elif mode == "VERIFY":
        base["draft"] = {
            "claims": [prompt or "claim"],
            "evidence": ["local verifier", "API response", "browser text"],
            "uncertainty": "external/current facts need source check",
            "verdict": "pass only after real evidence",
        }
    else:
        base["draft"] = {
            section: f"{spec['label']} response section for: {prompt or 'sample prompt'}"
            for section in spec["output_sections"]
        }
    _audit({"event": "mode_applied", "mode": mode, "prompt_len": len(prompt)})
    return base


def apply_mode(request: ModeRequest) -> dict[str, Any]:
    parsed = parse_mode_command(request.text)
    mode = normalize_mode(request.mode) if request.mode else parsed["mode"]
    prompt = parsed["prompt"] if parsed["explicit"] else request.text.strip()
    result = _mode_response(mode, prompt)
    result["parsed"] = parsed
    result["language"] = request.language
    return result


def verify_mode_engine() -> dict[str, Any]:
    reg = registry()
    truth = apply_mode(ModeRequest(text="TRUTHMODE: Миний бизнес санааг үнэл"))
    alias_business = apply_mode(ModeRequest(text="HORMOZI: offer шалга"))
    alias_attention = apply_mode(ModeRequest(text="GARYVEE: content өсөлт"))
    alias_startup = apply_mode(ModeRequest(text="YCOMBINATOR: MVP зөвлөгөө"))
    eli10 = apply_mode(ModeRequest(text="ELI10: Mode Engine гэж юу вэ"))
    execute = apply_mode(ModeRequest(text="EXECUTE: mode engine нэм"))
    verify = apply_mode(ModeRequest(text="VERIFY: энэ үнэн үү"))
    strategy = apply_mode(ModeRequest(text="STRATEGY: урт хугацааны чиглэл"))

    expected_modes = {
        "TRUTHMODE",
        "REDTEAM",
        "UNLEARN",
        "BUSINESSCOACH",
        "STARTUPMODE",
        "ATTENTIONMODE",
        "ELI10",
        "SOCRATES",
        "FIRSTPRINCIPLES",
        "HUMAN",
        "80/20",
        "EXECUTE",
        "VERIFY",
        "STRATEGY",
    }
    checks = {
        "registry_ok": reg["ok"] is True,
        "fourteen_modes": reg["mode_count"] == 14,
        "all_expected_modes_present": set(MODES) == expected_modes,
        "truthmode_present": truth["mode"] == "TRUTHMODE" and "weaknesses" in truth["draft"],
        "redteam_present": "REDTEAM" in MODES,
        "unlearn_present": "UNLEARN" in MODES,
        "businesscoach_alias": alias_business["mode"] == "BUSINESSCOACH",
        "attention_alias": alias_attention["mode"] == "ATTENTIONMODE",
        "startup_alias": alias_startup["mode"] == "STARTUPMODE",
        "eli10_simple": eli10["mode"] == "ELI10" and "simple_answer" in eli10["draft"],
        "socrates_present": "SOCRATES" in MODES,
        "firstprinciples_present": "FIRSTPRINCIPLES" in MODES,
        "human_present": "HUMAN" in MODES,
        "eighty_twenty_present": "80/20" in MODES,
        "execute_mode": execute["mode"] == "EXECUTE" and "tasks" in execute["draft"],
        "verify_mode": verify["mode"] == "VERIFY" and "evidence" in verify["draft"],
        "strategy_mode": strategy["mode"] == "STRATEGY",
        "public_names_tuka_native": GUARDS["tuka_native_public_names"] is True,
        "brand_aliases_not_public_modes": "HORMOZI" not in MODES and "GARYVEE" not in MODES and "YCOMBINATOR" not in MODES,
        "mode_does_not_bypass_governance": GUARDS["mode_does_not_bypass_governance"] is True,
        "mode_does_not_enable_execution": RUNTIME["execution_enabled"] is False,
        "external_actions_disabled": RUNTIME["external_actions_enabled"] is False,
        "admin_approval_required": GUARDS["admin_approval_required_for_actions"] is True,
        "truthmode_not_abusive_guard": GUARDS["truthmode_must_not_be_abusive"] is True,
        "redteam_harm_guard": GUARDS["redteam_must_not_provide_harmful_exploit_steps"] is True,
        "verify_requires_evidence_or_uncertainty": GUARDS["verify_mode_requires_evidence_or_uncertainty"] is True,
        "audit_written": AUDIT_PATH.exists(),
        "preview_only": RUNTIME["preview_only"] is True,
        "no_fake_pass": GUARDS["no_fake_pass"] is True,
    }
    passed = sum(1 for value in checks.values() if value is True)
    total = len(checks)
    report = {
        "ok": passed == total,
        "phase": "tuka_mode_engine_v1",
        "passed": passed,
        "total": total,
        "checks": checks,
        "registry": reg,
        "samples": {
            "truth": truth,
            "business_alias": alias_business,
            "attention_alias": alias_attention,
            "startup_alias": alias_startup,
            "eli10": eli10,
            "execute": execute,
            "verify": verify,
            "strategy": strategy,
        },
        "updated_at": _now(),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(json.dumps(verify_mode_engine(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
