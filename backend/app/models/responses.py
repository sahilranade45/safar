"""
Safar — API Response Models

Models for API request/response payloads and agent execution metadata.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
from app.models.travel import FinalPlan, TravelRequest


# ==============================================================================
# Agent Execution Metadata
# ==============================================================================

class AgentExecution(BaseModel):
    """Metadata about a single agent's execution."""
    agent_name: str
    status: str = "pending"  # pending, running, completed, failed
    duration_seconds: float = 0.0
    error: str = ""


# ==============================================================================
# API Responses
# ==============================================================================

class TravelPlanResponse(BaseModel):
    """Full API response for a travel plan request."""
    success: bool = True
    plan: Optional[FinalPlan] = None
    agent_executions: list[AgentExecution] = Field(default_factory=list)
    total_duration_seconds: float = 0.0
    error: str = ""


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    api_key_configured: bool = False
    model: str = ""


class ErrorResponse(BaseModel):
    """Structured error response."""
    success: bool = False
    error: str
    detail: str = ""


# ==============================================================================
# Replan Request
# ==============================================================================

class ReplanRequest(BaseModel):
    """Request to modify an existing travel plan."""
    original_request: TravelRequest
    modification: str = Field(
        ...,
        min_length=1,
        description="What the user wants to change"
    )
    existing_plan: Optional[FinalPlan] = None
