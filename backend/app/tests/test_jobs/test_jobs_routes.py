"""
Tests for Jobs & Internship Finder FastAPI Endpoints
Strict Zero-Fabrication Architecture:
No synthetic or seeded jobs are used. All behaviors for real provider responses,
unavailable states, zero results, rate limits, and missing credentials are verified.
"""

import io
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import httpx
from app.main import app
from app.Auth.security import create_access_token
from app.Jobs.providers.aggregator_provider import job_provider

client = TestClient(app)
token = create_access_token(user_id=1, email="test@example.com")
headers = {"Authorization": f"Bearer {token}"}
ORIG_HTTPX_GET = httpx.Client.get


def test_profile_endpoints():
    """Verify profile retrieval and storage."""
    # 1. Get empty/initial profile
    resp = client.get("/jobs/profile", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "name" in data

    # 2. Save candidate profile
    payload = {
        "name": "Virat Sharma",
        "email": "test@example.com",
        "education": [
            {
                "college": "BMS College of Engineering",
                "degree": "B.Tech",
                "branch": "Computer Science",
                "graduation_year": 2025,
                "cgpa": 9.1,
            }
        ],
        "all_normalized_skills": ["Python", "FastAPI", "React", "Docker"],
        "preferred_roles": ["AI Engineer", "Software Developer"],
        "preferred_locations": ["Bangalore"],
        "remote_preference": "any",
    }
    save_resp = client.post("/jobs/profile", headers=headers, json=payload)
    assert save_resp.status_code == 200
    saved_data = save_resp.json()
    assert saved_data["name"] == "Virat Sharma"
    assert "Python" in saved_data["all_normalized_skills"]


def test_resume_extract_endpoint():
    """Verify resume extraction enforces user confirmation requirement."""
    resume_content = b"""
John Doe
Email: john@test.com
B.Tech in Information Technology, 2025
Skills: Python, TypeScript, React, PostgreSQL, Docker
Projects: Building Lisa AI Operating System with LangGraph
"""
    files = {"file": ("resume.txt", io.BytesIO(resume_content), "text/plain")}
    resp = client.post("/jobs/profile/extract-resume", headers=headers, files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "Python" in data["all_normalized_skills"]
    assert "React" in data["all_normalized_skills"]
    assert data["extracted_from_resume"] is True
    assert data["is_confirmed_by_user"] is False


# ── Strict Real-Data Provider Behavior Tests (A, B, C, D, E) ──────────────────

def test_case_a_real_provider_available():
    """Case A: Real provider available -> real results returned with transparent matches."""
    mock_remoteok_payload = [
        {"legal": "RemoteOK API"},
        {
            "id": "1138001",
            "position": "Senior AI & Python Engineer",
            "company": "Anthropic AI",
            "location": "Worldwide Remote",
            "tags": ["python", "fastapi", "machine-learning", "docker"],
            "description": "<p>Build production LLM reasoning engines with Python and FastAPI.</p>",
            "url": "https://remoteok.com/remote-jobs/1138001",
            "salary_min": 140000,
            "salary_max": 180000,
            "date": "2026-09-29T10:00:00Z",
        },
    ]

    def mock_get(self, url, *args, **kwargs):
        url_str = str(url)
        if "remoteok.com" in url_str:
            mock = MagicMock()
            mock.status_code = 200
            mock.json.return_value = mock_remoteok_payload
            return mock
        if "arbeitnow.com" in url_str:
            mock = MagicMock()
            mock.status_code = 200
            mock.json.return_value = {"data": []}
            return mock
        if any(d in url_str for d in ["adzuna.com", "rapidapi.com", "jooble.org"]):
            mock = MagicMock()
            mock.status_code = 200
            mock.json.return_value = {"results": [], "data": [], "jobs": []}
            return mock
        return ORIG_HTTPX_GET(self, url, *args, **kwargs)

    with patch.object(httpx.Client, "get", mock_get), \
         patch("app.Config.settings.ADZUNA_APP_ID", None), \
         patch("app.Config.settings.ADZUNA_APP_KEY", None), \
         patch("app.Config.settings.RAPIDAPI_KEY", None), \
         patch("app.Config.settings.JSEARCH_API_KEY", None), \
         patch("app.Config.settings.JOOBLE_API_KEY", None):
        job_provider._cache.clear()
        search_payload = {"role": "Python", "limit": 5}
        resp = client.post("/jobs/search", headers=headers, json=search_payload)
        assert resp.status_code == 200
        data = resp.json()
        search_resp = data["search_response"]

        assert search_resp["has_live_results"] is True
        assert search_resp["total_results"] >= 1
        job = search_resp["jobs"][0]
        assert job["company"] == "Anthropic AI"
        assert job["apply_url"] == "https://remoteok.com/remote-jobs/1138001"
        assert "Found" in search_resp["status_message"]
        # Verify deterministic match score computed
        assert job["id"] in data["matches"]
        assert data["matches"][job["id"]]["match_score"] > 0


def test_case_b_provider_unavailable():
    """Case B: Provider unavailable -> honest unavailable state (never substitute fake jobs)."""
    def mock_get(self, url, *args, **kwargs):
        url_str = str(url)
        if any(d in url_str for d in ["remoteok.com", "arbeitnow.com", "adzuna.com", "rapidapi.com", "jooble.org"]):
            raise httpx.ConnectError("Network connection refused")
        return ORIG_HTTPX_GET(self, url, *args, **kwargs)

    with patch.object(httpx.Client, "get", mock_get), \
         patch("app.Config.settings.ADZUNA_APP_ID", None), \
         patch("app.Config.settings.ADZUNA_APP_KEY", None), \
         patch("app.Config.settings.RAPIDAPI_KEY", None), \
         patch("app.Config.settings.JSEARCH_API_KEY", None), \
         patch("app.Config.settings.JOOBLE_API_KEY", None):
        job_provider._cache.clear()
        search_payload = {"role": "AI Engineer", "limit": 5}
        resp = client.post("/jobs/search", headers=headers, json=search_payload)
        assert resp.status_code == 200
        data = resp.json()
        search_resp = data["search_response"]

        assert search_resp["has_live_results"] is False
        assert search_resp["total_results"] == 0
        assert search_resp["jobs"] == []
        assert search_resp["status_message"] == "No live job results are currently available."


def test_case_c_provider_returns_zero_results():
    """Case C: Provider returns zero results -> honest empty state."""
    def mock_get(self, url, *args, **kwargs):
        url_str = str(url)
        if "remoteok.com" in url_str:
            mock = MagicMock()
            mock.status_code = 200
            mock.json.return_value = [{"disclaimer": "header"}]
            return mock
        if "arbeitnow.com" in url_str:
            mock = MagicMock()
            mock.status_code = 200
            mock.json.return_value = {"data": []}
            return mock
        if any(d in url_str for d in ["adzuna.com", "rapidapi.com", "jooble.org"]):
            mock = MagicMock()
            mock.status_code = 200
            mock.json.return_value = {"results": [], "data": [], "jobs": []}
            return mock
        return ORIG_HTTPX_GET(self, url, *args, **kwargs)

    with patch.object(httpx.Client, "get", mock_get), \
         patch("app.Config.settings.ADZUNA_APP_ID", None), \
         patch("app.Config.settings.ADZUNA_APP_KEY", None), \
         patch("app.Config.settings.RAPIDAPI_KEY", None), \
         patch("app.Config.settings.JSEARCH_API_KEY", None), \
         patch("app.Config.settings.JOOBLE_API_KEY", None):
        job_provider._cache.clear()
        search_payload = {"role": "NonExistentSpecialty12345", "limit": 5}
        resp = client.post("/jobs/search", headers=headers, json=search_payload)
        assert resp.status_code == 200
        data = resp.json()
        search_resp = data["search_response"]

        assert search_resp["has_live_results"] is False
        assert search_resp["total_results"] == 0
        assert search_resp["jobs"] == []
        assert search_resp["status_message"] == "No matching opportunities were found."


def test_case_d_provider_rate_limited():
    """Case D: Provider rate-limited -> honest provider error / retry state."""
    def mock_get(self, url, *args, **kwargs):
        url_str = str(url)
        if any(d in url_str for d in ["remoteok.com", "arbeitnow.com", "adzuna.com", "rapidapi.com", "jooble.org"]):
            mock = MagicMock()
            mock.status_code = 429
            return mock
        return ORIG_HTTPX_GET(self, url, *args, **kwargs)

    with patch.object(httpx.Client, "get", mock_get), \
         patch("app.Config.settings.ADZUNA_APP_ID", None), \
         patch("app.Config.settings.ADZUNA_APP_KEY", None), \
         patch("app.Config.settings.RAPIDAPI_KEY", None), \
         patch("app.Config.settings.JSEARCH_API_KEY", None), \
         patch("app.Config.settings.JOOBLE_API_KEY", None):
        job_provider._cache.clear()
        search_payload = {"role": "Python", "limit": 5}
        resp = client.post("/jobs/search", headers=headers, json=search_payload)
        assert resp.status_code == 200
        data = resp.json()
        search_resp = data["search_response"]

        assert search_resp["has_live_results"] is False
        assert search_resp["total_results"] == 0
        assert search_resp["jobs"] == []
        assert "rate limit reached" in search_resp["status_message"].lower()


def test_case_e_no_provider_credentials():
    """Case E: No provider credentials -> configuration-required state."""
    job_provider._cache.clear()
    job_provider._last_statuses = {"Adzuna": "not_configured"}
    summary = job_provider.get_status_summary(total_jobs=0)
    assert summary == "Live job search is not configured."


# ── Full E2E Flow From Real Provider Data ─────────────────────────────────────

def test_e2e_search_gap_and_track_flow():
    """
    E2E Test without synthetic or seeded jobs:
    Provider response -> Search -> Details -> Skill Gap -> Tracker -> Update -> Delete
    """
    mock_payload = [
        {"disclaimer": "RemoteOK"},
        {
            "id": "e2e_test_job_1",
            "position": "Backend AI Developer",
            "company": "DeepTech Systems",
            "location": "Worldwide Remote",
            "tags": ["python", "fastapi", "react", "postgresql"],
            "description": "Develop full-stack AI applications with FastAPI and PostgreSQL.",
            "url": "https://deeptech.example.com/apply/1",
            "salary_min": 100000,
            "salary_max": 120000,
        },
    ]

    def mock_get(self, url, *args, **kwargs):
        url_str = str(url)
        if "remoteok.com" in url_str:
            mock = MagicMock()
            mock.status_code = 200
            mock.json.return_value = mock_payload
            return mock
        if "arbeitnow.com" in url_str:
            mock = MagicMock()
            mock.status_code = 200
            mock.json.return_value = {"data": []}
            return mock
        if any(d in url_str for d in ["adzuna.com", "rapidapi.com", "jooble.org"]):
            mock = MagicMock()
            mock.status_code = 200
            mock.json.return_value = {"results": [], "data": [], "jobs": []}
            return mock
        return ORIG_HTTPX_GET(self, url, *args, **kwargs)

    with patch.object(httpx.Client, "get", mock_get), \
         patch("app.Config.settings.ADZUNA_APP_ID", None), \
         patch("app.Config.settings.ADZUNA_APP_KEY", None), \
         patch("app.Config.settings.RAPIDAPI_KEY", None), \
         patch("app.Config.settings.JSEARCH_API_KEY", None), \
         patch("app.Config.settings.JOOBLE_API_KEY", None):
        job_provider._cache.clear()

        # 1. Search opportunities
        search_resp = client.post("/jobs/search", headers=headers, json={"role": "Backend", "limit": 5})
        assert search_resp.status_code == 200
        jobs = search_resp.json()["search_response"]["jobs"]
        assert len(jobs) >= 1
        target_job = jobs[0]
        job_id = target_job["id"]
        assert target_job["company"] == "DeepTech Systems"

        # 2. Get details
        detail_resp = client.get(f"/jobs/{job_id}", headers=headers)
        assert detail_resp.status_code == 200
        assert detail_resp.json()["id"] == job_id
        assert detail_resp.json()["company"] == "DeepTech Systems"

        # 3. Analyze skill gap
        gap_resp = client.get(f"/jobs/{job_id}/skill-gap", headers=headers)
        assert gap_resp.status_code == 200
        gap_data = gap_resp.json()
        assert gap_data["job_id"] == job_id
        assert "Python" in gap_data["matched_skills"]
        assert "recommended_preparation" in gap_data

        # 4. Deep resume-job evaluation
        analysis_resp = client.post("/jobs/analyze-resume-job", headers=headers, json={"job_id": job_id})
        assert analysis_resp.status_code == 200
        analysis_data = analysis_resp.json()
        assert analysis_data["job_id"] == job_id
        assert len(analysis_data["strengths"]) > 0
        assert "transparent_assessment" in analysis_data

        # 5. Track in application tracker
        track_resp = client.post("/jobs/applications", headers=headers, json={"job_id": job_id, "status": "saved"})
        assert track_resp.status_code == 200
        assert track_resp.json()["status"] == "saved"

        # 6. Verify in list
        list_resp = client.get("/jobs/applications/all", headers=headers)
        assert list_resp.status_code == 200
        items = list_resp.json()
        assert any(i["job_id"] == job_id for i in items)

        # 7. Update status to interview
        update_resp = client.patch(
            f"/jobs/applications/{job_id}/status",
            headers=headers,
            json={"status": "interview", "notes": "Interview on Friday"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "interview"

        # 8. Untrack
        del_resp = client.delete(f"/jobs/applications/{job_id}", headers=headers)
        assert del_resp.status_code == 200
        assert del_resp.json()["deleted"] is True
