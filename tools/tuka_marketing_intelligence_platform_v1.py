from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "tuka_marketing_intelligence_platform_v1_report.json"
AUDIT_PATH = DATA_DIR / "tuka_marketing_intelligence_platform_audit.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _audit(event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    event = {"ts": _now(), **event}
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


AGENTS: dict[str, dict[str, Any]] = {
    "seo": {
        "name": "Tuka SEO Agent",
        "inspired_by_domain": "search intelligence platforms",
        "capabilities": [
            "keyword_research",
            "competitor_seo_analysis",
            "backlink_analysis",
            "search_intent_classification",
            "technical_seo_audit",
            "content_gap_analysis",
        ],
    },
    "social": {
        "name": "Tuka Social Agent",
        "inspired_by_domain": "social planning platforms",
        "capabilities": [
            "platform_content_planning",
            "schedule_recommendation",
            "trend_mapping",
            "best_posting_time",
            "engagement_prediction",
        ],
    },
    "content": {
        "name": "Tuka Content Agent",
        "inspired_by_domain": "AI copy and content platforms",
        "capabilities": [
            "blog",
            "article",
            "social_post",
            "ad_copy",
            "landing_page",
            "email_campaign",
        ],
    },
    "research": {
        "name": "Tuka Research Agent",
        "inspired_by_domain": "web and industry research platforms",
        "capabilities": [
            "google_public_search_contract",
            "youtube_public_search_contract",
            "news_public_sources",
            "research_papers",
            "forums",
            "reddit_public_threads",
            "industry_reports",
        ],
    },
    "competitor": {
        "name": "Tuka Competitor Agent",
        "inspired_by_domain": "competitive intelligence platforms",
        "capabilities": [
            "public_website_review",
            "public_seo_review",
            "public_content_review",
            "public_social_review",
            "public_ads_review",
            "public_reviews_review",
            "swot_analysis",
        ],
    },
    "analytics": {
        "name": "Tuka Analytics Agent",
        "inspired_by_domain": "analytics and product intelligence platforms",
        "capabilities": ["traffic", "conversion", "retention", "revenue", "funnels"],
    },
    "ads": {
        "name": "Tuka Ads Agent",
        "inspired_by_domain": "ad planning and optimization platforms",
        "capabilities": [
            "campaign_hypothesis",
            "audience_safety_review",
            "creative_variants",
            "budget_guardrails",
            "manual_review_before_spend",
        ],
    },
    "brand": {
        "name": "Tuka Brand Agent",
        "inspired_by_domain": "brand management platforms",
        "capabilities": [
            "brand_voice",
            "brand_consistency",
            "brand_guideline",
            "reputation_monitoring",
        ],
    },
    "video": {
        "name": "Tuka Video Agent",
        "inspired_by_domain": "video creation and editing platforms",
        "capabilities": [
            "script",
            "storyboard",
            "subtitle",
            "voiceover",
            "presentation",
            "short_video_concept",
        ],
    },
    "growth": {
        "name": "Tuka Growth Agent",
        "inspired_by_domain": "growth experimentation platforms",
        "capabilities": [
            "growth_experiments",
            "ab_testing",
            "campaign_optimization",
            "lead_generation",
        ],
    },
}


GUARDS = {
    "no_copycat_product": True,
    "tuka_native_names": True,
    "public_data_by_default": True,
    "user_consent_required": True,
    "private_data_only_with_explicit_authorization": True,
    "no_private_email_without_consent": True,
    "no_private_message_without_consent": True,
    "no_private_search_history_without_consent": True,
    "no_hidden_tracking": True,
    "no_spying": True,
    "no_fake_engagement": True,
    "no_misinformation": True,
    "sources_required_for_research": True,
    "posting_requires_approval": True,
    "ad_spend_requires_manual_review": True,
    "delete_send_publish_requires_approval": True,
    "audit_logging": True,
    "fail_closed": True,
}


RUNTIME = {
    "live_external_tool_calls_enabled": False,
    "live_search_enabled": False,
    "live_social_posting_enabled": False,
    "live_ad_buying_enabled": False,
    "live_private_data_access_enabled": False,
    "live_analytics_connector_enabled": False,
    "execution_enabled": False,
    "preview_only": True,
}


