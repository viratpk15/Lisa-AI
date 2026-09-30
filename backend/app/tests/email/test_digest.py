"""
Jarvis AIOS — Email Intelligence Digest Tests
---------------------------------------------
Tests for email.digest:
- counts math correct across categories
- top N urgent sorted by priority desc
- upcoming deadlines sorted ascending
- 'today' excludes older than 24h
- 'week' excludes older than 7d
- cache hit returns same payload with cached=True
- cache expiry regenerates with fresh data
- user isolation (user A cannot see user B's emails/digest)
"""

import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from app.Data.database import SessionLocal
from app.Tools.email.models import (
    EmailAnalysisModel,
    EmailDigestCacheModel,
    EmailModel,
)
from app.Tools.engine import engine


def _seed_email_with_analysis(
    user_id: int,
    subject: str,
    received_hours_ago: float,
    category: str,
    priority_score: int,
    summary_text: str = "",
    deadline: str | None = None,
    tasks: list[str] | None = None,
) -> int:
    """Helper to seed an email and corresponding analysis record."""
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        rec_time = (now - timedelta(hours=received_hours_ago)).isoformat()
        now_iso = now.isoformat()

        email = EmailModel(
            user_id=user_id,
            gmail_message_id=f"msg_dig_{now.timestamp()}_{subject[:10]}",
            gmail_thread_id="th_dig_1",
            sender=f"sender_{category.lower()}@test.org",
            sender_domain="test.org",
            recipients="[\"user@test.org\"]",
            subject=subject,
            body_text=f"Body for {subject}",
            received_at=rec_time,
            attachment_metadata="[]",
            gmail_metadata="{}",
            created_at=rec_time,
            updated_at=rec_time,
        )
        db.add(email)
        db.commit()
        db.refresh(email)

        action_payload = json.dumps({
            "tasks": tasks or [],
            "links": ["https://example.com/action"],
            "sender_action_required": bool(tasks),
        })

        analysis = EmailAnalysisModel(
            email_id=email.id,
            category=category,
            subcategory="general",
            priority_score=priority_score,
            summary_text=summary_text or f"Summary for {subject}",
            action_items_json=action_payload,
            deadline=deadline,
            classified_at=now_iso,
            summarized_at=now_iso,
            extracted_at=now_iso,
            created_at=now_iso,
            updated_at=now_iso,
        )
        db.add(analysis)
        db.commit()
        return email.id
    finally:
        db.close()


def test_digest_counts_and_sorting_for_today():
    """Verify category counts, top urgent desc sort, and deadline asc sort for 'today'."""
    # Seed emails for Alice (901)
    _seed_email_with_analysis(
        user_id=901,
        subject="Critical Server Outage",
        received_hours_ago=2,
        category="URGENT",
        priority_score=95,
        summary_text="Database server memory exhaustion incident.",
        deadline="2026-10-02T15:00:00Z",
        tasks=["Restore DB backup"],
    )
    _seed_email_with_analysis(
        user_id=901,
        subject="Security Patch Notice",
        received_hours_ago=6,
        category="URGENT",
        priority_score=85,
        summary_text="Apply OpenSSL CVE patch immediately.",
        deadline="2026-09-30T10:00:00Z",
        tasks=["Update packages"],
    )
    _seed_email_with_analysis(
        user_id=901,
        subject="Monthly Cloud Billing",
        received_hours_ago=12,
        category="FINANCE",
        priority_score=60,
        summary_text="Cloud services invoice for September.",
        deadline="2026-10-15T00:00:00Z",
    )
    # Older than 24h (30h ago)
    _seed_email_with_analysis(
        user_id=901,
        subject="Campus Seminar",
        received_hours_ago=30,
        category="COLLEGE",
        priority_score=40,
    )

    res = engine.execute("email.digest", caller_context={"user_id": 901}, period="today")

    assert res["period"] == "today"
    assert res["cached"] is False
    counts = res["counts_by_category"]
    assert counts.get("URGENT") == 2
    assert counts.get("FINANCE") == 1
    # 30-hour old email must not be counted in 'today'
    assert "COLLEGE" not in counts

    # Top urgent sorted desc by priority: 95 then 85 then 60
    assert len(res["top_urgent"]) == 3
    assert res["top_urgent"][0]["priority_score"] == 95
    assert res["top_urgent"][0]["subject"] == "Critical Server Outage"
    assert res["top_urgent"][1]["priority_score"] == 85
    assert res["top_urgent"][2]["priority_score"] == 60

    # Upcoming deadlines sorted asc: "2026-09-30..." before "2026-10-02..." before "2026-10-15..."
    deadlines = [d["deadline"] for d in res["upcoming_deadlines"]]
    assert deadlines == [
        "2026-09-30T10:00:00Z",
        "2026-10-02T15:00:00Z",
        "2026-10-15T00:00:00Z",
    ]


