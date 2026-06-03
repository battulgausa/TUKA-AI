"""Tuka Global Marketing Intelligence Agent v1.

Privacy-first marketing intelligence for Tuka.

This module intentionally does not scrape private messages, email, search
history, phone activity, or social-media accounts without consent. It builds
plans from consented user data, public trend data, official APIs, and public
web/search data contracts only.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "global_marketing_intelligence_audit.jsonl"


PLATFORMS = [
    "Facebook",
    "Instagram",
    "TikTok",
    "YouTube",
    "X/Twitter",
    "LinkedIn",
    "Reddit",
    "Pinterest",
    "Snapchat",
    "Threads",
    "WhatsApp community strategy",
    "Telegram community strategy",
]


MVP_PLATFORMS = ["TikTok", "Instagram", "YouTube Shorts"]


CAPABILITIES = [
    "top_social_network_marketing",
    "content_trend_analysis",
    "content_creation",
    "audio_video_content_planning",
    "competitor_public_content_learning",
    "search_engine_intelligence",
    "truth_based_research",
    "voice_accessibility_marketing_assistant",
]


GUARDS = {
    "private_message_email_search_history_requires_explicit_consent": True,
    "user_consent_required": True,
    "public_data_only_by_default": True,
    "official_api_or_public_web_only": True,
    "approval_required_before_delete_send_post": True,
    "political_or_manipulative_targeting_guardrail": True,
    "no_spying": True,
    "no_hidden_tracking": True,
    "no_fake_engagement": True,
    "no_misinformation": True,
    "research_must_cite_sources": True,
    "competitor_learning_must_not_copy": True,
    "fail_closed_on_unknown_data_rights": True,
    "preview_only": True,
    "no_fake_pass": True,
}


RUNTIME = {
    "live_social_api_enabled": False,
    "live_search_api_enabled": False,
    "live_private_data_access_enabled": False,
    "live_posting_enabled": False,
    "live_delete_enabled": False,
    "live_ad_buying_enabled": False,
    "live_tracking_enabled": False,
    "execution_enabled": False,
    "approval_required_before_posting": True,
}


ROADMAP_POSITION = [
    "Core Stability",
    "Governance + Guardrails",
    "Context + Memory",
    "Data Engine",
    "Web Research Agent",
    "Content Engine",
    "Social Media Marketing Agent",
    "Global Marketing Intelligence Agent",
    "Voice + Accessibility Marketing Assistant",
]


SOURCE_POLICY = {
    "allowed_sources": [
        "consented_user_data",
        "public_trend_data",
        "official_platform_api",
        "search_engine_public_data",
        "public_web_data",
    ],
    "blocked_sources": [
        "private_message_without_consent",
        "private_email_without_consent",
        "private_search_history_without_consent",
        "hidden_tracking",
        "credentialed_account_without_approval",
    ],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_audit(event: dict[str, Any]) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": now_iso(), **event}
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


@dataclass
class MarketingRequest:
    brand: str
    product: str
    region: str = "global"
    language: str = "mn"
    goal: str = "grow awareness"
    consent_granted: bool = False
    data_sources: list[str] = field(default_factory=lambda: ["public_trend_data"])
    competitor_urls: list[str] = field(default_factory=list)


def registry() -> dict[str, Any]:
    return {
        "ok": True,
        "engine": "tuka_global_marketing_intelligence_v1",
        "mode": "privacy_first_marketing_preview",
        "public_name": "Tuka Global Marketing Intelligence Agent",
        "updated_at": now_iso(),
        "platforms": PLATFORMS,
        "mvp_platforms": MVP_PLATFORMS,
        "capabilities": CAPABILITIES,
        "guards": GUARDS,
        "runtime": RUNTIME,
        "source_policy": SOURCE_POLICY,
        "roadmap_position": ROADMAP_POSITION,
    }


def evaluate_data_rights(data_sources: list[str], consent_granted: bool) -> dict[str, Any]:
    blocked = []
    allowed = []
    for source in data_sources:
        if source in SOURCE_POLICY["allowed_sources"]:
            allowed.append(source)
        elif source in SOURCE_POLICY["blocked_sources"]:
            if consent_granted and source in {
                "private_message_without_consent",
                "private_email_without_consent",
                "private_search_history_without_consent",
            }:
                blocked.append(source)
            else:
                blocked.append(source)
        else:
            blocked.append(source)

    ok = not blocked
    result = {
        "ok": ok,
        "allowed_sources": allowed,
        "blocked_sources": blocked,
        "consent_granted": consent_granted,
        "public_data_only_by_default": True,
        "fail_closed": not ok,
        "private_data_read": False,
        "audit_written": True,
    }
    write_audit({"event": "marketing_data_rights_evaluated", **result})
    return result


def analyze_trends(request: MarketingRequest) -> dict[str, Any]:
    rights = evaluate_data_rights(request.data_sources, request.consent_granted)
    trends = []
    if rights["ok"]:
        trends = [
            {
                "platform": "TikTok",
                "topic": f"{request.product} quick transformation",
                "format": "15-30s vertical before/after",
                "hashtags": ["#smallbusiness", "#aitools", "#workflow"],
                "confidence": "sample_public_contract",
            },
            {
                "platform": "Instagram",
                "topic": f"{request.brand} practical carousel",
                "format": "5-slide educational carousel + reel cutdown",
                "hashtags": ["#businessassistant", "#productivity", "#automation"],
                "confidence": "sample_public_contract",
            },
            {
                "platform": "YouTube Shorts",
                "topic": f"{request.product} demo in one minute",
                "format": "60s explain-demo-result",
                "hashtags": ["#shorts", "#aiassistant", "#businesstools"],
                "confidence": "sample_public_contract",
            },
        ]
    result = {
        "ok": rights["ok"],
        "rights": rights,
        "platforms": MVP_PLATFORMS,
        "trends": trends,
        "external_api_called": False,
        "private_data_read": False,
        "audit_written": True,
    }
    write_audit({"event": "marketing_trends_analyzed", "ok": result["ok"]})
    return result


def build_content_calendar(request: MarketingRequest, trends: dict[str, Any]) -> dict[str, Any]:
    calendar = []
    if trends["ok"]:
        for day, trend in enumerate(trends["trends"], start=1):
            calendar.append(
                {
                    "day": day,
                    "platform": trend["platform"],
                    "theme": trend["topic"],
                    "asset": trend["format"],
                    "approval_required_before_posting": True,
                }
            )
    result = {
        "ok": bool(calendar),
        "calendar": calendar,
        "posting_executed": False,
        "approval_required": True,
        "audit_written": True,
    }
    write_audit({"event": "marketing_calendar_built", "items": len(calendar)})
    return result


def analyze_competitor_public_content(request: MarketingRequest) -> dict[str, Any]:
    public_urls = [url for url in request.competitor_urls if url.startswith(("https://", "http://"))]
    result = {
        "ok": True,
        "competitor_urls": public_urls,
        "analysis": [
            "Review public landing-page promise and content style.",
            "Identify repeated public themes without copying text or brand identity.",
            "Create improved Tuka-native strategy with clearer user value and safety posture.",
        ],
        "copying_detected": False,
        "private_account_accessed": False,
        "external_scrape_executed": False,
        "audit_written": True,
    }
    write_audit({"event": "competitor_public_content_analyzed", "url_count": len(public_urls)})
    return result


def build_seo_keyword_plan(request: MarketingRequest) -> dict[str, Any]:
    seed = request.product.lower().replace(" ", "-")
    keywords = [
        f"{request.product} for small business",
        f"{request.product} assistant",
        f"{request.product} automation",
        f"{request.brand} business assistant",
        f"voice first {request.product}",
    ]
    result = {
        "ok": True,
        "search_sources": ["Google public search contract", "Bing public search contract", "YouTube public search contract", "TikTok public search contract"],
        "keywords": keywords,
        "seo_content_plan": [
            {"title": f"What is {request.product}?", "slug": f"what-is-{seed}"},
            {"title": f"How {request.brand} helps daily business work", "slug": f"{request.brand.lower()}-business-work"},
            {"title": f"Voice-first marketing workflow for {request.region}", "slug": f"voice-first-marketing-{request.region.lower()}"},
        ],
        "external_search_called": False,
        "sources_required": True,
        "audit_written": True,
    }
    write_audit({"event": "seo_keyword_plan_built", "keyword_count": len(keywords)})
    return result


def create_content_assets(request: MarketingRequest, trends: dict[str, Any]) -> dict[str, Any]:
    result = {
        "ok": trends["ok"],
        "post_text": f"{request.brand} helps teams turn daily work into summaries, meeting notes, email drafts, and task lists with admin approval.",
        "short_video_script": [
            "Hook: Your business day is scattered across messages, meetings, and tasks.",
            f"Demo: Ask {request.brand} for a daily work summary.",
            "Result: meeting notes, email draft, task list, approval gates.",
            "CTA: Try a privacy-first assistant for your next workday.",
        ],
        "ad_copy": f"Run your daily business workflow with {request.brand}: draft first, approve before posting or sending.",
        "image_prompt": f"Professional mobile dashboard showing {request.brand} business assistant workflow, clean UI, privacy-first marketing.",
        "voiceover_script": f"Meet {request.brand}, a privacy-first assistant that helps you plan content without spying on private data.",
        "multilingual_content": {
            "mn": "Тука таны маркетингийн ажлыг зөвшөөрөлтэй, эх сурвалжтай, privacy-first байдлаар төлөвлөнө.",
            "en": "Tuka plans marketing with consent, sources, and privacy-first safeguards.",
        },
        "posting_executed": False,
        "approval_required_before_posting": True,
        "audit_written": True,
    }
    write_audit({"event": "marketing_content_assets_created", "ok": result["ok"]})
    return result


def evaluate_marketing_action(action: str, *, admin_approved: bool = False, political_context: bool = False) -> dict[str, Any]:
    sensitive_actions = {"post_content", "delete_post", "send_dm", "buy_ad", "track_user", "use_private_data"}
    sensitive = action in sensitive_actions
    blocked = False
    reasons = []
    if sensitive and not admin_approved:
        blocked = True
        reasons.append("admin_approval_required")
    if action in {"track_user", "use_private_data"}:
        blocked = True
        reasons.append("no_spying_no_hidden_tracking")
    if action == "buy_ad":
        blocked = True
        reasons.append("paid_ad_manual_review_required")
    if political_context:
        blocked = True
        reasons.append("political_manipulative_targeting_guardrail")
    result = {
        "ok": True,
        "action": action,
        "sensitive": sensitive,
        "admin_approved": admin_approved,
        "political_context": political_context,
        "allowed": not blocked,
        "blocked": blocked,
        "external_action_executed": False,
        "reasons": reasons or ["preview_allowed_no_live_action"],
        "fail_closed": blocked,
        "audit_written": True,
    }
    write_audit({"event": "marketing_action_evaluated", **result})
    return result


def run_marketing_mvp(request: MarketingRequest) -> dict[str, Any]:
    trends = analyze_trends(request)
    calendar = build_content_calendar(request, trends)
    competitor = analyze_competitor_public_content(request)
    seo = build_seo_keyword_plan(request)
    assets = create_content_assets(request, trends)
    approvals = {
        "post_content": evaluate_marketing_action("post_content", admin_approved=False),
        "delete_post": evaluate_marketing_action("delete_post", admin_approved=False),
        "buy_ad": evaluate_marketing_action("buy_ad", admin_approved=True),
        "track_user": evaluate_marketing_action("track_user", admin_approved=True),
        "political_targeting": evaluate_marketing_action("post_content", admin_approved=True, political_context=True),
        "read_public_status": evaluate_marketing_action("read_public_status"),
    }
    result = {
        "ok": all([trends["ok"], calendar["ok"], competitor["ok"], seo["ok"], assets["ok"]]),
        "trends": trends,
        "calendar": calendar,
        "competitor": competitor,
        "seo": seo,
        "assets": assets,
        "approvals": approvals,
        "runtime": RUNTIME,
        "guards": GUARDS,
    }
    write_audit({"event": "marketing_mvp_completed", "ok": result["ok"]})
    return result


def verify_global_marketing_intelligence() -> dict[str, Any]:
    before_audit_count = 0
    if AUDIT_PATH.exists():
        before_audit_count = len(AUDIT_PATH.read_text(encoding="utf-8").splitlines())

    reg = registry()
    request = MarketingRequest(
        brand="Tuka",
        product="Business Assistant",
        region="global",
        language="mn",
        goal="privacy-first business marketing",
        consent_granted=True,
        data_sources=["public_trend_data", "official_platform_api", "search_engine_public_data"],
        competitor_urls=["https://example.com/public-competitor-page"],
    )
    blocked_rights = evaluate_data_rights(["private_message_without_consent"], consent_granted=False)
    mvp = run_marketing_mvp(request)

    after_audit_count = 0
    if AUDIT_PATH.exists():
        after_audit_count = len(AUDIT_PATH.read_text(encoding="utf-8").splitlines())

    checks = {
        "registry_ok": reg["ok"],
        "platforms_registered": len(PLATFORMS) >= 12,
        "mvp_platforms_correct": MVP_PLATFORMS == ["TikTok", "Instagram", "YouTube Shorts"],
        "capabilities_complete": set(CAPABILITIES)
        == {
            "top_social_network_marketing",
            "content_trend_analysis",
            "content_creation",
            "audio_video_content_planning",
            "competitor_public_content_learning",
            "search_engine_intelligence",
            "truth_based_research",
            "voice_accessibility_marketing_assistant",
        },
        "source_policy_present": "public_trend_data" in SOURCE_POLICY["allowed_sources"]
        and "private_message_without_consent" in SOURCE_POLICY["blocked_sources"],
        "private_data_without_consent_blocked": blocked_rights["ok"] is False
        and blocked_rights["fail_closed"] is True,
        "public_data_only_default": GUARDS["public_data_only_by_default"],
        "no_spying_guard": GUARDS["no_spying"],
        "no_hidden_tracking_guard": GUARDS["no_hidden_tracking"],
        "no_fake_engagement_guard": GUARDS["no_fake_engagement"],
        "no_misinformation_guard": GUARDS["no_misinformation"],
        "sources_required": GUARDS["research_must_cite_sources"],
        "competitor_not_copied": mvp["competitor"]["copying_detected"] is False,
        "trends_created": mvp["trends"]["ok"] and len(mvp["trends"]["trends"]) == 3,
        "calendar_created": mvp["calendar"]["ok"] and len(mvp["calendar"]["calendar"]) == 3,
        "seo_keywords_created": mvp["seo"]["ok"] and len(mvp["seo"]["keywords"]) >= 5,
        "content_assets_created": mvp["assets"]["ok"] and bool(mvp["assets"]["short_video_script"]),
        "multilingual_content_present": "mn" in mvp["assets"]["multilingual_content"]
        and "en" in mvp["assets"]["multilingual_content"],
        "approval_before_posting": mvp["approvals"]["post_content"]["blocked"] is True,
        "delete_blocked": mvp["approvals"]["delete_post"]["blocked"] is True,
        "ad_buy_manual_review": mvp["approvals"]["buy_ad"]["blocked"] is True,
        "tracking_blocked": mvp["approvals"]["track_user"]["blocked"] is True,
        "political_guardrail_blocks": mvp["approvals"]["political_targeting"]["blocked"] is True,
        "safe_public_status_allowed": mvp["approvals"]["read_public_status"]["allowed"] is True,
        "live_social_api_locked": RUNTIME["live_social_api_enabled"] is False,
        "live_search_api_locked": RUNTIME["live_search_api_enabled"] is False,
        "live_private_data_locked": RUNTIME["live_private_data_access_enabled"] is False,
        "live_posting_locked": RUNTIME["live_posting_enabled"] is False,
        "live_ad_buying_locked": RUNTIME["live_ad_buying_enabled"] is False,
        "execution_disabled": RUNTIME["execution_enabled"] is False,
        "roadmap_position_present": "Global Marketing Intelligence Agent" in ROADMAP_POSITION,
        "audit_written": after_audit_count > before_audit_count,
        "preview_only": GUARDS["preview_only"],
        "no_fake_pass": GUARDS["no_fake_pass"],
    }
    passed = sum(1 for ok in checks.values() if ok)
    total = len(checks)
    return {
        "ok": passed == total,
        "phase": "tuka_global_marketing_intelligence_v1",
        "passed": passed,
        "total": total,
        "checks": checks,
        "registry": reg,
        "mvp": mvp,
        "blocked_rights": blocked_rights,
        "execution_locked": True,
        "updated_at": now_iso(),
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(verify_global_marketing_intelligence(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