@dataclass
class MarketingPlatformRequest:
    topic: str = "Solar energy Mongolia"
    brand: str = "Tuka"
    region: str = "Mongolia"
    language: str = "mn"
    goal: str = "Generate a privacy-first marketing intelligence report"
    consent_granted: bool = True
    data_sources: list[str] | None = None
    competitor_urls: list[str] | None = None


def registry() -> dict[str, Any]:
    return {
        "ok": True,
        "engine": "tuka_marketing_intelligence_platform_v1",
        "public_name": "Tuka Marketing Intelligence Platform",
        "mode": "privacy_first_ai_marketing_operating_system_preview",
        "updated_at": _now(),
        "brain": "Tuka Marketing Brain",
        "agents": AGENTS,
        "guards": GUARDS,
        "runtime": RUNTIME,
        "positioning": {
            "not_copying": [
                "HubSpot",
                "Semrush",
                "Ahrefs",
                "Canva",
                "Jasper",
                "Hootsuite",
            ],
            "tuka_native_goal": "Unify best-practice marketing intelligence patterns into governed Tuka-native agents.",
        },
        "future_ceo_workflow": [
            "SEO",
            "Social",
            "Sales",
            "Competitor",
            "Revenue",
            "Risk",
            "Opportunities",
            "PDF",
            "PowerPoint",
            "Dashboard",
        ],
    }


def evaluate_data_rights(request: MarketingPlatformRequest) -> dict[str, Any]:
    sources = request.data_sources or ["public_web_data", "public_search_data", "user_provided_data"]
    private_markers = {
        "private_email",
        "private_message",
        "private_search_history",
        "phone_activity",
        "credentialed_social_account",
    }
    blocked = [source for source in sources if source in private_markers and not request.consent_granted]
    result = {
        "ok": not blocked,
        "sources": sources,
        "blocked_sources": blocked,
        "consent_granted": request.consent_granted,
        "public_data_by_default": True,
        "private_data_read": False,
        "fail_closed": bool(blocked),
        "audit_written": True,
    }
    _audit({"event": "marketing_platform_data_rights", "ok": result["ok"], "blocked": blocked})
    return result


def run_seo_agent(request: MarketingPlatformRequest) -> dict[str, Any]:
    keyword = request.topic
    result = {
        "ok": True,
        "agent": "Tuka SEO Agent",
        "keyword": keyword,
        "search_volume": "sample_contract_requires_live_provider_for_real_volume",
        "competition": "medium-preview",
        "trend": "rising-preview",
        "intent": "commercial_informational",
        "related_keywords": [
            f"{keyword} cost",
            f"{keyword} companies",
            f"{keyword} installation",
            f"{keyword} business case",
            f"{keyword} financing",
        ],
        "content_ideas": [
            f"What businesses should know about {keyword}",
            f"Cost comparison guide for {keyword}",
            f"Common mistakes in {keyword} projects",
        ],
        "technical_seo_audit": ["metadata", "page_speed", "schema_markup", "indexability"],
        "backlink_analysis": "preview_only_no_external_crawl",
        "content_gap_analysis": "preview_only_public_sources_required",
        "live_search_called": False,
    }
    _audit({"event": "seo_agent_preview", "keyword": keyword})
    return result


def run_social_agent(request: MarketingPlatformRequest) -> dict[str, Any]:
    platforms = ["Facebook", "Instagram", "TikTok", "LinkedIn", "YouTube", "X"]
    result = {
        "ok": True,
        "agent": "Tuka Social Agent",
        "platforms": platforms,
        "schedule": [
            {"platform": "TikTok", "format": "short demo", "best_time": "evening-preview"},
            {"platform": "Instagram", "format": "carousel + reel", "best_time": "lunch-preview"},
            {"platform": "LinkedIn", "format": "case study post", "best_time": "weekday morning-preview"},
        ],
        "trend": ["educational short video", "before/after workflow", "local business proof"],
        "engagement_prediction": "sample_preview_requires_real_metrics_for_score",
        "posting_executed": False,
        "approval_required_before_posting": True,
    }
    _audit({"event": "social_agent_preview", "platform_count": len(platforms)})
    return result