def test_digest_period_week_cutoff():
    """Verify period='week' includes items up to 7 days old, but excludes items > 7 days."""
    _seed_email_with_analysis(
        user_id=901,
        subject="Three Days Old",
        received_hours_ago=72,  # 3 days
        category="INTERNSHIP",
        priority_score=75,
    )
    _seed_email_with_analysis(
        user_id=901,
        subject="Ten Days Old",
        received_hours_ago=240,  # 10 days
        category="TRAVEL",
        priority_score=50,
    )

    res = engine.execute("email.digest", caller_context={"user_id": 901}, period="week")

    counts = res["counts_by_category"]
    assert counts.get("INTERNSHIP") == 1
    # 10 days old email must be excluded
    assert "TRAVEL" not in counts


def test_digest_caching_and_expiry():
    """Verify cache hit returns cached payload and expired cache regenerates."""
    _seed_email_with_analysis(
        user_id=901,
        subject="Live Alert",
        received_hours_ago=1,
        category="URGENT",
        priority_score=90,
    )

    # 1. Initial generation
    res1 = engine.execute("email.digest", caller_context={"user_id": 901}, period="today")
    assert res1["cached"] is False

    # 2. Second immediate call should hit cache
    res2 = engine.execute("email.digest", caller_context={"user_id": 901}, period="today")
    assert res2["cached"] is True
    assert res2["counts_by_category"] == res1["counts_by_category"]

    # 3. Simulate cache expiry (TTL for 'today' is 15 minutes = 900s)
    db = SessionLocal()
    try:
        cache_row = db.execute(
            select(EmailDigestCacheModel).where(
                EmailDigestCacheModel.user_id == 901,
                EmailDigestCacheModel.period == "today",
            )
        ).scalar_one()
        # Set generated_at to 20 minutes ago
        cache_row.generated_at = (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
        db.commit()
    finally:
        db.close()

    # 4. Third call after expiry must regenerate
    res3 = engine.execute("email.digest", caller_context={"user_id": 901}, period="today")
    assert res3["cached"] is False


def test_digest_user_isolation():
    """Verify Alice (901) cannot see Bob's (902) emails in her digest."""
    # Alice email
    _seed_email_with_analysis(
        user_id=901,
        subject="Alice Only Note",
        received_hours_ago=1,
        category="PERSONAL",
        priority_score=50,
    )
    # Bob email
    _seed_email_with_analysis(
        user_id=902,
        subject="Bob Confidential Deal",
        received_hours_ago=1,
        category="FINANCE",
        priority_score=99,
    )

    res_alice = engine.execute("email.digest", caller_context={"user_id": 901}, period="today")
    res_bob = engine.execute("email.digest", caller_context={"user_id": 902}, period="today")

    assert "PERSONAL" in res_alice["counts_by_category"]
    assert "FINANCE" not in res_alice["counts_by_category"]
    assert all("Bob" not in u["subject"] for u in res_alice["top_urgent"])

    assert "FINANCE" in res_bob["counts_by_category"]
    assert "PERSONAL" not in res_bob["counts_by_category"]
    assert all("Alice" not in u["subject"] for u in res_bob["top_urgent"])
