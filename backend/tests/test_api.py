"""
Safar — API Endpoint Tests

Tests for FastAPI endpoints.
Uses mocked LLM — no API key required.
"""

import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test GET /api/health returns 200 with expected fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "api_key_configured" in data
    assert "model" in data


@pytest.mark.asyncio
async def test_plan_without_api_key():
    """Test POST /api/plan returns 503 when API key is not configured."""
    with patch("app.main.settings") as mock_settings:
        mock_settings.is_api_key_configured = False

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/plan", json={
                "destination": "Goa",
                "days": 3,
                "travelers": 2,
                "budget": 25000,
            })

        assert response.status_code == 503


@pytest.mark.asyncio
async def test_plan_invalid_input():
    """Test POST /api/plan rejects invalid input."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Missing required fields
        response = await client.post("/api/plan", json={})
        assert response.status_code == 422

        # Invalid days
        response = await client.post("/api/plan", json={
            "destination": "Goa",
            "days": 0,
            "travelers": 2,
            "budget": 25000,
        })
        assert response.status_code == 422

        # Invalid budget
        response = await client.post("/api/plan", json={
            "destination": "Goa",
            "days": 3,
            "travelers": 2,
            "budget": -100,
        })
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_replan_without_api_key():
    """Test POST /api/replan returns 503 when API key is not configured."""
    with patch("app.main.settings") as mock_settings:
        mock_settings.is_api_key_configured = False

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/replan", json={
                "original_request": {
                    "destination": "Goa",
                    "days": 3,
                    "travelers": 2,
                    "budget": 25000,
                },
                "modification": "Reduce budget",
            })

        assert response.status_code == 503