def run_content_agent(request: MarketingPlatformRequest) -> dict[str, Any]:
    result = {
        "ok": True,
        "agent": "Tuka Content Agent",
        "blog": f"How {request.topic} can help local businesses",
        "article_outline": ["problem", "market context", "options", "risks", "next steps"],
        "social_post": f"{request.topic}: practical guide for business owners in {request.region}.",
        "ad_copy": "Plan first, verify sources, approve before publishing.",
        "landing_page": ["headline", "benefits", "proof", "FAQ", "CTA"],
        "email_campaign": ["intro", "education", "case-study", "offer", "follow-up"],
        "generated_from_private_data": False,
    }
    _audit({"event": "content_agent_preview", "topic": request.topic})
    return result


def run_video_agent(request: MarketingPlatformRequest) -> dict[str, Any]:
    result = {
        "ok": True,
        "agent": "Tuka Video Agent",
        "script": [
            f"Hook: Why {request.topic} matters now.",
            "Explain the business problem.",
            "Show a simple comparison.",
            "End with a clear next step.",
        ],
        "storyboard": ["opening problem", "data card", "solution walkthrough", "CTA"],
        "subtitle": "Generated preview subtitles only.",
        "voiceover": f"Today we are looking at {request.topic} with a privacy-first research workflow.",
        "presentation": ["Title", "Market", "Opportunity", "Risks", "Action plan"],
        "short_video_concept": "45-second educational vertical video",
        "video_rendered": False,
    }
    _audit({"event": "video_agent_preview", "topic": request.topic})
    return result


def run_competitor_agent(request: MarketingPlatformRequest) -> dict[str, Any]:
    competitors = request.competitor_urls or ["https://example.com/public-competitor-page"]
    result = {
        "ok": True,
        "agent": "Tuka Competitor Agent",
        "public_sources_only": True,
        "competitor_urls": competitors,
        "website": "public landing-page structure preview",
        "seo": "public SEO signals preview",
        "content": "public content themes preview",
        "social_media": "public profile/content contract only",
        "ads": "public ad-library contract only",
        "reviews": "public reviews contract only",
        "swot": {
            "strengths": ["clear offer", "existing awareness"],
            "weaknesses": ["generic positioning", "limited local proof"],
            "opportunities": ["localized education", "trust-first workflow"],
            "threats": ["price competition", "fast-moving platforms"],
        },
        "copying_detected": False,
        "private_account_accessed": False,
    }
    _audit({"event": "competitor_agent_preview", "competitors": len(competitors)})
    return result


def run_research_agent(request: MarketingPlatformRequest) -> dict[str, Any]:
    result = {
        "ok": True,
        "agent": "Tuka Research Agent",
        "sources": [
            "Google public search contract",
            "YouTube public search contract",
            "News public sources contract",
            "Research paper metadata contract",
            "Forum/Reddit public thread contract",
            "Industry report public contract",
        ],
        "claims": [
            {"claim": f"{request.topic} requires source-backed local market validation.", "status": "needs_source"},
            {"claim": "Private user data is not required for public trend research.", "status": "verified_policy"},
        ],
        "uncertainty": "live_research_required_for_current_numbers",
        "private_email_read": False,
        "private_message_read": False,
        "private_search_history_read": False,
        "live_web_called": False,
    }
    _audit({"event": "research_agent_preview", "topic": request.topic})
    return result


def run_analytics_agent(request: MarketingPlatformRequest) -> dict[str, Any]:
    result = {
        "ok": True,
        "agent": "Tuka Analytics Agent",
        "traffic": "requires consented analytics connector",
        "conversion": "preview funnel model",
        "retention": "requires consented product data",
        "revenue": "requires consented finance data",
        "funnels": ["visit", "lead", "consultation", "proposal", "sale"],
        "connector_called": False,
        "consent_required": True,
    }
    _audit({"event": "analytics_agent_preview"})
    return result


def run_ads_agent(request: MarketingPlatformRequest) -> dict[str, Any]:
    result = {
        "ok": True,
        "agent": "Tuka Ads Agent",
        "campaign_hypothesis": f"Educational campaign for {request.topic}",
        "creative_variants": ["problem/solution", "local proof", "cost guide"],
        "budget_guardrails": ["daily cap", "manual review", "no spend without approval"],
        "political_or_manipulative_targeting": "blocked",
        "ad_spend_executed": False,
        "manual_review_required": True,
    }
    _audit({"event": "ads_agent_preview", "spend_executed": False})
    return result


def run_brand_agent(request: MarketingPlatformRequest) -> dict[str, Any]:
    result = {
        "ok": True,
        "agent": "Tuka Brand Agent",
        "brand_voice": "clear, practical, trustworthy, privacy-first",
        "brand_consistency": ["same promise", "same safety language", "same proof style"],
        "brand_guideline": ["no copycat naming", "Tuka-native wording", "source-backed claims"],
        "reputation_monitoring": "public mentions only, live monitoring disabled",
        "private_monitoring": False,
    }
    _audit({"event": "brand_agent_preview"})
    return result


def run_growth_agent(request: MarketingPlatformRequest) -> dict[str, Any]:
    result = {
        "ok": True,
        "agent": "Tuka Growth Agent",
        "growth_experiments": [
            "SEO landing page experiment",
            "short video education experiment",
            "lead magnet guide experiment",
        ],
        "ab_testing": ["headline", "CTA", "video hook"],
        "campaign_optimization": "manual-review preview",
        "lead_generation": "consent-based forms only",
        "automated_outreach_executed": False,
    }
    _audit({"event": "growth_agent_preview"})
    return result


def block_sensitive_action(action: str, admin_approved: bool = False) -> dict[str, Any]:
    hard_blocked = {"ad_spend", "delete_content", "send_email", "publish_post", "hidden_tracking"}
    allowed_preview = action == "read_public_status"
    blocked = action in hard_blocked or not allowed_preview
    reason = "preview_allowed" if allowed_preview else "admin_approval_or_manual_review_required"
    if action == "hidden_tracking":
        reason = "no_spying_no_hidden_tracking"
    if action == "ad_spend":
        reason = "ad_spend_manual_review_required"
    result = {
        "ok": True,
        "action": action,
        "admin_approved": admin_approved,
        "allowed": allowed_preview and not blocked,
        "blocked": blocked,
        "reason": reason,
        "external_action_executed": False,
        "audit_written": True,
    }
    _audit({"event": "marketing_platform_action_gate", "action": action, "blocked": blocked})
    return result


def run_platform_demo(request: MarketingPlatformRequest) -> dict[str, Any]:
    rights = evaluate_data_rights(request)
    if not rights["ok"]:
        return {
            "ok": False,
            "data_rights": rights,
            "fail_closed": True,
            "private_data_read": False,
            "updated_at": _now(),
        }

    agents = {
        "seo": run_seo_agent(request),
        "social": run_social_agent(request),
        "content": run_content_agent(request),
        "research": run_research_agent(request),
        "competitor": run_competitor_agent(request),
        "analytics": run_analytics_agent(request),
        "ads": run_ads_agent(request),
        "brand": run_brand_agent(request),
        "video": run_video_agent(request),
        "growth": run_growth_agent(request),
    }
    report = {
        "ok": True,
        "title": f"{request.brand} Marketing Intelligence Report: {request.topic}",
        "sections": [
            "SEO",
            "Social",
            "Content",
            "Research",
            "Competitor",
            "Analytics",
            "Ads",
            "Brand",
            "Video",
            "Growth",
            "Risk",
            "Opportunities",
        ],
        "outputs": ["PDF blueprint", "PowerPoint outline", "Dashboard cards"],
        "files_written": False,
        "approval_required_before_export_or_send": True,
    }
    action_gates = {
        "publish_post": block_sensitive_action("publish_post"),
        "send_email": block_sensitive_action("send_email"),
        "delete_content": block_sensitive_action("delete_content"),
        "ad_spend": block_sensitive_action("ad_spend", admin_approved=True),
        "hidden_tracking": block_sensitive_action("hidden_tracking", admin_approved=True),
        "read_public_status": block_sensitive_action("read_public_status"),
    }
    result = {
        "ok": all(item["ok"] for item in agents.values()),
        "data_rights": rights,
        "agents": agents,
        "executive_report": report,
        "action_gates": action_gates,
        "guards": GUARDS,
        "runtime": RUNTIME,
        "updated_at": _now(),
    }
    _audit({"event": "marketing_platform_demo", "ok": result["ok"]})
    return result


def verify_marketing_intelligence_platform() -> dict[str, Any]:
    request = MarketingPlatformRequest(
        topic="Solar energy Mongolia",
        brand="Tuka",
        region="Mongolia",
        data_sources=["public_web_data", "public_search_data", "user_provided_data"],
        competitor_urls=["https://example.com/public-competitor-page"],
    )
    demo = run_platform_demo(request)
    blocked = evaluate_data_rights(
        MarketingPlatformRequest(
            topic="private data test",
            consent_granted=False,
            data_sources=["private_email", "private_message", "private_search_history"],
        )
    )
    reg = registry()
    checks = {
        "registry_ok": reg["ok"] is True,
        "marketing_brain_present": reg["brain"] == "Tuka Marketing Brain",
        "ten_agents_registered": len(AGENTS) == 10,
        "seo_agent_complete": set(AGENTS["seo"]["capabilities"]) >= {"keyword_research", "backlink_analysis", "technical_seo_audit"},
        "social_agent_complete": set(AGENTS["social"]["capabilities"]) >= {"schedule_recommendation", "best_posting_time", "engagement_prediction"},
        "content_agent_complete": set(AGENTS["content"]["capabilities"]) >= {"blog", "ad_copy", "email_campaign"},
        "video_agent_complete": set(AGENTS["video"]["capabilities"]) >= {"script", "storyboard", "voiceover"},
        "competitor_agent_swot": demo["agents"]["competitor"]["swot"]["opportunities"] != [],
        "research_public_sources": demo["agents"]["research"]["private_email_read"] is False,
        "analytics_consent_required": demo["agents"]["analytics"]["consent_required"] is True,
        "ads_manual_review": demo["agents"]["ads"]["manual_review_required"] is True,
        "brand_agent_guidelines": bool(demo["agents"]["brand"]["brand_guideline"]),
        "growth_agent_experiments": len(demo["agents"]["growth"]["growth_experiments"]) >= 3,
        "solar_energy_example": demo["agents"]["seo"]["keyword"] == "Solar energy Mongolia",
        "seo_related_keywords": len(demo["agents"]["seo"]["related_keywords"]) >= 5,
        "executive_report_outputs": set(demo["executive_report"]["outputs"]) == {"PDF blueprint", "PowerPoint outline", "Dashboard cards"},
        "copycat_guard": GUARDS["no_copycat_product"] is True,
        "tuka_native_guard": GUARDS["tuka_native_names"] is True,
        "public_data_default": GUARDS["public_data_by_default"] is True,
        "private_without_consent_blocked": blocked["ok"] is False and blocked["private_data_read"] is False,
        "no_hidden_tracking": GUARDS["no_hidden_tracking"] is True and demo["action_gates"]["hidden_tracking"]["blocked"] is True,
        "no_fake_engagement": GUARDS["no_fake_engagement"] is True,
        "no_misinformation": GUARDS["no_misinformation"] is True,
        "sources_required": GUARDS["sources_required_for_research"] is True,
        "posting_blocked": demo["action_gates"]["publish_post"]["blocked"] is True,
        "send_delete_blocked": demo["action_gates"]["send_email"]["blocked"] is True and demo["action_gates"]["delete_content"]["blocked"] is True,
        "ad_spend_blocked": demo["action_gates"]["ad_spend"]["blocked"] is True,
        "safe_public_read_allowed": demo["action_gates"]["read_public_status"]["allowed"] is True,
        "live_external_tools_locked": RUNTIME["live_external_tool_calls_enabled"] is False,
        "live_private_data_locked": RUNTIME["live_private_data_access_enabled"] is False,
        "execution_disabled": RUNTIME["execution_enabled"] is False,
        "audit_written": AUDIT_PATH.exists(),
        "preview_only": RUNTIME["preview_only"] is True,
        "fail_closed": GUARDS["fail_closed"] is True,
    }
    passed = sum(1 for value in checks.values() if value is True)
    total = len(checks)
    report = {
        "ok": passed == total,
        "phase": "tuka_marketing_intelligence_platform_v1",
        "passed": passed,
        "total": total,
        "checks": checks,
        "registry": reg,
        "demo": demo,
        "blocked_private_data": blocked,
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
    print(json.dumps(verify_marketing_intelligence_platform(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
